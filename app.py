import os
import json
import threading
import time
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
import chromadb
from sentence_transformers import SentenceTransformer
from psycopg2.extras import RealDictCursor

# استيراد الملفات الجديدة
from config import *
from customer_memory import CustomerMemoryManager
from conversation_manager import ConversationManager
from quick_response import QuickResponseSystem
from ai_retriever import EnhancedRetriever
from smart_response import SmartResponseGenerator
from whatsapp_handler import WhatsAppHandler
from admin_template import ADMIN_TEMPLATE
from cleanup_manager import start_cleanup_thread

# إنشاء التطبيق
app = Flask(__name__)

# --- تهيئة النظام الذكي مع الذاكرة ---
customer_memory = CustomerMemoryManager()
conversation_manager = ConversationManager(customer_memory)
quick_system = QuickResponseSystem()
whatsapp_handler = WhatsAppHandler(quick_system)

# تحميل مكونات الذكاء الاصطناعي
openai_client = None
enhanced_retriever = None
response_generator = None

if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    print("✅ OpenAI جاهز")

# تحميل ChromaDB (اختياري - للسرعة)
try:
    print("📄 تحميل نموذج الذكاء الاصطناعي...")
    model = SentenceTransformer(MODEL_NAME)
    
    print("📄 الاتصال بقاعدة البيانات...")
    chroma_client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
    collection = chroma_client.get_collection(name=COLLECTION_NAME)
    
    enhanced_retriever = EnhancedRetriever(model, collection)
    response_generator = SmartResponseGenerator(openai_client, enhanced_retriever, quick_system, customer_memory)
    
    print(f"✅ النظام جاهز مع الذاكرة الذكية! قاعدة البيانات: {collection.count()} مستند")

except Exception as e:
    print(f"⌚ فشل تحميل AI: {e}")
    print("💡 سيعمل بالردود السريعة والذاكرة فقط")
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
        
        # === توليد الرد الذكي مع الذاكرة ===
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

