import os
import json
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
from psycopg2.extras import RealDictCursor

# استيراد الملفات المحدثة (بدون النماذج المحلية)
from config import *
from customer_memory import CustomerMemoryManager
from conversation_manager import ConversationManager
from quick_response import QuickResponseSystem
from ai_retriever import EnhancedRetriever
from smart_response import SmartResponseGenerator
from whatsapp_handler import WhatsAppHandler
from admin_template import ADMIN_TEMPLATE
from customers_templete import CUSTOMERS_TEMPLATE
from perf_templete import PERFORMANCE_TEMPLATE 
from statusTemplete import STATUS_TEMPLATE
from home_templete import HOME_TEMPLETE
from cleanup_manager import start_cleanup_thread
from admin_routes import setup_admin_routes

# إنشاء التطبيق
app = Flask(__name__)

# --- تهيئة النظام الذكي مع الذاكرة ---
print("🔄 تحميل النظام المحسن (بدون نماذج محلية)...")

customer_memory = CustomerMemoryManager()
conversation_manager = ConversationManager(customer_memory)
quick_system = QuickResponseSystem()
whatsapp_handler = WhatsAppHandler(quick_system)

# تحميل مكونات الذكاء الاصطناعي المحدثة
openai_client = None
enhanced_retriever = None
response_generator = None

# تحميل OpenAI Client
if OPENAI_API_KEY:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        print("✅ OpenAI Client جاهز")
    except Exception as e:
        print(f"❌ خطأ في تحميل OpenAI: {e}")

# تحميل النظام الذكي الجديد (بدون نماذج محلية - RAM صفر!)
try:
    print("📊 تهيئة نظام البحث الذكي الجديد...")
    
    # النظام الجديد يستخدم OpenAI embeddings + PostgreSQL فقط
    enhanced_retriever = EnhancedRetriever(customer_memory)
    response_generator = SmartResponseGenerator(openai_client, enhanced_retriever, quick_system, customer_memory)
    
    print("✅ النظام المحدث جاهز! (توفير 70-80% من الـ RAM)")
    
    # عرض إحصائيات النظام الجديد
    retriever_stats = enhanced_retriever.get_retriever_stats()
    print(f"📈 إحصائيات النظام المحسن:")
    print(f"   • الأسئلة الشائعة المحلية: {retriever_stats['frequent_qa_count']}")
    print(f"   • OpenAI Embeddings: {'متاح' if retriever_stats['embeddings_enabled'] else 'غير متاح'}")
    
    if 'total_cached' in retriever_stats:
        print(f"   • عدد embeddings في cache: {retriever_stats['total_cached']}")
        print(f"   • حجم cache: {retriever_stats['total_size_mb']:.2f} MB")

except Exception as e:
    print(f"⚠️ تحذير في تحميل النظام المحدث: {e}")
    print("💡 سيعمل بالردود السريعة والذاكرة فقط")
    enhanced_retriever = None
    response_generator = SmartResponseGenerator(openai_client, None, quick_system, customer_memory)

# --- المسارات الرئيسية ---
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return challenge, 200
        return 'فشل التحقق', 403
    
    if request.method == 'POST':
        data = request.get_json()
        
        if not data or 'entry' not in data:
            return 'OK', 200
        
        # معالجة سريعة للرسائل
        for entry in data['entry']:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                
                if 'messages' not in value:
                    continue
                
                for message_data in value['messages']:
                    message_type = message_data.get('type', '')
                    message_id = message_data.get('id', '')
                    phone_number = message_data.get('from', '')
                    
                    if not phone_number:
                        continue
                    
                    # فحص الرسائل المكررة
                    if whatsapp_handler.is_duplicate_message(message_id):
                        print(f"⚠️ رسالة مكررة: {message_id}")
                        continue
                    
                    # فحص معدل الرسائل
                    if whatsapp_handler.check_rate_limit(phone_number):
                        print(f"⚠️ سرعة عالية من: {phone_number}")
                        continue
                    
                    # === معالجة الرسائل التفاعلية (جديد) ===
                    if message_type == 'interactive':
                        interactive_data = message_data.get('interactive', {})
                        
                        # معالجة الرد التفاعلي في thread منفصل
                        thread = threading.Thread(
                            target=handle_interactive_message_thread,
                            args=(phone_number, interactive_data),
                            daemon=True
                        )
                        thread.start()
                        continue
                    
                    # === معالجة الرسائل النصية العادية ===
                    if message_type == 'text':
                        user_message = message_data.get('text', {}).get('body', '').strip()
                        
                        if not user_message:
                            continue
                        
                        # معالجة فورية في thread منفصل
                        thread = threading.Thread(
                            target=process_user_message_with_memory,
                            args=(phone_number, user_message),
                            daemon=True
                        )
                        thread.start()
        
        return 'OK', 200

