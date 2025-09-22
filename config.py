import os

# --- إعدادات WhatsApp ---
ACCESS_TOKEN = os.environ.get('WHATSAPP_ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('WHATSAPP_VERIFY_TOKEN')
PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')

# --- إعدادات OpenAI ---
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# --- إعدادات قاعدة البيانات ---
DATABASE_URL = os.environ.get('DATABASE_URL')

<<<<<<< HEAD
# --- إعدادات Embeddings الجديدة (OpenAI فقط) ---
EMBEDDING_MODEL = "text-embedding-3-small"  # أرخص وأسرع
USE_OPENAI_EMBEDDINGS = True
ENABLE_EMBEDDING_CACHE = True  # cache للتوفير
EMBEDDING_CACHE_DURATION = 86400  # 24 ساعة

# --- إلغاء إعدادات ChromaDB والنماذج المحلية ---
# (محذوفة لتوفير الذاكرة)
=======
# --- إعدادات ChromaDB ---
MODEL_NAME = "intfloat/multilingual-e5-large"
PERSIST_DIRECTORY = "my_chroma_db"
COLLECTION_NAME = "recruitment_qa"
>>>>>>> 48acdaad575ae42c443f8469a20da9c9faa3d4ee

# --- متغيرات عامة ---
gen = False

# --- إعدادات إضافية ---
TIMEZONE = 'Asia/Riyadh'

# إعدادات الكاش المحسنة
CACHE_TIMEOUT = 3600  # ساعة واحدة
MAX_CACHE_SIZE = 50   # مخفض من 100 لتوفير ذاكرة

# إعدادات المحادثة المحسنة  
MAX_CONVERSATION_HISTORY = 5  # مخفض من 10
CONVERSATION_CONTEXT_SIZE = 2  # مخفض من 3

# إعدادات الردود
RESPONSE_TIMEOUT = 30
MAX_MESSAGE_LENGTH = 900

# معلومات المكتب
OFFICE_PHONES = ['0556914447', '0506207444', '0537914445']
OFFICE_NAME = 'مكتب الركائز البشرية للاستقدام'

# رابط صورة الأسعار
PRICES_IMAGE_URL = "https://i.imghippo.com/files/La2232xjc.jpg"

# إعدادات قاعدة البيانات المحسنة
DB_POOL_MIN_CONN = 1
DB_POOL_MAX_CONN = 5  # مخفض من 10
DB_CONNECTION_TIMEOUT = 30

# إعدادات OpenAI embeddings المحسنة
EMBEDDING_BATCH_SIZE = 50  # مخفض من 100 لتوفير API calls
EMBEDDING_RATE_LIMIT_DELAY = 0.2  # زيادة التأخير لتوفير التكلفة

# إعدادات التوفير الجديدة
USE_QUICK_RESPONSES_FIRST = True  # أولوية للردود السريعة
ENABLE_SMART_CACHING = True      # cache ذكي للاستفسارات المتكررة
FALLBACK_TO_SIMPLE_RESPONSE = True  # رد بسيط عند فشل OpenAI

print("✅ تم تحميل إعدادات النظام المحسن (بدون نماذج محلية)")
if DATABASE_URL:
    print("📊 قاعدة بيانات PostgreSQL - متصلة")
if OPENAI_API_KEY:
    print("🧠 OpenAI API - متاح")
    print(f"🤖 نموذج Embeddings: {EMBEDDING_MODEL}")
    print("💰 وضع التوفير - نشط")
if ACCESS_TOKEN:
    print("📱 WhatsApp Business API - متاح")
<<<<<<< HEAD
print("⚡ النظام محسن لاستهلاك أقل للذاكرة!")
=======
>>>>>>> 48acdaad575ae42c443f8469a20da9c9faa3d4ee