@app.route('/')
def home():
    """الصفحة الرئيسية مع أزرار التنقل"""
    return render_template_string("""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مكتب الركائز البشرية - النظام الذكي التفاعلي</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .hero-section {
            padding: 60px 0;
            color: white;
            text-align: center;
        }
        .feature-card {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        .feature-card:hover {
            transform: translateY(-5px);
        }
        .btn-custom {
            padding: 15px 30px;
            font-size: 18px;
            border-radius: 50px;
            margin: 10px;
            transition: all 0.3s;
        }
        .btn-custom:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        .stats-box {
            background: rgba(255,255,255,0.9);
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .new-feature {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="hero-section">
        <div class="container">
            <h1 class="display-3 mb-4">🧠 مكتب الركائز البشرية</h1>
            <p class="lead mb-4">النظام الذكي التفاعلي مع القوائم التفاعلية والذاكرة الشخصية</p>
            
            <!-- إعلان الميزة الجديدة -->
            <div class="new-feature">
                <h4>🆕 جديد! القوائم التفاعلية في الواتساب</h4>
                <p>الآن العملاء يمكنهم استخدام قوائم تفاعلية وأزرار سريعة للوصول لخدماتنا!</p>
            </div>
            
            <div class="row justify-content-center">
                <div class="col-md-3">
                    <a href="/status" class="btn btn-light btn-custom">
                        <i class="fas fa-chart-line"></i><br>حالة النظام
                    </a>
                </div>
                <div class="col-md-3">
                    <a href="/admin" class="btn btn-warning btn-custom">
                        <i class="fas fa-cog"></i><br>لوحة الإدارة
                    </a>
                </div>
                <div class="col-md-3">
                    <a href="/customers-stats" class="btn btn-info btn-custom">
                        <i class="fas fa-users"></i><br>إحصائيات العملاء
                    </a>
                </div>
                <div class="col-md-3">
                    <a href="/test-system" class="btn btn-success btn-custom">
                        <i class="fas fa-flask"></i><br>اختبار النظام
                    </a>
                </div>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="row">
            <div class="col-md-4">
                <div class="feature-card">
                    <i class="fas fa-mobile-alt fa-3x text-primary mb-3"></i>
                    <h4>قوائم تفاعلية</h4>
                    <p>أزرار وقوائم منسدلة في الواتساب للوصول السريع للخدمات</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="feature-card">
                    <i class="fas fa-brain fa-3x text-success mb-3"></i>
                    <h4>ذاكرة شخصية</h4>
                    <p>يتذكر اسم كل عميل وتاريخه مع المكتب</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="feature-card">
                    <i class="fas fa-lightning-bolt fa-3x text-warning mb-3"></i>
                    <h4>ردود فورية</h4>
                    <p>استجابة سريعة للترحيب والأسعار والشكر</p>
                </div>
            </div>
        </div>
        
        <div class="stats-box text-center">
            <h3>النظام يعمل بأقصى ذكاء مع القوائم التفاعلية! 🚀</h3>
            <p>متكامل مع WhatsApp Business API وOpenAI وPostgreSQL</p>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """)

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
    
    return f"""
    <html><head><title>حالة النظام - الركائز البشرية</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
    body{{font-family:Arial;margin:40px;background:#f0f8ff;}}
    .box{{background:white;padding:20px;border-radius:10px;margin:10px 0;box-shadow:0 4px 8px rgba(0,0,0,0.1);}}
    .green{{color:#28a745;}} .red{{color:#dc3545;}} .blue{{color:#007bff;}} .purple{{color:#6f42c1;}} .orange{{color:#fd7e14;}}
    .stat{{background:#e3f2fd;padding:15px;margin:10px 0;border-radius:8px;border-left:4px solid #2196f3;}}
    h1{{color:#1976d2;text-align:center;}}
    .new{{background:#fff3cd;border-left:4px solid #ffc107;}}
    </style></head><body>
    
    <div class="container">
        <div class="box">
            <h1>🧠 حالة النظام الذكي التفاعلي</h1>
            <div class="text-center">
                <a href="/" class="btn btn-primary">العودة للرئيسية</a>
                <a href="/admin" class="btn btn-warning">لوحة الإدارة</a>
            </div>
        </div>
        
        <div class="box">
            <h2>📊 الحالة العامة:</h2>
            <p class="{'green' if openai_client else 'red'}">{'✅' if openai_client else '❌'} OpenAI API</p>
            <p class="{'green' if enhanced_retriever else 'red'}">{'✅' if enhanced_retriever else '❌'} قاعدة البيانات الذكية</p>
            <p class="{'green' if customer_memory.db_pool else 'red'}">{'✅' if customer_memory.db_pool else '❌'} PostgreSQL Connection</p>
            <p class="green">⚡ الردود السريعة - نشط</p>
            <p class="blue">🙏 ردود الشكر السريعة - نشط</p>
            <p class="purple">🧠 <strong>محدث!</strong> نظام الذاكرة مع PostgreSQL - نشط</p>
            <p class="orange">📱 <strong>جديد!</strong> القوائم التفاعلية في الواتساب - {'نشط' if handler_stats['interactive_menu_available'] else 'غير نشط'}</p>
        </div>
        
        <div class="stat new">
            <h2>🆕 المميزات التفاعلية الجديدة:</h2>
            <ul>
                <li>✅ <strong>قوائم تفاعلية:</strong> أزرار وقوائم منسدلة في الواتساب</li>
                <li>✅ <strong>قائمة ترحيبية للعملاء الجدد:</strong> تظهر تلقائياً</li>
                <li>✅ <strong>أزرار سريعة:</strong> عاملة منزلية، مربية أطفال، تواصل معنا</li>
                <li>✅ <strong>معالجة ذكية للتفاعل:</strong> ردود تلقائية حسب الاختيار</li>
                <li>✅ <strong>عرض قائمة بكلمة "مساعدة":</strong> وصول سريع للخدمات</li>
                <li>✅ <strong>مسارات ذكية:</strong> اختيار "أسعار" → صورة فورية</li>
            </ul>
        </div>
        
        <div class="stat">
            <h2>🧠 إحصائيات الذاكرة الذكية:</h2>
            <ul>
                <li><strong>إجمالي العملاء المسجلين:</strong> {total_customers} عميل</li>
                <li><strong>العملاء النشطين في الذاكرة:</strong> {cached_customers} عميل</li>
                <li><strong>المحادثات النشطة:</strong> {active_conversations} محادثة</li>
                <li><strong>الرسائل قيد المعالجة:</strong> {handler_stats['processing_messages_count']} رسالة</li>
                <li><strong>الأرقام المحدودة السرعة:</strong> {handler_stats['rate_limited_numbers']} رقم</li>
            </ul>
        </div>
        
        <div class="box">
            <h2>⚡ المميزات المحدثة:</h2>
            <ul>
                <li>✅ <strong>قاعدة بيانات PostgreSQL:</strong> بيانات ديناميكية ومحدثة</li>
                <li>✅ <strong>ذاكرة شخصية للعملاء:</strong> البوت يتذكر اسم العميل وتاريخه</li>
                <li>✅ <strong>ترحيب مخصص:</strong> "أهلاً أخونا أحمد الكريم مرة ثانية"</li>
                <li>✅ <strong>تتبع الخدمات السابقة:</strong> يعرف العمالة السابقة والطلبات الحالية</li>
                <li>✅ <strong>سياق المحادثة:</strong> يتذكر آخر 3 رسائل من كل عميل</li>
                <li>✅ <strong>ردود ذكية مخصصة:</strong> حسب تفضيلات كل عميل</li>
                <li>✅ <strong>كاش ذكي:</strong> سرعة عالية مع توفير الذاكرة</li>
                <li>🆕 <strong>قوائم تفاعلية:</strong> تجربة مستخدم متطورة في الواتساب</li>
                <li>🆕 <strong>أزرار سريعة:</strong> وصول فوري للخدمات والأسعار</li>
                <li>🆕 <strong>معالجة تفاعلية:</strong> ردود ذكية على الأزرار والقوائم</li>
            </ul>
        </div>
        
        <p class="green text-center"><strong>النظام يعمل بأقصى ذكاء مع القوائم التفاعلية! 🧠 📱 🚀</strong></p>
    </div>
    </body></html>"""