def handle_interactive_message_thread(phone_number: str, interactive_data: dict):
    """معالجة الرسائل التفاعلية في thread منفصل"""
    try:
        print(f"🔘 رد تفاعلي من {phone_number}: {interactive_data.get('type', '')}")
        
        # تحديث نشاط المحادثة
        conversation_manager.update_activity(phone_number)
        
        # معالجة الرد التفاعلي
        success = whatsapp_handler.handle_interactive_message(interactive_data, phone_number)
        
        if success:
            print(f"✅ تم معالجة الرد التفاعلي بنجاح: {phone_number}")
        else:
            print(f"❌ فشل في معالجة الرد التفاعلي: {phone_number}")
            
    except Exception as e:
        print(f"❌ خطأ في معالجة الرد التفاعلي: {e}")
        whatsapp_handler.send_message(phone_number, "عذراً، حدث خطأ تقني. 📞 0556914447")

def process_user_message_with_memory(phone_number: str, user_message: str):
    """معالجة سريعة للرسائل مع القوائم التفاعلية والذاكرة الشخصية"""
    start_time = time.time()
    
    try:
        # إدارة المحادثة مع الذاكرة
        is_first = conversation_manager.is_first_message(phone_number)
        
        if is_first:
            conversation_manager.register_conversation(phone_number)
            print(f"🆕 محادثة جديدة: {phone_number}")
        else:
            conversation_manager.update_activity(phone_number)
        
        # جلب معلومات العميل من الذاكرة
        customer_info = customer_memory.get_customer_info(phone_number)
        customer_name = customer_info.get('name', '') if customer_info else None
        
        if customer_info:
            print(f"👤 عميل مسجل: {customer_name or 'غير معروف'}")
        
        # === فحص طلب القائمة الرئيسية (جديد) ===
        if whatsapp_handler.should_show_main_menu(user_message):
            print(f"📋 طلب قائمة رئيسية من: {phone_number}")
            whatsapp_handler.interactive_menu.send_main_menu(phone_number)
            return
        
        # === للعملاء الجدد، إرسال قائمة ترحيبية (جديد) ===
        if is_first:
            print(f"🌟 إرسال قائمة ترحيبية للعميل الجديد: {phone_number}")
            whatsapp_handler.send_welcome_menu_to_new_customer(phone_number, customer_name)
            return
        
        # === توليد الرد الذكي مع الذاكرة (النظام المحدث) ===
        if response_generator:
            bot_response, should_send_image, image_url = response_generator.generate_response(
                user_message, phone_number, is_first
            )
            
            # إرسال الرد
            if should_send_image and image_url:
                success = whatsapp_handler.send_image_with_text(phone_number, bot_response, image_url)
            else:
                success = whatsapp_handler.send_message(phone_number, bot_response)
        else:
            # نظام احتياطي أساسي مع الذاكرة
            if quick_system.is_greeting_message(user_message):
                bot_response = quick_system.get_welcome_response(customer_name)
                success = whatsapp_handler.send_message(phone_number, bot_response)
            elif quick_system.is_thanks_message(user_message):
                bot_response = quick_system.get_thanks_response(customer_name)
                success = whatsapp_handler.send_message(phone_number, bot_response)
            elif quick_system.is_price_inquiry(user_message):
                bot_response, image_url = quick_system.get_price_response()
                success = whatsapp_handler.send_image_with_text(phone_number, bot_response, image_url)
            else:
                if customer_name:
                    bot_response = f"""أهلاً وسهلاً أخونا {customer_name} الكريم مرة ثانية في مكتب الركائز البشرية! 🌟

سيتواصل معك متخصص قريباً.

💡 يمكنك كتابة "مساعدة" لعرض قائمة الخدمات التفاعلية

📞 0556914447"""
                else:
                    bot_response = """أهلاً بك في مكتب الركائز البشرية! 🌟

سيتواصل معك أحد موظفينا قريباً.

💡 اكتب "مساعدة" لعرض قائمة خدماتنا التفاعلية

📞 0556914447"""
                success = whatsapp_handler.send_message(phone_number, bot_response)
            
            # إضافة للذاكرة حتى في النظام الاحتياطي
            customer_memory.add_conversation_message(phone_number, user_message, bot_response)
        
        # إحصائيات سريعة
        response_time = time.time() - start_time
        customer_status = "عميل مسجل" if customer_info else "عميل جديد"
        print(f"✅ استجابة في {response_time:.2f}s لـ {phone_number} ({customer_status})")
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        whatsapp_handler.send_message(phone_number, "عذراً، حدث خطأ تقني. 📞 0556914447")

# === المسارات الإدارية ===

@app.route('/')
def home():
    """الصفحة الرئيسية مع أزرار التنقل"""
    return render_template_string(HOME_TEMPLETE)

