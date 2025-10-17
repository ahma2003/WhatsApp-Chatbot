import random

class QuickResponseSystem:
    def __init__(self):
        # ردود الترحيب السريعة
        self.welcome_patterns = {
            'سلام': True, 'السلام': True, 'عليكم': True,
            'مرحبا': True, 'مرحبتين': True, 'هلا': True, 'اهلا': True,
            'كيفك': True, 'كيف الحال': True, 'شلونك': True, 'وش اخبارك': True,
            'صباح': True, 'مساء': True, 'اهلين': True, 'حياك': True, 'حياكم': True,
            'يعطيك العافية': True, 'تسلم': True, 'الله يعطيك العافية': True,
            'هاي': True, 'هالو': True, 'hello': True, 'hi': True,
            'good morning': True, 'good evening': True,
            'ايش اخبارك': True, 'وش مسوي': True, 'كيف امورك': True
        }
        
        # كلمات وعبارات الشكر بالهجة السعودية
        self.thanks_patterns = {
            'شكرا': True, 'شكراً': True, 'شكر': True, 'مشكور': True, 'مشكوره': True,
            'تسلم': True, 'تسلمي': True, 'تسلمين': True, 'تسلمون': True,
            'يعطيك': True, 'يعطيكم': True, 'الله يعطيك': True, 'الله يعطيكم': True,
            'العافية': True, 'يعطيك العافية': True, 'الله يعطيك العافية': True,
            'جزاك': True, 'جزاكم': True, 'جزاك الله': True, 'جزاكم الله': True,
            'خيراً': True, 'خير': True, 'جزاك الله خير': True, 'جزاك الله خيرا': True,
            'ماقصرت': True, 'ماقصرتوا': True, 'ما قصرت': True, 'ما قصرتوا': True,
            'مشكورين': True, 'مشكورات': True, 'thank': True, 'thanks': True,
            'appreciate': True, 'بارك': True, 'بارك الله': True, 'الله يبارك': True,
            'وفقك': True, 'وفقكم': True, 'الله يوفقك': True, 'الله يوفقكم': True,
            'كثر خيرك': True, 'كثر خيركم': True, 'الله يكثر خيرك': True, 
            'خلاص': True, 'كفايه': True, 'كافي': True, 'بس كذا': True,
            'تمام': True, 'زين': True, 'ممتاز': True, 'perfect': True
        }
        
        # جمل كاملة للشكر بالهجة السعودية
        self.thanks_phrases = [
            'شكرا لك', 'شكرا ليك', 'شكراً لك', 'شكراً ليك',
            'الله يعطيك العافية', 'يعطيك العافية', 'الله يعطيكم العافية',
            'تسلم إيدك', 'تسلم ايدك', 'تسلمي إيدك', 'تسلمي ايدك',
            'جزاك الله خير', 'جزاك الله خيرا', 'جزاك الله خيراً',
            'الله يجزاك خير', 'الله يجزيك خير', 'الله يجزيكم خير',
            'ما قصرت', 'ماقصرت', 'ما قصرتوا', 'ماقصرتوا',
            'كثر خيرك', 'الله يكثر خيرك', 'كثر خيركم',
            'الله يوفقك', 'الله يوفقكم', 'وفقك الله', 'وفقكم الله',
            'بارك الله فيك', 'بارك الله فيكم', 'الله يبارك فيك',
            'شكرا على المساعدة', 'شكرا على المساعده', 'شكراً على المساعدة',
            'thanks a lot', 'thank you', 'thank u', 'appreciate it',
            'مشكورين والله', 'مشكور والله', 'تسلم والله'
        ]
        
        # كلمات دلالية للأسعار
        self.price_keywords = [
            'سعر', 'اسعار', 'أسعار', 'كلفة', 'اسعاركم',
            'ريال', 'مبلغ', 'عروضكم',
            'عرض', 'عروض', 'باقة', 'باقات', 'خصم', 'خصومات', 'خصوماتكم',
            'ثمن', 'مصاريف', 'مصروف', 'دفع', 'بكام'
        ]
        
        # جمل كاملة للأسعار
        self.price_phrases = [
            'كم السعر', 'ايش السعر', 'وش السعر', 'ايش اسعاركم',
            'ايش الكلفة', 'وش الكلفة',
            'كم التكاليف',    
            'كم الثمن', 'ابغى اعرف السعر',
            'عايز اعرف السعر', 'ايه الاسعار', 'وش الاسعار',
            'اسعار الاستقدام'
        ]
    
    def _check_gender(self, gender: str) -> str:
        """
        دالة محسّنة للتحقق من الجنس
        
        Args:
            gender: الجنس من قاعدة البيانات ("ذكر" أو "أنثى")
            
        Returns:
            str: "female" إذا كانت أنثى، "male" إذا كان ذكر، أو None إذا غير محدد
        """
        if not gender:
            return None
        
        gender_str = str(gender).strip()
        
        # التحقق المباشر من القيم المتوقعة
        if gender_str == "أنثى":
            return "female"
        elif gender_str == "ذكر":
            return "male"
        
        # في حالة وجود قيم أخرى (احتياطي)
        gender_lower = gender_str.lower()
        
        female_values = [
            'female', 'f', 
            'أنثى', 'انثى', 'أنثي', 'انثي',
            'بنت', 'مرأة', 'امرأة', 'سيدة',
            'woman', 'girl', 'lady'
        ]
        
        male_values = [
            'male', 'm',
            'ذكر', 'ذكور',
            'رجل', 'شاب',
            'man', 'boy'
        ]
        
        if gender_lower in female_values:
            return "female"
        elif gender_lower in male_values:
            return "male"
        
        return None
    
    def is_greeting_message(self, message: str) -> bool:
        """فحص سريع للرسائل الترحيبية"""
        if not message or len(message.strip()) == 0:
            return False
            
        message_clean = message.lower().strip()
        words = message_clean.split()
        
        if len(words) <= 6:
            for word in words:
                clean_word = ''.join(c for c in word if c.isalnum() or c in 'أابتثجحخدذرزسشصضطظعغفقكلمنهويىءآإ')
                if clean_word in self.welcome_patterns:
                    return True
                    
        return False
    
    def is_thanks_message(self, message: str) -> bool:
        """فحص سريع ودقيق لرسائل الشكر بالهجة السعودية"""
        if not message or len(message.strip()) == 0:
            return False
            
        message_clean = message.lower().strip()
        
        # فحص الجمل الكاملة أولاً
        for phrase in self.thanks_phrases:
            if phrase in message_clean:
                return True
        
        # فحص الكلمات المفردة
        words = message_clean.split()
        thanks_word_count = 0
        
        for word in words:
            clean_word = ''.join(c for c in word if c.isalnum() or c in 'أابتثجحخدذرزسشصضطظعغفقكلمنهويىءآإ')
            
            if clean_word in self.thanks_patterns:
                thanks_word_count += 1
        
        return thanks_word_count >= 1
    
    def is_price_inquiry(self, message: str) -> bool:
        """فحص سريع ودقيق للسؤال عن الأسعار"""
        if not message or len(message.strip()) == 0:
            return False
            
        message_clean = message.lower().strip()
        
        # فحص الجمل الكاملة أولاً
        for phrase in self.price_phrases:
            if phrase in message_clean:
                return True
        
        # فحص الكلمات المفردة
        words = message_clean.split()
        price_word_count = 0
        
        for word in words:
            clean_word = ''.join(c for c in word if c.isalnum() or c in 'أابتثجحخدذرزسشصضطظعغفقكلمنهويىءآإ')
            
            if clean_word in self.price_keywords:
                price_word_count += 1
        
        return price_word_count >= 1
    
    def get_welcome_response(self, customer_name: str = None, gender: str = None) -> str:
        """
        رد الترحيب السريع مع تحديد النوع
        
        Args:
            customer_name: اسم العميل (اختياري)
            gender: نوع العميل ('ذكر' أو 'أنثى') (اختياري)
        
        Returns:
            str: رسالة الترحيب المخصصة
        """
        # استخدام الدالة المحسّنة للتحقق من الجنس
        gender_type = self._check_gender(gender)
        
        # طباعة للتأكد من التعرف الصحيح
        print(f"🔍 Gender Check: '{gender}' -> type={gender_type}, name={customer_name}")
        
        # رد مخصص للعملاء المسجلين
        if customer_name:
            if gender_type == "female":
                return f"""أهلاً وسهلاً أختنا {customer_name} الكريمة مرة ثانية 🌟

حياك الله مرة ثانية في مكتب الركائز البشرية للاستقدام

كيف يمكنني مساعدتك اليوم؟ 😊

📝 يمكنك الكتابة مباشرة:
• "عاملة منزلية" - للحصول على عاملة
• "مربية أطفال" - لطلب مربية  
• "أسعار" - لعرض الأسعار
• "مساعدة" - للقائمة الكاملة

📞 أو اتصلي: 0556914447"""
            elif gender_type == "male":
                return f"""أهلاً وسهلاً أخونا {customer_name} الكريم مرة ثانية 🌟

حياك الله مرة ثانية في مكتب الركائز البشرية للاستقدام

كيف يمكنني مساعدتك اليوم؟ 😊

📝 يمكنك الكتابة مباشرة:
• "عاملة منزلية" - للحصول على عاملة
• "مربية أطفال" - لطلب مربية  
• "أسعار" - لعرض الأسعار
• "مساعدة" - للقائمة الكاملة

📞 أو اتصل: 0556914447"""
        
        # رد عام للعملاء الجدد
        return """أهلاً وسهلاً بك في مكتب الركائز البشرية للاستقدام 🌟

نحن هنا لخدمتك ومساعدتك في جميع احتياجاتك من العمالة المنزلية المدربة والمؤهلة.

كيف يمكنني مساعدتك اليوم؟ 😊

📝 يمكنك الكتابة مباشرة:
• "عاملة منزلية" - للحصول على عاملة
• "مربية أطفال" - لطلب مربية  
• "أسعار" - لعرض الأسعار
• "مساعدة" - للقائمة الكاملة

📞 أو اتصل: 0556914447"""

    def get_thanks_response(self, customer_name: str = None, gender: str = None) -> str:
        """
        رد الشكر السريع بالهجة السعودية مع تحديد النوع
        
        Args:
            customer_name: اسم العميل (اختياري)
            gender: نوع العميل ('ذكر' أو 'أنثى') (اختياري)
        
        Returns:
            str: رسالة شكر مخصصة
        """
        # استخدام الدالة المحسّنة للتحقق من الجنس
        gender_type = self._check_gender(gender)
        
        # طباعة للتأكد من التعرف الصحيح
        print(f"🔍 Gender Check (Thanks): '{gender}' -> type={gender_type}, name={customer_name}")
        
        # ردود مخصصة للإناث
        if customer_name and gender_type == "female":
            responses = [
                f"""العفو أختنا {customer_name} الكريمة 🌟

الله يعطيك العافية.. نحن في خدمتك دائماً في مكتب الركائز البشرية

هل تحتاجين أي مساعدة أخرى؟ 😊""",
                
                f"""أهلاً وسهلاً أختنا {customer_name}.. هذا واجبنا 🤝

نحن سعداء بخدمتك في مكتب الركائز البشرية للاستقدام

الله يوفقك.. ولا تترددي في التواصل معنا متى شئتي! 💙""",
                
                f"""حياك الله أختنا {customer_name}.. ما قصرنا شي 🌟

خدمتك شرف لنا في مكتب الركائز البشرية

تواصلي معنا في أي وقت.. نحن هنا لخدمتك! 📞"""
            ]
        # ردود مخصصة للذكور
        elif customer_name and gender_type == "male":
            responses = [
                f"""العفو أخونا {customer_name} الكريم 🌟

الله يعطيك العافية.. نحن في خدمتك دائماً في مكتب الركائز البشرية

هل تحتاج أي مساعدة أخرى؟ 😊""",
                
                f"""أهلاً وسهلاً أخونا {customer_name}.. هذا واجبنا 🤝

نحن سعداء بخدمتك في مكتب الركائز البشرية للاستقدام

الله يوفقك.. ولا تتردد في التواصل معنا متى شئت! 💙""",
                
                f"""حياك الله أخونا {customer_name}.. ما قصرنا شي 🌟

خدمتك شرف لنا في مكتب الركائز البشرية

تواصل معنا في أي وقت.. نحن هنا لخدمتك! 📞"""
            ]
        # ردود عامة بدون اسم
        else:
            responses = [
                """العفو عميلنا العزيز 🌟

الله يعطيك العافية.. نحن في خدمتك دائماً في مكتب الركائز البشرية

هل تحتاج أي مساعدة أخرى؟ 😊""",
                
                """أهلاً وسهلاً.. هذا واجبنا 🤝

نحن سعداء بخدمتك في مكتب الركائز البشرية للاستقدام

الله يوفقك.. ولا تتردد في التواصل معنا متى شئت! 💙""",
                
                """حياك الله.. ما قصرنا شي 🌟

خدمتك شرف لنا في مكتب الركائز البشرية

تواصل معنا في أي وقت.. نحن هنا لخدمتك! 📞"""
            ]
        
        return random.choice(responses)

    def get_price_response(self) -> tuple:
        """رد الأسعار المختصر مع الصورة"""
        text_response = """إليك عروضنا الحالية للعمالة المنزلية المدربة 💼

🎉 عرض خاص بمناسبة اليوم الوطني السعودي 95

للاستفسار والحجز اتصل بنا:
📞 0556914447 / 0506207444 / 0537914445"""
        
        image_url = "https://i.imghippo.com/files/La2232xjc.jpg"
        
        return text_response, image_url