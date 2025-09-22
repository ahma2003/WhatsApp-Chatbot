import os
import json
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
from psycopg2.extras import RealDictCursor

# استيراد الملفات المحدثة
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
print("🔄 تحميل النظام المحسن...")

customer_memory = CustomerMemoryManager()
conversation_manager = ConversationManager(customer_memory)
quick_system = QuickResponseSystem()
whatsapp_handler = WhatsAppHandler(quick_system)

# تحميل مكونات الذكاء الاصطناعي
openai_client = None
enhanced_retriever = None
response_generator = None

# تحميل OpenAI Client
if OPENAI_API_KEY:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        print("✅ OpenAI Client جاهز")
    except Exception as e:
        print(f"⚠️ تحذير في تحميل OpenAI: {e}")

# تحميل النظام الذكي
try:
    print("🔊 تهيئة نظام البحث الذكي...")
    enhanced_retriever = EnhancedRetriever(customer_memory)
    response_generator = SmartResponseGenerator(openai_client, enhanced_retriever, quick_system, customer_memory)
    print("✅ النظام المحدث جاهز!")
except Exception as e:
    print(f"⚠️ تحذير في تحميل النظام: {e}")
    print("💡 سيعمل بالردود السريعة فقط")
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
                    
                    # === معالجة الرسائل التفاعلية ===
                    if message_type == 'interactive':
                        interactive_data = message_data.get('interactive', {})
                        thread = threading.Thread(
                            target=handle_interactive_message_thread,
                            args=(phone_number, interactive_data),
                            daemon=True
                        )
                        thread.start()
                        continue
                    
                    # === معالجة الرسائل النصية ===
                    if message_type == 'text':
                        user_message = message_data.get('text', {}).get('body', '').strip()
                        
                        if not user_message:
                            continue
                        
                        print(f"📨 رسالة من {phone_number}: {user_message}")
                        
                        # معالجة فورية في thread منفصل
                        thread = threading.Thread(
                            target=process_user_message_fixed,
                            args=(phone_number, user_message),
                            daemon=True
                        )
                        thread.start()
        
        return 'OK', 200

def handle_interactive_message_thread(phone_number: str, interactive_data: dict):
    """معالجة الرسائل التفاعلية"""
    try:
        print(f"🔘 رد تفاعلي من {phone_number}")
        conversation_manager.update_activity(phone_number)
        success = whatsapp_handler.handle_interactive_message(interactive_data, phone_number)
        
        if success:
            print(f"✅ تم معالجة الرد التفاعلي: {phone_number}")
        else:
            print(f"❌ فشل في معالجة الرد التفاعلي: {phone_number}")
            
    except Exception as e:
        print(f"❌ خطأ في معالجة الرد التفاعلي: {e}")
        whatsapp_handler.send_message(phone_number, "عذراً، حدث خطأ تقني. 📞 0556914447")

