import os

# --- إعدادات WhatsApp ---
ACCESS_TOKEN = os.environ.get('WHATSAPP_ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('WHATSAPP_VERIFY_TOKEN')
PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')

# --- إعدادات OpenAI ---
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# --- إعدادات قاعدة البيانات ---
DATABASE_URL = os.environ.get('DATABASE_URL')

# --- إعدادات ChromaDB ---
MODEL_NAME = "intfloat/multilingual-e5-large"
PERSIST_DIRECTORY = "my_chroma_db"
COLLECTION_NAME = "recruitment_qa"

# --- متغيرات عامة ---
gen = False

# --- إعدادات إضافية ---
# المنطقة الزمنية
TIMEZONE = 'Asia/Riyadh'

# إعدادات الكاش
CACHE_TIMEOUT = 3600  # ساعة واحدة
MAX_CACHE_SIZE = 100  # 100 عميل في الكاش

# إعدادات المحادثة
MAX_CONVERSATION_HISTORY = 10  # آخر 10 رسائل
CONVERSATION_CONTEXT_SIZE = 3  # آخر 3 رسائل للسياق

# إعدادات الردود
RESPONSE_TIMEOUT = 30  # 30 ثانية timeout للردود
MAX_MESSAGE_LENGTH = 900  # أقصى طول للرسالة

# معلومات المكتب
OFFICE_PHONES = ['0556914447', '0506207444', '0537914445']
OFFICE_NAME = 'مكتب الركائز البشرية للاستقدام'

# رابط صورة الأسعار (يجب تحديثه)
PRICES_IMAGE_URL = "https://i.imghippo.com/files/La2232xjc.jpg"

# إعدادات قاعدة البيانات المتقدمة
DB_POOL_MIN_CONN = 1
DB_POOL_MAX_CONN = 10
DB_CONNECTION_TIMEOUT = 30

print("✅ تم تحميل إعدادات النظام")
if DATABASE_URL:
    print("📊 قاعدة بيانات PostgreSQL - متصلة")
if OPENAI_API_KEY:
    print("🧠 OpenAI API - متاح")
if ACCESS_TOKEN:
    print("📱 WhatsApp Business API - متاح")