@app.route('/status')
def status():
    """صفحة حالة سريعة مع إحصائيات الذاكرة والقوائم التفاعلية"""
    active_conversations = len(conversation_manager.conversations)
    cached_customers = len(customer_memory.customer_cache)
    handler_stats = whatsapp_handler.get_handler_stats()
    
    # جلب إجمالي العملاء من قاعدة البيانات
    total_customers = 0
    try:
        if customer_memory.db_pool:
            conn = customer_memory.db_pool.getconn()
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM customers")
                total_customers = cur.fetchone()[0]
            customer_memory.db_pool.putconn(conn)
    except Exception as e:
        print(f"خطأ في جلب عدد العملاء: {e}")
    
    # إحصائيات النظام الجديد
    system_info = {
        'total_customers': total_customers,
        'cached_customers': cached_customers,
        'active_conversations': active_conversations,
        'openai_client': openai_client is not None,
        'enhanced_retriever': enhanced_retriever is not None,
        'customer_memory': customer_memory,
        'handler_stats': handler_stats
    }
    
    return render_template_string(STATUS_TEMPLATE, **system_info)

@app.route('/performance-analytics')
def performance_analytics():
    """صفحة تحليل الأداء والتقارير الإدارية"""
    return render_template_string(PERFORMANCE_TEMPLATE)

@app.route('/customers-stats')
def customers_stats():
    """صفحة إحصائيات العملاء مع واجهة منسقة"""
    return render_template_string(CUSTOMERS_TEMPLATE)

@app.route('/api/customers-stats')
def api_customers_stats():
    """API endpoint لجلب إحصائيات العملاء بصيغة JSON"""
    
    stats = {
        "total_customers": 0,
        "active_customers_in_memory": len(customer_memory.customer_cache) if hasattr(customer_memory, 'customer_cache') else 0,
        "active_conversations": len(conversation_manager.conversations) if hasattr(conversation_manager, 'conversations') else 0,
        "registered_customers": [],
        "system_info": {
            "database_connected": customer_memory.db_pool is not None if hasattr(customer_memory, 'db_pool') else False,
            "query_time": datetime.now().isoformat(),
            "status": "initializing"
        }
    }
    
    # Add handler stats safely
    try:
        if hasattr(whatsapp_handler, 'get_handler_stats'):
            handler_stats = whatsapp_handler.get_handler_stats()
            stats["interaction_stats"] = handler_stats
        else:
            stats["interaction_stats"] = {"error": "Handler stats not available"}
    except Exception as e:
        print(f"Error getting handler stats: {e}")
        stats["interaction_stats"] = {"error": str(e)}
    
    # Database operations
    try:
        if hasattr(customer_memory, 'db_pool') and customer_memory.db_pool:
            conn = None
            try:
                conn = customer_memory.db_pool.getconn()
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Get total customers count
                    cur.execute("SELECT COUNT(*) as total FROM customers")
                    count_result = cur.fetchone()
                    if count_result:
                        stats["total_customers"] = int(count_result['total'])
                    
                    # Get customer details
                    cur.execute("""
                        SELECT c.phone_number, c.name, c.gender, c.preferred_nationality,
                               c.created_at::text as created_at_str,
                               COALESCE((SELECT COUNT(*) FROM past_services ps WHERE ps.phone_number = c.phone_number), 0) as services_count,
                               COALESCE((SELECT COUNT(*) FROM current_requests cr WHERE cr.phone_number = c.phone_number), 0) as requests_count
                        FROM customers c 
                        ORDER BY c.created_at DESC 
                        LIMIT 10
                    """)
                    
                    customers = cur.fetchall()
                    for customer in customers:
                        try:
                            customer_dict = {
                                "phone_number": str(customer.get('phone_number', '')),
                                "name": str(customer.get('name', 'غير معروف')),
                                "gender": str(customer.get('gender', 'غير محدد')),
                                "services_count": int(customer.get('services_count', 0)),
                                "requests_count": int(customer.get('requests_count', 0)),
                                "preferred_nationality": str(customer.get('preferred_nationality', 'غير محدد')),
                                "created_at": str(customer.get('created_at_str', ''))
                            }
                            stats["registered_customers"].append(customer_dict)
                        except Exception as customer_error:
                            print(f"Error processing customer data: {customer_error}")
                            continue
                    
                    stats["system_info"]["status"] = "success"
                    
            except Exception as db_error:
                print(f"Database error: {db_error}")
                stats["system_info"]["database_error"] = str(db_error)
                stats["system_info"]["status"] = "database_error"
            finally:
                if conn:
                    try:
                        customer_memory.db_pool.putconn(conn)
                    except Exception as conn_error:
                        print(f"Error returning connection: {conn_error}")
        else:
            stats["system_info"]["status"] = "no_database_connection"
    
    except Exception as general_error:
        print(f"General error: {general_error}")
        stats["system_info"]["general_error"] = str(general_error)
        stats["system_info"]["status"] = "error"
    
    return jsonify(stats)