def process_user_message_fixed(phone_number: str, user_message: str):
    """معالجة مُحسّنة للرسائل مع إصلاح عدم الرد"""
    start_time = time.time()
    
    try:
        print(f"🔄 بدء معالجة: '{user_message}' من {phone_number}")
        
        # إدارة المحادثة
        is_first = conversation_manager.is_first_message(phone_number)
        
        if is_first:
            conversation_manager.register_conversation(phone_number)
            print(f"🆕 محادثة جديدة: {phone_number}")
        else:
            conversation_manager.update_activity(phone_number)
        
        # جلب معلومات العميل
        customer_info = customer_memory.get_customer_info(phone_number)
        customer_name = customer_info.get('name', '') if customer_info else None
        
        # === فحص طلب القائمة الرئيسية ===
        if whatsapp_handler.should_show_main_menu(user_message):
            print(f"📋 طلب قائمة رئيسية من: {phone_number}")
            success = whatsapp_handler.interactive_menu.send_main_menu(phone_number)
            if not success:
                fallback_message = get_fallback_menu_message(customer_name)
                whatsapp_handler.send_message(phone_number, fallback_message)
            return
        
        # === للعملاء الجدد - إرسال قائمة ترحيبية ===
        if is_first:
            print(f"🌟 عميل جديد - إرسال ترحيب: {phone_number}")
            success = whatsapp_handler.send_welcome_menu_to_new_customer(phone_number, customer_name)
            if not success:
                # رد احتياطي للعملاء الجدد
                if customer_name:
                    fallback = f"""أهلاً وسهلاً أخونا {customer_name} الكريم! 🌟

مرحباً بك مرة ثانية في مكتب الركائز البشرية للاستقدام

يمكنك كتابة:
• "أسعار" - لعرض الأسعار
• "مساعدة" - للحصول على المساعدة

📞 للتواصل المباشر: 0556914447"""
                else:
                    fallback = """أهلاً وسهلاً بك في مكتب الركائز البشرية! 🌟

نحن هنا لخدمتك في جميع احتياجاتك من العمالة المنزلية

يمكنك كتابة:
• "أسعار" - لعرض الأسعار
• "مساعدة" - للحصول على المساعدة

📞 للتواصل: 0556914447"""
                whatsapp_handler.send_message(phone_number, fallback)
            return
        
        # === توليد الرد الذكي ===
        bot_response = None
        should_send_image = False
        image_url = None
        
        if response_generator:
            print(f"🧠 استخدام النظام الذكي")
            try:
                bot_response, should_send_image, image_url = response_generator.generate_response(
                    user_message, phone_number, is_first
                )
            except Exception as e:
                print(f"❌ خطأ في النظام الذكي: {e}")
                bot_response = None
        
        # === نظام احتياطي إذا فشل الذكي ===
        if not bot_response:
            print(f"🔧 استخدام النظام الاحتياطي")
            
            # فحص الترحيب
            if quick_system.is_greeting_message(user_message):
                bot_response = quick_system.get_welcome_response(customer_name)
            
            # فحص الشكر  
            elif quick_system.is_thanks_message(user_message):
                bot_response = quick_system.get_thanks_response(customer_name)
            
            # فحص الأسعار
            elif quick_system.is_price_inquiry(user_message):
                bot_response, image_url = quick_system.get_price_response()
                should_send_image = True
            
            # رد عام
            else:
                if customer_name:
                    bot_response = f"""أهلاً وسهلاً أخونا {customer_name} الكريم مرة ثانية! 🌟

شكراً لتواصلك مع مكتب الركائز البشرية للاستقدام

سيتواصل معك أحد متخصصينا قريباً لمساعدتك

💡 يمكنك كتابة "مساعدة" لعرض قائمة خدماتنا التفاعلية

📞 للتواصل المباشر: 0556914447"""
                else:
                    bot_response = """أهلاً وسهلاً بك في مكتب الركائز البشرية! 🌟

شكراً لتواصلك معنا، سيتواصل معك أحد موظفينا قريباً

💡 اكتب "مساعدة" لعرض قائمة خدماتنا التفاعلية

📞 للتواصل المباشر: 0556914447"""
        
        # === إرسال الرد ===
        success = False
        if should_send_image and image_url:
            print(f"🖼️ إرسال صورة مع نص")
            success = whatsapp_handler.send_image_with_text(phone_number, bot_response, image_url)
        else:
            print(f"💬 إرسال رسالة نصية")
            success = whatsapp_handler.send_message(phone_number, bot_response)
        
        if success:
            # إضافة للذاكرة
            customer_memory.add_conversation_message(phone_number, user_message, bot_response)
            
            # إحصائيات
            response_time = time.time() - start_time
            customer_status = "عميل مسجل" if customer_info else "عميل جديد"
            print(f"✅ تم الرد في {response_time:.2f}s لـ {phone_number} ({customer_status})")
        else:
            print(f"❌ فشل في إرسال الرد لـ {phone_number}")
        
    except Exception as e:
        print(f"❌ خطأ عام في المعالجة: {e}")
        # رد طوارئ
        try:
            emergency_response = "عذراً، حدث خطأ تقني مؤقت. يرجى المحاولة مرة أخرى أو الاتصال بنا: 📞 0556914447"
            whatsapp_handler.send_message(phone_number, emergency_response)
        except:
            print(f"❌ فشل حتى في الرد الطارئ لـ {phone_number}")