@app.route('/test-system')
def test_system():
    """صفحة اختبار النظام"""
    return render_template_string("""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>اختبار النظام - الركائز البشرية</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body style="background:#f8f9fa; padding:20px;">
    <div class="container">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h3>🧪 اختبار النظام الذكي التفاعلي</h3>
                <a href="/" class="btn btn-light">العودة للرئيسية</a>
            </div>
            <div class="card-body">
                <h4>اختبار سريع للذاكرة:</h4>
                <div class="mb-3">
                    <label>رقم الهاتف للاختبار:</label>
                    <input type="text" class="form-control" id="phoneInput" value="201234567890" placeholder="رقم الهاتف">
                </div>
                <div class="mb-3">
                    <label>الرسالة للاختبار:</label>
                    <input type="text" class="form-control" id="messageInput" value="السلام عليكم" placeholder="اكتب رسالة">
                </div>
                <button class="btn btn-success" onclick="testSystem()">اختبر النظام</button>
                <button class="btn btn-info" onclick="testMenu()">اختبر القائمة التفاعلية</button>
                
                <div id="result" class="mt-4"></div>
            </div>
        </div>
    </div>
    
    <script>
    function testSystem() {
        const phone = document.getElementById('phoneInput').value;
        const message = document.getElementById('messageInput').value;
        
        fetch(`/test-customer/${phone}/${message}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('result').innerHTML = `
                    <div class="alert alert-info">
                        <h5>نتيجة الاختبار:</h5>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    </div>
                `;
            })
            .catch(error => {
                document.getElementById('result').innerHTML = `
                    <div class="alert alert-danger">خطأ: ${error}</div>
                `;
            });
    }
    
    function testMenu() {
        document.getElementById('result').innerHTML = `
            <div class="alert alert-success">
                <h5>📱 القوائم التفاعلية متاحة في الواتساب:</h5>
                <ul>
                    <li>✅ قائمة رئيسية عند بداية المحادثة</li>
                    <li>✅ أزرار للخدمات (عاملة منزلية، مربية أطفال)</li>
                    <li>✅ قائمة الأسعار مع الصور</li>
                    <li>✅ معلومات التواصل والمتطلبات</li>
                    <li>✅ عرض القائمة بكتابة "مساعدة"</li>
                </ul>
                <p><strong>اختبر من الواتساب مباشرة!</strong></p>
            </div>
        `;
    }
    </script>
</body>
</html>
    """)

