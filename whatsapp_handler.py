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
        self.last_send_time = {}
        
        self.ACCESS_TOKEN = ACCESS_TOKEN
        self.PHONE_NUMBER_ID = PHONE_NUMBER_ID
        
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
    
    def _wait_before_send(self, to_number: str):
        """انتظار بين الرسائل لتجنب Rate Limiting من 360Dialog"""
        now = time.time()
        if to_number in self.last_send_time:
            time_since_last = now - self.last_send_time[to_number]
            if time_since_last < 1.5:
                wait_time = 1.5 - time_since_last
                print(f"⏳ انتظار {wait_time:.1f}s قبل الإرسال إلى {to_number}")
                time.sleep(wait_time)
        self.last_send_time[to_number] = time.time()
    
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
        """إرسال رسالة نصية عبر 360dialog مع معالجة Rate Limiting"""
        if not ACCESS_TOKEN:
            print("❌ ACCESS_TOKEN غير موجود")
            return False
        
        self._wait_before_send(to_number)
        
        url = "https://waba-v2.360dialog.io/messages"
        
        headers = {
            "D360-API-KEY": ACCESS_TOKEN,
            "Content-Type": "application/json"
        }
        
        message = message.strip()
        if len(message) > 900:
            message = message[:850] + "...\n\nللمزيد: 📞 0556914447"
        
        payload = json.dumps({
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "text",
            "text": {
                "body": message
            }
        })
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
                
                if response.status_code == 201 or response.status_code == 200:
                    print(f"✅ تم الإرسال إلى {to_number}")
                    return True
                elif response.status_code == 555:
                    print(f"⚠️ خطأ 555 - محاولة {attempt + 1}/{max_retries}")
                    if attempt < max_retries - 1:
                        time.sleep(2 * (attempt + 1))
                        continue
                else:
                    print(f"❌ خطأ {response.status_code}: {response.text}")
                    response.raise_for_status()
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ خطأ في المحاولة {attempt + 1}: {e}")
                if hasattr(e, 'response') and e.response:
                    print(f"📄 تفاصيل: {e.response.text}")
                
                if attempt < max_retries - 1:
                    time.sleep(2 * (attempt + 1))
                    continue
                    
        return False
    
    def send_image_with_text(self, to_number: str, message: str, image_url: str) -> bool:
        """إرسال صورة مع نص"""
        if not ACCESS_TOKEN:
            return False
        
        self._wait_before_send(to_number)
        
        url = "https://waba-v2.360dialog.io/messages"
        
        headers = {
            "D360-API-KEY": ACCESS_TOKEN,
            "Content-Type": "application/json"
        }
        
        if len(message) > 800:
            message = message[:750] + "...\n📞 للمزيد: 0556914447"
        
        payload = json.dumps({
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "image",
            "image": {
                "link": image_url,
                "caption": message
            }
        })
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
                
                if response.status_code == 201 or response.status_code == 200:
                    print(f"✅ تم إرسال الصورة إلى {to_number}")
                    return True
                else:
                    print(f"❌ خطأ {response.status_code}: {response.text}")
                    response.raise_for_status()
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ خطأ في إرسال الصورة: {e}")
                if attempt == max_retries - 1:
                    return self.send_message(to_number, f"{message}\n\n📞 للحصول على الأسعار: 0556914447")
                time.sleep(2)
                
        return False
    
    def send_welcome_menu_to_new_customer(self, to_number: str, customer_name: str = None) -> bool:
        """إرسال ترحيب بسيط للعملاء"""
        if customer_name:
            welcome_message = f"""أهلاً وسهلاً أخونا {customer_name} الكريم مرة ثانية في مكتب الركائز البشرية! 🌟

كيف يمكنني مساعدتك اليوم؟

📝 يمكنك الكتابة مباشرة:
• "عاملة منزلية" - للحصول على عاملة
• "مربية أطفال" - لطلب مربية  
• "أسعار" - لعرض الأسعار
• "مساعدة" - للقائمة الكاملة

📞 أو اتصل: 0556914447"""
        else:
            welcome_message = """أهلاً وسهلاً بك في مكتب الركائز البشرية للاستقدام! 🌟

📝 يمكنك الكتابة:
• "عاملة منزلية" - للحصول على عاملة محترفة
• "مربية أطفال" - لطلب مربية مدربة
• "أسعار" - لعرض الأسعار والعروض
• "تواصل" - للحصول على أرقام التواصل
• "مساعدة" - للقائمة الكاملة

📞 اتصل الآن: 0556914447

كيف أستطيع مساعدتك؟ 😊"""
        
        return self.send_message(to_number, welcome_message)
    
    def handle_interactive_message(self, interactive_data: dict, phone_number: str) -> bool:
        """معالجة الردود التفاعلية"""
        fallback_message = """يمكنك الكتابة مباشرة:
• "عاملة منزلية" - للحصول على عاملة
• "مربية أطفال" - لطلب مربية
• "أسعار" - لعرض الأسعار
• "مساعدة" - للقائمة الكاملة

أو اتصل: 📞 0556914447"""
        
        return self.send_message(phone_number, fallback_message)
    
    def cleanup_processing_messages(self):
        """تنظيف دوري"""
        if len(self.processing_messages) > 1000:
            messages_list = list(self.processing_messages)
            for msg_id in messages_list[:500]:
                self.processing_messages.discard(msg_id)
            print(f"🧹 تم تنظيف ذاكرة الرسائل")
        
        if len(self.last_send_time) > 100:
            numbers = list(self.last_send_time.keys())
            for num in numbers[:-50]:
                del self.last_send_time[num]
    
    def get_handler_stats(self) -> dict:
        """إحصائيات المعالج"""
        return {
            'processing_messages_count': len(self.processing_messages),
            'rate_limited_numbers': len(self.rate_limit),
            'tracked_numbers': len(self.last_send_time),
            'interactive_menu_available': False,
            'whatsapp_config_ready': bool(ACCESS_TOKEN)
        }