def get_fallback_menu_message(customer_name: str = None) -> str:
    """رسالة قائمة احتياطية إذا فشلت القوائم التفاعلية"""
    if customer_name:
        return f"""أهلاً أخونا {customer_name} الكريم! 🌟

خدماتنا في مكتب الركائز البشرية:

🏠 العمالة المنزلية
👶 مربيات الأطفال  
👨‍🍳 الطباخات
🚗 السائقين
🌾 عمال الزراعة

💰 للأسعار - اكتب: "أسعار"
📞 للتواصل: 0556914447 / 0506207444"""
    else:
        return """أهلاً وسهلاً بك في مكتب الركائز البشرية! 🌟

خدماتنا المتاحة:

🏠 العمالة المنزلية
👶 مربيات الأطفال  
👨‍🍳 الطباخات
🚗 السائقين
🌾 عمال الزراعة

💰 للأسعار - اكتب: "أسعار"
📞 للتواصل: 0556914447 / 0506207444"""

# === باقي المسارات (كما هي) ===
@app.route('/')
def home():
    return render_template_string(HOME_TEMPLETE)

@app.route('/status')
def status():
    active_conversations = len(conversation_manager.conversations)
    cached_customers = len(customer_memory.customer_cache)
    handler_stats = whatsapp_handler.get_handler_stats()
    
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
    return render_template_string(PERFORMANCE_TEMPLATE)

@app.route('/customers-stats')
def customers_stats():
    return render_template_string(CUSTOMERS_TEMPLATE)

@app.route('/api/customers-stats')
def api_customers_stats():
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
                    cur.execute("SELECT COUNT(*) as total FROM customers")
                    count_result = cur.fetchone()
                    if count_result:
                        stats["total_customers"] = int(count_result['total'])
                    
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
    return render_template_string(ADMIN_TEMPLATE)

@app.route('/admin/add-customer', methods=['POST'])
def add_customer():
    try:
        phone_number = request.form.get('phone_number', '').strip()
        name = request.form.get('name', '').strip()
        gender = request.form.get('gender', '')
        preferred_nationality = request.form.get('preferred_nationality', '')
        preferences = request.form.get('preferences', '').strip()
        
        if not phone_number or not name:
            return jsonify({
                'success': False, 
                'message': 'رقم الهاتف والاسم مطلوبان'
            }), 400
        
        normalized_phone = customer_memory.normalize_phone_number(phone_number)
        
        if customer_memory.db_pool:
            conn = customer_memory.db_pool.getconn()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT phone_number FROM customers WHERE phone_number = %s", (normalized_phone,))
                    if cur.fetchone():
                        return jsonify({
                            'success': False, 
                            'message': f'العميل {phone_number} موجود بالفعل في قاعدة البيانات'
                        }), 400
                    
                    cur.execute("""
                        INSERT INTO customers (phone_number, name, gender, preferred_nationality, preferences, created_at)
                        VALUES (%s, %s, %s, %s, %s, NOW())
                    """, (normalized_phone, name, gender, preferred_nationality, preferences))
                    
                    conn.commit()
                    
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

# باقي المسارات الإدارية
setup_admin_routes(app, customer_memory)

# تشغيل التنظيف الذكي
start_cleanup_thread(conversation_manager, customer_memory, whatsapp_handler)

if __name__ == '__main__':
    print("🧠 تشغيل بوت الركائز الذكي المحسن [إصدار مُصحح]...")
    print("🔧 الإصلاحات المطبقة:")
    print("   - ✅ إصلاح عدم الرد على الرسائل النصية")
    print("   - ✅ إضافة نظام احتياطي قوي")
    print("   - ✅ إصلاح معالجة العملاء الجدد")
    print("   - ✅ تحسين رسائل الخطأ")
    print("   - ✅ إضافة logs مفصلة للتتبع")
    print("=" * 70)
    print("🎉 النظام جاهز للعمل مع ضمان الرد على جميع الرسائل!")
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))