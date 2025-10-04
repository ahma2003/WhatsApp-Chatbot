import threading
import time
import json
import requests
from config import ACCESS_TOKEN, PHONE_NUMBER_ID
from interactive_menu import InteractiveMenuHandler

class WhatsAppHandler:
    def __init__(self, quick_system):
        self.processing_messages = set()
        self.rate_limit = {}
        self.quick_system = quick_system
        
        self.ACCESS_TOKEN = ACCESS_TOKEN
        self.PHONE_NUMBER_ID = PHONE_NUMBER_ID
        
        # معالج القوائم - سيستخدم رسائل نصية بدلاً من Interactive
        self.interactive_menu = InteractiveMenuHandler(self, quick_system)
    
    def is_duplicate_message(self, message_id: str) -> bool:
        """فحص الرسائل المكررة"""
        if message_id in self.processing_messages:
            return True
        self.processing_messages.add(message_id)
        threading.Timer(30.0, lambda: self.processing_messages.discard(message_id)).start()
        return False
    
    def check_rate_limit(self, phone_number: str) -> bool:
        """فحص معدل سريع"""
        now = time.time()
        if phone_number in self.rate_limit:
            if now - self.rate_limit[phone_number] < 0.5:
                return True
        self.rate_limit[phone_number] = now
        return False
    
    def should_show_main_menu(self, user_message: str) -> bool:
        """فحص طلب القائمة الرئيسية"""
        menu_triggers = [
            'مساعدة', 'help', 'قائمة', 'menu', 'خيارات', 'options',
            'خدمات', 'services', 'البداية', 'start', 'الرئيسية', 'home',
            'مساعده', 'القائمة', 'خدماتكم'
        ]
        
        message_clean = user_message.lower().strip()
        
        for trigger in menu_triggers:
            if trigger in message_clean:
                return True
                
        if len(message_clean) <= 15 and any(word in message_clean for word in ['مساعد', 'ساعد', 'خدم', 'قائم']):
            return True
            
        return False
    
    def send_message(self, to_number: str, message: str) -> bool:
        """إرسال رسالة نصية عبر 360dialog"""
        if not ACCESS_TOKEN:
            print("❌ ACCESS_TOKEN غير موجود")
            return False
        
        url = "https://waba.360dialog.io/v1/messages"
        
        headers = {
            "D360-API-KEY": ACCESS_TOKEN,
            "Content-Type": "application/json"
        }
        
        message = message.strip()
        if len(message) > 900:
            message = message[:850] + "...\n\nللمزيد: 📞 0556914447"
        
        data = {
            "recipient_type": "individual",
            "to": to_number,
            "type": "text",
            "text": {
                "body": message
            }
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=5)
            response.raise_for_status()
            print(f"✅ تم الإرسال إلى {to_number}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ خطأ WhatsApp: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"📄 تفاصيل: {e.response.text}")
            return False
    
    def send_image_with_text(self, to_number: str, message: str, image_url: str) -> bool:
        """إرسال صورة مع نص"""
        if not ACCESS_TOKEN:
            return False
        
        url = "https://waba.360dialog.io/v1/messages"
        
        headers = {
            "D360-API-KEY": ACCESS_TOKEN,
            "Content-Type": "application/json"
        }
        
        if len(message) > 800:
            message = message[:750] + "...\n📞 للمزيد: 0556914447"
        
        data = {
            "recipient_type": "individual",
            "to": to_number,
            "type": "image",
            "image": {
                "link": image_url,
                "caption": message
            }
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=8)
            response.raise_for_status()
            print(f"✅ تم إرسال الصورة إلى {to_number}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ خطأ في الصورة: {e}")
            return self.send_message(to_number, f"{message}\n\n📞 للحصول على الأسعار: 0556914447")
    
    def send_welcome_menu_to_new_customer(self, to_number: str, customer_name: str = None) -> bool:
        """إرسال قائمة ترحيب نصية للعملاء الجدد"""
        if customer_name:
            welcome_message = f"""أهلاً وسهلاً أخونا {customer_name} الكريم مرة ثانية! 🌟

مرحباً بك في مكتب الركائز البشرية للاستقدام

📋 خدماتنا:
1️⃣ اكتب "عاملة منزلية" - للحصول على عاملة منزلية
2️⃣ اكتب "مربية أطفال" - لطلب مربية أطفال
3️⃣ اكتب "أسعار" - لعرض الأسعار والعروض
4️⃣ اكتب "تواصل" - للحصول على معلومات التواصل

📞 للتواصل المباشر:
• 0556914447
• 0506207444
• 0537914445

كيف يمكنني مساعدتك اليوم؟ 😊"""
        else:
            welcome_message = """أهلاً وسهلاً بك في مكتب الركائز البشرية للاستقدام! 🌟

📋 خدماتنا الرئيسية:
1️⃣ اكتب "عاملة منزلية" - للحصول على عاملة منزلية محترفة
2️⃣ اكتب "مربية أطفال" - لطلب مربية أطفال مدربة
3️⃣ اكتب "أسعار" - لعرض الأسعار والعروض الحالية
4️⃣ اكتب "تواصل" - للحصول على معلومات التواصل

📞 أرقام التواصل:
• 0556914447 (الخط الرئيسي)
• 0506207444 (خط الطوارئ)
• 0537914445 (خط المبيعات)

🕒 نحن في خدمتك من 8 صباحاً حتى 10 مساءً

كيف أستطيع مساعدتك؟ 😊"""
        
        return self.send_message(to_number, welcome_message)
    
    def handle_interactive_message(self, interactive_data: dict, phone_number: str) -> bool:
        """معالجة الردود التفاعلية - حالياً معطلة"""
        # نظراً لأن Interactive Messages غير مفعلة، سنرد برسالة نصية
        fallback_message = """عذراً، يبدو أن هناك مشكلة في النظام.

يمكنك الكتابة مباشرة:
• "عاملة منزلية" - للحصول على عاملة
• "مربية أطفال" - لطلب مربية
• "أسعار" - لعرض الأسعار
• "تواصل" - للتواصل معنا

أو اتصل بنا: 📞 0556914447"""
        
        return self.send_message(phone_number, fallback_message)
    
    def cleanup_processing_messages(self):
        """تنظيف دوري"""
        if len(self.processing_messages) > 1000:
            messages_list = list(self.processing_messages)
            for msg_id in messages_list[:500]:
                self.processing_messages.discard(msg_id)
            print(f"🧹 تم تنظيف ذاكرة الرسائل")
    
    def get_handler_stats(self) -> dict:
        """إحصائيات المعالج"""
        return {
            'processing_messages_count': len(self.processing_messages),
            'rate_limited_numbers': len(self.rate_limit),
            'interactive_menu_available': False,  # معطلة مؤقتاً
            'whatsapp_config_ready': bool(ACCESS_TOKEN)
        }