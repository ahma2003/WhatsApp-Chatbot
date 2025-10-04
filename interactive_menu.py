class InteractiveMenuHandler:
    """معالج القوائم - يستخدم رسائل نصية حالياً بدلاً من Interactive Messages"""
    
    def __init__(self, whatsapp_handler, quick_system):
        self.whatsapp_handler = whatsapp_handler
        self.quick_system = quick_system
        
    def send_main_menu(self, to_number: str) -> bool:
        """إرسال القائمة الرئيسية كرسالة نصية"""
        menu_text = """🏢 مكتب الركائز البشرية للاستقدام

أهلاً وسهلاً بك! 🌟

📋 اختر الخدمة المطلوبة بكتابة رقمها:

1️⃣ خدماتنا (عاملات منزليات، مربيات أطفال)
2️⃣ الأسعار والعروض الحالية
3️⃣ متطلبات الاستقدام والأوراق
4️⃣ تواصل معنا وأرقام الهواتف
5️⃣ تتبع حالة الطلب
6️⃣ الأسئلة الشائعة

📝 أو اكتب مباشرة:
• "عاملة منزلية" - للحصول على عاملة
• "مربية أطفال" - لطلب مربية
• "أسعار" - لعرض الأسعار

📞 اتصل الآن: 0556914447

كيف يمكنني مساعدتك؟"""
        
        return self.whatsapp_handler.send_message(to_number, menu_text)

    def send_services_menu(self, to_number: str) -> bool:
        """قائمة الخدمات"""
        services_text = """🏠 خدماتنا المتميزة

نوفر لك أفضل العمالة المنزلية:

🔹 عاملات منزليات محترفات
🔹 مربيات أطفال مدربات  
🔹 طباخات ماهرات
🔹 سائقين مؤهلين
🔹 عمال زراعة

✨ جميع العمالة مدربة ومؤهلة بأعلى المعايير

💬 للاستفسار اكتب:
• "عاملة منزلية" - للتفاصيل والأسعار
• "مربية أطفال" - لمربيات الأطفال
• "أسعار" - لجميع الأسعار

📞 أو اتصل: 0556914447"""
        
        return self.whatsapp_handler.send_message(to_number, services_text)

    def send_contact_menu(self, to_number: str) -> bool:
        """قائمة التواصل"""
        contact_text = """📞 تواصل معنا

يسعدنا تواصلك في أي وقت:

📱 أرقام الهواتف:
• 0556914447 (الخط الرئيسي)
• 0506207444 (خط الطوارئ)
• 0537914445 (خط المبيعات)

🕒 أوقات العمل:
السبت - الخميس: 8 ص - 10 م
الجمعة: 2 م - 10 م

📍 نحن في خدمتك دائماً!

💬 اكتب "مساعدة" للعودة للقائمة الرئيسية"""
        
        return self.whatsapp_handler.send_message(to_number, contact_text)

    # الدوال الباقية لا تُستخدم حالياً لأن Interactive Messages معطلة
    def send_button_message(self, *args, **kwargs):
        """معطلة - تتطلب Official Business Account"""
        return False

    def send_list_message(self, *args, **kwargs):
        """معطلة - تتطلب Official Business Account"""
        return False

    def handle_interactive_response(self, response_data: dict, phone_number: str) -> str:
        """معالجة الردود - حالياً معطلة"""
        return self.send_main_menu(phone_number)

    def handle_button_click(self, button_id: str, phone_number: str) -> str:
        """معالجة الأزرار - حالياً نصية"""
        if button_id == "domestic_worker" or "عاملة" in button_id.lower():
            text_response, image_url = self.quick_system.get_price_response()
            if image_url:
                self.whatsapp_handler.send_image_with_text(phone_number, text_response, image_url)
                return ""
            return text_response
            
        elif button_id == "nanny_service" or "مربية" in button_id.lower():
            return """👶 خدمة مربيات الأطفال

نوفر مربيات أطفال مدربات ومؤهلات:
• خبرة في رعاية الأطفال
• تدريب على السلامة والإسعافات
• مهارات تعليمية وترفيهية
• جنسيات متنوعة

للاستفسار عن الأسعار:
📞 0556914447"""
            
        elif "قائمة" in button_id or "menu" in button_id.lower():
            self.send_main_menu(phone_number)
            return ""
            
        elif "اتصال" in button_id or "call" in button_id.lower():
            return self.send_contact_menu(phone_number)

        return "شكراً لاهتمامك! 😊"

    def handle_list_selection(self, list_id: str, phone_number: str) -> str:
        """معالجة القوائم المنسدلة - حالياً نصية"""
        
        # التعامل مع الاختيارات الرقمية
        if list_id in ["1", "خدمات", "services_menu"]:
            self.send_services_menu(phone_number)
            return ""
            
        elif list_id in ["2", "أسعار", "prices_menu"]:
            text_response, image_url = self.quick_system.get_price_response()
            if image_url:
                self.whatsapp_handler.send_image_with_text(phone_number, text_response, image_url)
                return ""
            return text_response
            
        elif list_id in ["3", "متطلبات", "requirements_menu"]:
            return """📋 متطلبات الاستقدام

للحصول على عاملة منزلية:

✅ المستندات:
• صورة الهوية الوطنية
• صورة كشف حساب بنكي
• نموذج طلب الاستقدام
• عقد العمل

✅ الإجراءات:
• دفع المقدم (50%)
• اختيار العاملة
• متابعة الإجراءات الحكومية
• استلام العاملة (45-60 يوم)

للتفاصيل: 📞 0556914447"""
            
        elif list_id in ["4", "تواصل", "support_menu"]:
            self.send_contact_menu(phone_number)
            return ""
            
        elif list_id in ["5", "تتبع", "status_check"]:
            return """📊 تتبع حالة الطلب

للاستفسار عن طلبك:

1️⃣ اتصل: 0556914447
2️⃣ اذكر رقم العقد أو الهاتف
3️⃣ أو قل "تتبع طلبي"

⏰ التحديثات يومياً
📱 رسائل دورية"""

        elif list_id in ["6", "أسئلة", "faq_menu"]:
            return """❓ الأسئلة الشائعة

🔹 مدة الاستقدام؟
▫️ 45-60 يوم عمل

🔹 يوجد ضمان؟  
▫️ نعم، 3 أشهر شاملة

🔹 تغيير العاملة؟
▫️ نعم، مجاناً بفترة الضمان

🔹 طرق الدفع؟
▫️ نقداً أو تحويل بنكي

للمزيد: 📞 0556914447"""

        return "تم استلام طلبك! 😊"
