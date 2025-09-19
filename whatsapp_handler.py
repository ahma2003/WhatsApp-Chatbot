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
        
        # إضافة هذه المتغيرات للوصول من InteractiveMenuHandler
        self.ACCESS_TOKEN = ACCESS_TOKEN
        self.PHONE_NUMBER_ID = PHONE_NUMBER_ID
        
        # إضافة معالج القوائم التفاعلية
        self.interactive_menu = InteractiveMenuHandler(self, quick_system)
    
    def is_duplicate_message(self, message_id: str) -> bool:
        """فحص الرسائل المكررة"""
        if message_id in self.processing_messages:
            return True
        self.processing_messages.add(message_id)
        
        # إزالة المعالجة بعد 30 ثانية
        threading.Timer(30.0, lambda: self.processing_messages.discard(message_id)).start()
        return False
    
    def check_rate_limit(self, phone_number: str) -> bool:
        """فحص معدل سريع - رسالة كل 0.5 ثانية"""
        now = time.time()
        if phone_number in self.rate_limit:
            if now - self.rate_limit[phone_number] < 0.5:
                return True
        self.rate_limit[phone_number] = now
        return False
    
    def should_show_main_menu(self, user_message: str) -> bool:
        """فحص إذا كانت الرسالة تستدعي عرض القائمة الرئيسية"""
        menu_triggers = [
            'مساعدة', 'help', 'قائمة', 'menu', 'خيارات', 'options',
            'خدمات', 'services', 'البداية', 'start', 'الرئيسية', 'home',
            'مساعده', 'القائمة', 'القايمة', 'الخدمات', 'خدماتكم'
        ]
        
        message_clean = user_message.lower().strip()
        
        # فحص الكلمات المفردة
        for trigger in menu_triggers:
            if trigger in message_clean:
                return True
                
        # فحص إذا كانت الرسالة قصيرة ومحتملة أن تكون طلب مساعدة
        if len(message_clean) <= 15 and any(word in message_clean for word in ['مساعد', 'ساعد', 'خدم', 'قائم']):
            return True
            
        return False
    
    def send_message(self, to_number: str, message: str) -> bool:
        """إرسال رسالة سريع"""
        if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
            print("❌ معلومات WhatsApp غير مكتملة")
            return False
            
        url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        message = message.strip()
        if len(message) > 900:
            message = message[:850] + "...\n\nللمزيد: 📞 0556914447"
        
        data = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "text": {"body": message}
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=5)
            response.raise_for_status()
            print(f"✅ تم الإرسال إلى {to_number}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ خطأ WhatsApp: {e}")
            return False
    
    def send_image_with_text(self, to_number: str, message: str, image_url: str) -> bool:
        """إرسال صورة مع رسالة"""
        if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
            return False
            
        url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # رسالة مختصرة للـ caption
        if len(message) > 800:
            message = message[:750] + "...\n📞 للمزيد: 0556914447"
        
        data = {
            "messaging_product": "whatsapp",
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
            # رد احتياطي بالنص فقط
            return self.send_message(to_number, f"{message}\n\n📞 اتصل للحصول على صورة الأسعار: 0556914447")
    
    def send_welcome_menu_to_new_customer(self, to_number: str, customer_name: str = None) -> bool:
        """إرسال قائمة ترحيبية للعملاء الجدد"""
        if customer_name:
            welcome_text = f"""أهلاً وسهلاً أخونا {customer_name} الكريم مرة ثانية! 🌟

مرحباً بك في مكتب الركائز البشرية للاستقدام

يمكنك استخدام القائمة أدناه للوصول السريع لخدماتنا:"""
        else:
            welcome_text = """أهلاً وسهلاً بك في مكتب الركائز البشرية للاستقدام! 🌟

نحن هنا لخدمتك في جميع احتياجاتك من العمالة المنزلية المدربة

استخدم القائمة أدناه للحصول على ما تحتاجه:"""
        
        # إرسال رسالة ترحيب أولاً
        self.send_message(to_number, welcome_text)
        
        # ثم إرسال القائمة التفاعلية
        time.sleep(1)  # توقف قصير بين الرسائل
        return self.interactive_menu.send_main_menu(to_number)
    
    def handle_interactive_message(self, interactive_data: dict, phone_number: str) -> bool:
        """معالجة الرسائل التفاعلية (الأزرار والقوائم)"""
        try:
            response = self.interactive_menu.handle_interactive_response(interactive_data, phone_number)
            
            if response:  # إذا كان هناك رد نصي
                return self.send_message(phone_number, response)
            
            # إذا لم يكن هناك رد (مثل إرسال قائمة جديدة)
            return True
            
        except Exception as e:
            print(f"❌ خطأ في معالجة الرسالة التفاعلية: {e}")
            fallback_message = """عذراً، حدث خطأ في معالجة اختيارك.

يمكنك:
• كتابة "مساعدة" لعرض القائمة مرة أخرى
• أو الاتصال بنا: 📞 0556914447"""
            return self.send_message(phone_number, fallback_message)
    
    def cleanup_processing_messages(self):
        """تنظيف دوري لذاكرة معالجة الرسائل"""
        if len(self.processing_messages) > 1000:
            # احتفظ بآخر 500 رسالة فقط
            messages_list = list(self.processing_messages)
            for msg_id in messages_list[:500]:
                self.processing_messages.discard(msg_id)
            print(f"🧹 تم تنظيف ذاكرة الرسائل: {len(messages_list[:500])} رسالة")
    
    def get_handler_stats(self) -> dict:
        """إحصائيات معالج الواتساب"""
        return {
            'processing_messages_count': len(self.processing_messages),
            'rate_limited_numbers': len(self.rate_limit),
            'interactive_menu_available': self.interactive_menu is not None,
            'whatsapp_config_ready': bool(ACCESS_TOKEN and PHONE_NUMBER_ID)
        }