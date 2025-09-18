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
MODEL_NAME = 'intfloat/multilingual-e5-large'
PERSIST_DIRECTORY = "my_chroma_db"
COLLECTION_NAME = "recruitment_qa"

# --- متغيرات عامة ---
gen = False