@app.route('/test-customer/<phone_number>/<message>')
def test_customer_memory(phone_number, message):
    """اختبار نظام الذاكرة للعملاء"""
    start_time = time.time()
    
    # جلب معلومات العميل
    customer_info = customer_memory.get_customer_info(phone_number)
    
    # اختبار الردود السريعة
    is_greeting = quick_system.is_greeting_message(message)
    is_thanks = quick_system.is_thanks_message(message)
    is_price = quick_system.is_price_inquiry(message)
    is_menu_request = whatsapp_handler.should_show_main_menu(message)
    
    processing_time = time.time() - start_time
    
    result = {
        "رقم_الهاتف": phone_number,
        "الرسالة": message,
        "عميل_مسجل": customer_info is not None,
        "اسم_العميل": customer_info.get('name', 'غير مسجل') if customer_info else 'غير مسجل',
        "نوع_الرسالة": {
            "ترحيب": is_greeting,
            "شكر": is_thanks,
            "سؤال_أسعار": is_price,
            "طلب_قائمة_تفاعلية": is_menu_request
        },
        "الميزات_التفاعلية": {
            "قائمة_تفاعلية_متاحة": whatsapp_handler.interactive_menu is not None,
            "معالج_الأزرار_نشط": True,
            "معالج_القوائم_نشط": True
        },
        "وقت_المعالجة": f"{processing_time:.4f} ثانية",
        "حالة_النظام": "جاهز للقوائم التفاعلية"
    }
    
    return jsonify(result, ensure_ascii=False)

@app.route('/customers-stats')
def customers_stats():
    """إحصائيات مفصلة عن العملاء من PostgreSQL"""
    stats = {
        "إجمالي_العملاء_المسجلين": 0,
        "العملاء_النشطين_في_الذاكرة": len(customer_memory.customer_cache),
        "المحادثات_النشطة": len(conversation_manager.conversations),
        "العملاء_المسجلون": [],
        "إحصائيات_التفاعل": whatsapp_handler.get_handler_stats()
    }
    
    try:
        if customer_memory.db_pool:
            conn = customer_memory.db_pool.getconn()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # جلب عدد العملاء
                cur.execute("SELECT COUNT(*) FROM customers")
                stats["إجمالي_العملاء_المسجلين"] = cur.fetchone()[0]
                
                # جلب أول 10 عملاء مع تفاصيلهم
                cur.execute("""
                    SELECT c.*, 
                           (SELECT COUNT(*) FROM past_services WHERE phone_number = c.phone_number) as services_count,
                           (SELECT COUNT(*) FROM current_requests WHERE phone_number = c.phone_number) as requests_count
                    FROM customers c 
                    ORDER BY c.created_at DESC 
                    LIMIT 10
                """)
                
                customers = cur.fetchall()
                for customer in customers:
                    stats["العملاء_المسجلون"].append({
                        "رقم_الهاتف": customer['phone_number'],
                        "الاسم": customer.get('name', 'غير معروف'),
                        "الجنس": customer.get('gender', 'غير محدد'),
                        "عدد_الخدمات_السابقة": customer['services_count'],
                        "عدد_الطلبات_الحالية": customer['requests_count'],
                        "الجنسية_المفضلة": customer.get('preferred_nationality', 'غير محدد')
                    })
            
            customer_memory.db_pool.putconn(conn)
    
    except Exception as e:
        print(f"خطأ في جلب إحصائيات العملاء: {e}")
    
    return jsonify(stats, ensure_ascii=False)

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

# باقي المسارات للإدارة
from admin_routes import setup_admin_routes
setup_admin_routes(app, customer_memory)

# تشغيل التنظيف الذكي
start_cleanup_thread(conversation_manager, customer_memory, whatsapp_handler)

if __name__ == '__main__':
    print("🧠 تشغيل بوت الركائز الذكي مع القوائم التفاعلية...")
    print("⚡ المميزات:")
    print("   - ردود فورية للترحيب والأسعار")
    print("   - 🙏 ردود شكر فورية بالهجة السعودية")
    print("   - 🧠 ذاكرة شخصية لكل عميل")
    print("   - 👤 تخزين بيانات ديناميكي مع PostgreSQL")
    print("   - 📊 تتبع الخدمات السابقة والطلبات الحالية")
    print("   - 💬 سياق المحادثة الذكي")
    print("   - 🎯 ردود مخصصة حسب تفضيلات العميل")
    print("   - ⚡ كاش ذكي للسرعة العالية")
    print("   - 📱 **جديد!** قوائم تفاعلية في الواتساب")
    print("   - 🔘 **جديد!** أزرار سريعة للخدمات")
    print("   - 📋 **جديد!** قوائم منسدلة للوصول السريع")
    print("   - 🌟 **جديد!** قائمة ترحيبية للعملاء الجدد")
    print("   - 💡 **جديد!** عرض القائمة بكتابة 'مساعدة'")
    print("=" * 70)
    print("🎉 النظام جاهز للقوائم التفاعلية الذكية!")
    print("=" * 70)
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))