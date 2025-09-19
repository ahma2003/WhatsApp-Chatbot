class InteractiveMenuHandler:
    def __init__(self, whatsapp_handler, quick_system):
        self.whatsapp_handler = whatsapp_handler
        self.quick_system = quick_system
        
    def send_main_menu(self, to_number: str) -> bool:
        """إرسال القائمة الرئيسية التفاعلية"""
        return self.send_list_message(
            to_number=to_number,
            header_text="🏢 مكتب الركائز البشرية للاستقدام",
            body_text="""أهلاً وسهلاً بك في مكتب الركائز البشرية! 🌟

اختر الخدمة التي تحتاجها من القائمة أدناه:""",
            footer_text="نحن في خدمتك دائماً",
            button_text="اختر الخدمة",
            sections=[
                {
                    "title": "خدماتنا الأساسية",
                    "rows": [
                        {
                            "id": "services_menu",
                            "title": "🏠 خدماتنا",
                            "description": "عرض جميع الخدمات المتاحة"
                        },
                        {
                            "id": "prices_menu", 
                            "title": "💰 الأسعار والعروض",
                            "description": "اطلع على أحدث الأسعار والعروض"
                        },
                        {
                            "id": "requirements_menu",
                            "title": "📋 متطلبات الاستقدام", 
                            "description": "تعرف على الأوراق المطلوبة"
                        }
                    ]
                },
                {
                    "title": "الدعم والمساعدة",
                    "rows": [
                        {
                            "id": "support_menu",
                            "title": "💬 تواصل معنا",
                            "description": "طرق التواصل وأرقام الهواتف"
                        },
                        {
                            "id": "status_check",
                            "title": "📊 تتبع الطلب",
                            "description": "تابع حالة طلبك الحالي"
                        },
                        {
                            "id": "faq_menu",
                            "title": "❓ الأسئلة الشائعة",
                            "description": "إجابات على الاستفسارات المتكررة"
                        }
                    ]
                }
            ]
        )

    def send_services_menu(self, to_number: str) -> bool:
        """قائمة الخدمات المتاحة"""
        return self.send_button_message(
            to_number=to_number,
            header_text="🏠 خدماتنا المتميزة",
            body_text="""نوفر لك أفضل العمالة المنزلية المدربة والمؤهلة:

🔹 عاملات منزليات محترفات
🔹 مربيات أطفال مدربات  
🔹 طباخات ماهرات
🔹 سائقين مؤهلين
🔹 عمال زراعة

جميع العمالة مدربة ومؤهلة بأعلى المعايير""",
            footer_text="اختر نوع الخدمة التي تحتاجها",
            buttons=[
                {
                    "type": "reply",
                    "reply": {
                        "id": "domestic_worker",
                        "title": "🏠 عاملة منزلية"
                    }
                },
                {
                    "type": "reply", 
                    "reply": {
                        "id": "nanny_service",
                        "title": "👶 مربية أطفال"
                    }
                },
                {
                    "type": "reply",
                    "reply": {
                        "id": "back_main_menu",
                        "title": "🔙 القائمة الرئيسية"
                    }
                }
            ]
        )

    def send_contact_menu(self, to_number: str) -> bool:
        """قائمة التواصل"""
        return self.send_button_message(
            to_number=to_number,
            header_text="📞 تواصل معنا",
            body_text="""يسعدنا تواصلك معنا في أي وقت:

📱 الهواتف:
• 0556914447
• 0506207444  
• 0537914445

🕒 أوقات العمل:
السبت - الخميس: 8 ص - 10 م
الجمعة: 2 م - 10 م""",
            footer_text="اختر طريقة التواصل المفضلة",
            buttons=[
                {
                    "type": "reply",
                    "reply": {
                        "id": "call_now",
                        "title": "📞 اتصال مباشر"
                    }
                },
                {
                    "type": "reply",
                    "reply": {
                        "id": "whatsapp_chat", 
                        "title": "💬 واتساب"
                    }
                },
                {
                    "type": "reply",
                    "reply": {
                        "id": "back_main_menu",
                        "title": "🔙 القائمة الرئيسية"
                    }
                }
            ]
        )

    def send_button_message(self, to_number: str, header_text: str, body_text: str, 
                           footer_text: str, buttons: list) -> bool:
        """إرسال رسالة بأزرار تفاعلية"""
        if not self.whatsapp_handler.ACCESS_TOKEN or not self.whatsapp_handler.PHONE_NUMBER_ID:
            return False
            
        url = f"https://graph.facebook.com/v18.0/{self.whatsapp_handler.PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {self.whatsapp_handler.ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "header": {
                    "type": "text",
                    "text": header_text
                },
                "body": {
                    "text": body_text
                },
                "footer": {
                    "text": footer_text
                },
                "action": {
                    "buttons": buttons
                }
            }
        }
        
        try:
            import requests, json
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=8)
            response.raise_for_status()
            print(f"✅ تم إرسال القائمة التفاعلية إلى {to_number}")
            return True
        except Exception as e:
            print(f"❌ خطأ في إرسال القائمة التفاعلية: {e}")
            return False

    def send_list_message(self, to_number: str, header_text: str, body_text: str,
                         footer_text: str, button_text: str, sections: list) -> bool:
        """إرسال قائمة منسدلة تفاعلية"""
        if not self.whatsapp_handler.ACCESS_TOKEN or not self.whatsapp_handler.PHONE_NUMBER_ID:
            return False
            
        url = f"https://graph.facebook.com/v18.0/{self.whatsapp_handler.PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {self.whatsapp_handler.ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": header_text
                },
                "body": {
                    "text": body_text
                },
                "footer": {
                    "text": footer_text
                },
                "action": {
                    "button": button_text,
                    "sections": sections
                }
            }
        }
        
        try:
            import requests, json
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=8)
            response.raise_for_status()
            print(f"✅ تم إرسال القائمة المنسدلة إلى {to_number}")
            return True
        except Exception as e:
            print(f"❌ خطأ في إرسال القائمة المنسدلة: {e}")
            return False

    def handle_interactive_response(self, response_data: dict, phone_number: str) -> str:
        """معالجة ردود الأزرار والقوائم التفاعلية"""
        interactive_type = response_data.get('type')
        
        if interactive_type == 'button_reply':
            button_id = response_data.get('button_reply', {}).get('id')
            return self.handle_button_click(button_id, phone_number)
            
        elif interactive_type == 'list_reply':
            list_id = response_data.get('list_reply', {}).get('id')
            return self.handle_list_selection(list_id, phone_number)
            
        return "عذراً، لم أستطع فهم اختيارك. جرب مرة أخرى."

    def handle_button_click(self, button_id: str, phone_number: str) -> str:
        """معالجة النقر على الأزرار"""
        if button_id == "domestic_worker":
            # إرسال صورة الأسعار للعاملات المنزليات
            text_response, image_url = self.quick_system.get_price_response()
            if image_url:
                self.whatsapp_handler.send_image_with_text(phone_number, text_response, image_url)
                return ""
            return text_response
            
        elif button_id == "nanny_service":
            return """👶 خدمة مربيات الأطفال

نوفر مربيات أطفال مدربات ومؤهلات:
• تجربة في رعاية الأطفال
• تدريب على السلامة والإسعافات الأولية  
• مهارات تعليمية وترفيهية
• جنسيات متنوعة حسب طلبكم

للاستفسار عن الأسعار: 📞 0556914447"""
            
        elif button_id == "back_main_menu":
            self.send_main_menu(phone_number)
            return ""
            
        elif button_id == "call_now":
            return """📞 للتواصل المباشر اتصل على:

• 0556914447 (الخط الرئيسي)
• 0506207444 (خط الطوارئ)
• 0537914445 (خط المبيعات)

🕒 نحن في خدمتك من 8 صباحاً حتى 10 مساءً"""

        elif button_id == "whatsapp_chat":
            return """💬 أهلاً بك! أنت تتحدث معنا الآن عبر واتساب

يمكنك كتابة:
• "أسعار" - لعرض الأسعار
• "خدمات" - لعرض الخدمات  
• "مساعدة" - للحصول على المساعدة

أو اكتب أي استفسار وسنجيبك فوراً! 😊"""

        return "شكراً لاختيارك!"

    def handle_list_selection(self, list_id: str, phone_number: str) -> str:
        """معالجة اختيار من القائمة المنسدلة"""
        if list_id == "services_menu":
            self.send_services_menu(phone_number)
            return ""
            
        elif list_id == "prices_menu":
            text_response, image_url = self.quick_system.get_price_response()
            if image_url:
                self.whatsapp_handler.send_image_with_text(phone_number, text_response, image_url)
                return ""
            return text_response
            
        elif list_id == "support_menu":
            self.send_contact_menu(phone_number)
            return ""
            
        elif list_id == "requirements_menu":
            return """📋 متطلبات الاستقدام

للحصول على عاملة منزلية تحتاج إلى:

✅ المستندات المطلوبة:
• صورة الهوية الوطنية
• صورة كشف حساب بنكي
• نموذج طلب الاستقدام
• عقد العمل

✅ الإجراءات:
• دفع المقدم (50%)
• اختيار العاملة المناسبة
• متابعة الإجراءات الحكومية
• استلام العاملة خلال 45-60 يوم

للتفاصيل أكثر: 📞 0556914447"""

        elif list_id == "status_check":
            return """📊 تتبع حالة الطلب

للاستفسار عن حالة طلبك:

1️⃣ اتصل على: 0556914447
2️⃣ اكتب رقم العقد أو رقم الهاتف
3️⃣ أو قل "تتبع طلبي" وسنساعدك

⏰ يتم تحديث حالة الطلبات يومياً
📱 ستصلك رسائل تحديث دورية"""

        elif list_id == "faq_menu":
            return """❓ الأسئلة الشائعة

🔹 كم مدة الاستقدام؟
▫️ عادة 45-60 يوم عمل

🔹 هل يوجد ضمان؟  
▫️ نعم، ضمان شامل لمدة 3 أشهر

🔹 هل يمكن تغيير العاملة؟
▫️ نعم، خلال فترة الضمان مجاناً

🔹 ما هي طرق الدفع؟
▫️ نقداً أو تحويل بنكي

للمزيد: 📞 0556914447"""

        return "تم استلام اختيارك!"
