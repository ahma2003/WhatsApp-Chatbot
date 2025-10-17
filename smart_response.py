class SmartResponseGenerator:
    def __init__(self, openai_client, retriever, quick_system, customer_memory):
        self.openai_client = openai_client
        self.retriever = retriever
        self.quick_system = quick_system
        self.customer_memory = customer_memory
    
    def generate_response(self, user_message: str, phone_number: str, is_first: bool) -> tuple:
        """إنتاج الرد الذكي مع الذاكرة الشخصية"""
        
        print(f"🔍 معالجة: '{user_message}' من {phone_number}")
        
        # جلب معلومات العميل من الذاكرة (مع الجنس)
        customer_info = self.customer_memory.get_customer_info(phone_number)
        customer_name = customer_info.get('name', '') if customer_info else None
        customer_gender = customer_info.get('gender', '') if customer_info else None
        
        # 1. أولوية عليا للترحيب (مع التخصيص حسب الجنس)
        if self.quick_system.is_greeting_message(user_message):
            print(f"⚡ رد ترحيب فوري مخصص")
            response = self.quick_system.get_welcome_response(customer_name, customer_gender)
            self.customer_memory.add_conversation_message(phone_number, user_message, response)
            return response, False, None
        
        # 2. أولوية عليا للشكر (مع التخصيص حسب الجنس)
        if self.quick_system.is_thanks_message(user_message):
            print(f"🙏 رد شكر فوري مخصص")
            response = self.quick_system.get_thanks_response(customer_name, customer_gender)
            self.customer_memory.add_conversation_message(phone_number, user_message, response)
            return response, False, None
        
        # 3. أولوية عليا للأسعار
        if self.quick_system.is_price_inquiry(user_message):
            print(f"💰 طلب أسعار مكتشف")
            text_response, image_url = self.quick_system.get_price_response()
            self.customer_memory.add_conversation_message(phone_number, user_message, text_response)
            return text_response, True, image_url
        
        # 4. الردود العادية (ذكية مع الذاكرة)
        print(f"🤔 معالجة عادية مع ذاكرة شخصية")
        
        # بحث سريع في قاعدة البيانات
        retrieved_data, confidence_score = self.retriever.retrieve_best_matches(user_message) if self.retriever else ([], 0)
        
        # إذا لم يكن هناك OpenAI
        if not self.openai_client:
            if retrieved_data:
                response = f"بناءً على معلوماتنا:\n\n{retrieved_data[0]['answer']}\n\nهل يمكنني مساعدتك في شيء آخر؟"
            else:
                # تخصيص الرد حسب الجنس
                if customer_name:
                    if customer_gender and customer_gender.lower() in ['female', 'أنثى', 'انثى', 'f', 'انثي', 'أنثي']:
                        response = f"أهلاً بك مرة ثانية أختنا {customer_name} الكريمة في مكتب الركائز البشرية! 🌟\nسيتواصل معك أحد موظفينا قريباً للمساعدة.\n\nهل تريدين معرفة أسعارنا الحالية؟"
                    else:
                        response = f"أهلاً بك مرة ثانية أخونا {customer_name} الكريم في مكتب الركائز البشرية! 🌟\nسيتواصل معك أحد موظفينا قريباً للمساعدة.\n\nهل تريد معرفة أسعارنا الحالية؟"
                else:
                    response = "أهلاً بك في مكتب الركائز البشرية! 🌟\nسيتواصل معك أحد موظفينا قريباً للمساعدة.\n\nهل تريد معرفة أسعارنا الحالية؟"
            
            self.customer_memory.add_conversation_message(phone_number, user_message, response)
            return response, False, None
        
        try:
            # إنشاء رد ذكي مع الذاكرة الشخصية
            context = self.generate_context_string(retrieved_data)
            conversation_context = self.customer_memory.get_conversation_context(phone_number)
            customer_summary = self.customer_memory.create_customer_summary(customer_info)
            
            # تحديد نوع الترحيب حسب العميل والجنس
            if is_first and customer_name:
                if customer_gender and customer_gender.lower() in ['female', 'أنثى', 'انثى', 'f', 'انثي', 'أنثي']:
                    greeting = f"أهلاً وسهلاً أختنا {customer_name} الكريمة مرة ثانية في مكتب الركائز البشرية للاستقدام! 🌟\n\n"
                else:
                    greeting = f"أهلاً وسهلاً أخونا {customer_name} الكريم مرة ثانية في مكتب الركائز البشرية للاستقدام! 🌟\n\n"
            elif is_first:
                greeting = "أهلاً وسهلاً بك في مكتب الركائز البشرية للاستقدام! 🌟\n\n"
            else:
                greeting = ""
                
            system_prompt = f"""{greeting}أنت مساعد ذكي لمكتب الركائز البشرية للاستقدام.

معلومات العميل:
{customer_summary}

آخر محادثات:
{conversation_context}

أجب بشكل مختصر وودود من المعلومات المتوفرة فقط.
استخدم عبارات: عميلنا الكريم، حياك الله، يسعدنا خدمتك.
إذا كان العميل له تعامل سابق، أشر إليه بلطف.
اختتم بسؤال لتشجيع الحوار.

السؤال: {user_message}
المعلومات: {context}"""

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=700,
                temperature=0.1
            )
            
            bot_response = response.choices[0].message.content.strip()
            
            # إضافة المحادثة للذاكرة
            self.customer_memory.add_conversation_message(phone_number, user_message, bot_response)
            
            return bot_response, False, None
            
        except Exception as e:
            print(f"❌ خطأ في OpenAI: {e}")
            # رد احتياطي سريع مع التخصيص حسب الجنس
            if retrieved_data:
                if customer_name:
                    if customer_gender and customer_gender.lower() in ['female', 'أنثى', 'انثى', 'f', 'انثي', 'أنثي']:
                        response = f"عميلتنا الكريمة أختنا {customer_name}، بناءً على خبرتنا:\n\n{retrieved_data[0]['answer']}\n\nللمزيد من المساعدة، اتصلي بنا: 📞 0556914447"
                    else:
                        response = f"عميلنا الكريم أخونا {customer_name}، بناءً على خبرتنا:\n\n{retrieved_data[0]['answer']}\n\nللمزيد من المساعدة، اتصل بنا: 📞 0556914447"
                else:
                    response = f"عميلنا العزيز، بناءً على خبرتنا:\n\n{retrieved_data[0]['answer']}\n\nللمزيد من المساعدة، اتصل بنا: 📞 0556914447"
            else:
                if customer_name:
                    if customer_gender and customer_gender.lower() in ['female', 'أنثى', 'انثى', 'f', 'انثي', 'أنثي']:
                        response = f"أهلاً أختنا {customer_name} الكريمة! 🌟 سيتواصل معك أحد متخصصينا قريباً.\n\nهل تريدين معرفة عروضنا الحالية؟"
                    else:
                        response = f"أهلاً أخونا {customer_name} الكريم! 🌟 سيتواصل معك أحد متخصصينا قريباً.\n\nهل تريد معرفة عروضنا الحالية؟"
                else:
                    response = "أهلاً بك! 🌟 سيتواصل معك أحد متخصصينا قريباً.\n\nهل تريد معرفة عروضنا الحالية؟"
            
            self.customer_memory.add_conversation_message(phone_number, user_message, response)
            return response, False, None
    
    def generate_context_string(self, retrieved_data):
        """إنشاء سياق مختصر"""
        if not retrieved_data:
            return "لا توجد معلومات محددة."
        
        # أول نتيجة فقط للسرعة
        item = retrieved_data[0]
        return f"السؤال: {item['question']}\nالإجابة: {item['answer']}"