@app.route('/admin')
def admin_panel():
    """لوحة تحكم الإدارة لإدارة العملاء"""
    return render_template_string(ADMIN_TEMPLATE)

@app.route('/admin/add-customer', methods=['POST'])
def add_customer():
    """إضافة عميل جديد"""
    try:
        # جلب البيانات من النموذج
        phone_number = request.form.get('phone_number', '').strip()
        name = request.form.get('name', '').strip()
        gender = request.form.get('gender', '')
        preferred_nationality = request.form.get('preferred_nationality', '')
        preferences = request.form.get('preferences', '').strip()
        
        # التحقق من صحة البيانات
        if not phone_number or not name:
            return jsonify({
                'success': False, 
                'message': 'رقم الهاتف والاسم مطلوبان'
            }), 400
        
        # تطبيع رقم الهاتف
        normalized_phone = customer_memory.normalize_phone_number(phone_number)
        
        # إضافة العميل لقاعدة البيانات
        if customer_memory.db_pool:
            conn = customer_memory.db_pool.getconn()
            try:
                with conn.cursor() as cur:
                    # التحقق من وجود العميل مسبقاً
                    cur.execute("SELECT phone_number FROM customers WHERE phone_number = %s", (normalized_phone,))
                    if cur.fetchone():
                        return jsonify({
                            'success': False, 
                            'message': f'العميل {phone_number} موجود بالفعل في قاعدة البيانات'
                        }), 400
                    
                    # إضافة العميل الجديد
                    cur.execute("""
                        INSERT INTO customers (phone_number, name, gender, preferred_nationality, preferences, created_at)
                        VALUES (%s, %s, %s, %s, %s, NOW())
                    """, (normalized_phone, name, gender, preferred_nationality, preferences))
                    
                    conn.commit()
                    
                    # تنظيف الكاش للتأكد من تحديث البيانات
                    if phone_number in customer_memory.customer_cache:
                        del customer_memory.customer_cache[phone_number]
                    if normalized_phone in customer_memory.customer_cache:
                        del customer_memory.customer_cache[normalized_phone]
                    
                    return jsonify({
                        'success': True, 
                        'message': f'تم إضافة العميل {name} ({phone_number}) بنجاح!'
                    })
                    
            finally:
                customer_memory.db_pool.putconn(conn)
        else:
            return jsonify({
                'success': False, 
                'message': 'خطأ في الاتصال بقاعدة البيانات'
            }), 500
            
    except Exception as e:
        print(f"خطأ في إضافة العميل: {e}")
        return jsonify({
            'success': False, 
            'message': f'حدث خطأ: {str(e)}'
        }), 500

# باقي المسارات للإدارة (من admin_routes.py)
setup_admin_routes(app, customer_memory)

# تشغيل التنظيف الذكي
start_cleanup_thread(conversation_manager, customer_memory, whatsapp_handler)

if __name__ == '__main__':
    print("🧠 تشغيل بوت الركائز الذكي المحسن مع القوائم التفاعلية...")
    print("⚡ المميزات المحسنة:")
    print("   - ✅ توفير 70-80% من استهلاك الـ RAM")
    print("   - 🧠 OpenAI embeddings بدلاً من النماذج المحلية")
    print("   - 💾 cache ذكي في PostgreSQL")
    print("   - ⚡ ردود فورية للترحيب والأسعار")
    print("   - 🙏 ردود شكر فورية بالهجة السعودية")
    print("   - 🧠 ذاكرة شخصية لكل عميل")
    print("   - 👤 تخزين بيانات ديناميكي مع PostgreSQL")
    print("   - 📊 تتبع الخدمات السابقة والطلبات الحالية")
    print("   - 💬 سياق المحادثة الذكي")
    print("   - 🎯 ردود مخصصة حسب تفضيلات العميل")
    print("   - 💰 تكلفة أقل بـ 60-70% شهرياً")
    print("   - 📱 قوائم تفاعلية في الواتساب")
    print("   - 🔘 أزرار سريعة للخدمات")
    print("   - 📋 قوائم منسدلة للوصول السريع")
    print("   - 🌟 قائمة ترحيبية للعملاء الجدد")
    print("   - 💡 عرض القائمة بكتابة 'مساعدة'")
    print("=" * 70)
    print("🎉 النظام جاهز للقوائم التفاعلية الذكية مع توفير هائل في الـ RAM!")
    print("💡 استهلاك ذاكرة أقل بـ 70-80% من النظام السابق")
    print("=" * 70)
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))