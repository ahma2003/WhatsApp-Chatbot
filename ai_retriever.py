from typing import List, Tuple, Optional
from openai_embeddings import OpenAIEmbeddingsManager

class EnhancedRetriever:
    def __init__(self, customer_memory):
        self.customer_memory = customer_memory
        self.embeddings_manager = OpenAIEmbeddingsManager(customer_memory)
        self.high_confidence_threshold = 0.75
        
        # قاعدة بيانات الأسئلة الشائعة (مدمجة في الكود للسرعة)
        self.frequent_qa = [
            {
                "question": "كم سعر العاملة المنزلية؟",
                "answer": "أسعار العمالة المنزلية تختلف حسب الجنسية والخبرة. لدينا عروض حالية بأسعار مميزة. للحصول على آخر الأسعار والعروض اتصل بنا على 0556914447",
                "keywords": ["سعر", "عاملة", "منزلية", "تكلفة", "أسعار"]
            },
            {
                "question": "كم مدة الاستقدام؟",
                "answer": "مدة الاستقدام عادة من 45-60 يوم عمل، وقد تختلف حسب الجنسية وإجراءات السفارة. نحرص على إنجاز المعاملات في أسرع وقت ممكن.",
                "keywords": ["مدة", "استقدام", "وقت", "كم", "يوم"]
            },
            {
                "question": "هل يوجد ضمان؟",
                "answer": "نعم، نوفر ضمان شامل لمدة 3 أشهر على جميع العمالة. في حالة وجود أي مشكلة، يمكن تغيير العاملة مجاناً خلال فترة الضمان.",
                "keywords": ["ضمان", "تغيير", "مشكلة", "مجاني"]
            },
            {
                "question": "ما هي الأوراق المطلوبة؟",
                "answer": "الأوراق المطلوبة: صورة الهوية الوطنية، صورة كشف حساب بنكي، نموذج طلب الاستقدام، وعقد العمل. فريقنا سيساعدك في إتمام جميع الإجراءات.",
                "keywords": ["أوراق", "مطلوبة", "مستندات", "هوية", "إجراءات"]
            },
            {
                "question": "كيفية التواصل معكم؟",
                "answer": "يمكنك التواصل معنا عبر: واتساب، هاتف: 0556914447 / 0506207444 / 0537914445. أوقات العمل: السبت-الخميس 8ص-10م، الجمعة 2م-10م",
                "keywords": ["تواصل", "هاتف", "واتساب", "أوقات", "عمل"]
            }
        ]
        
        print("✅ Enhanced Retriever محمل بدون نماذج محلية (RAM موفر)")
    
    def retrieve_best_matches(self, user_query: str, top_k: int = 3) -> Tuple[List[dict], float]:
        """البحث الذكي عن أفضل إجابات"""
        if not user_query or len(user_query.strip()) < 3:
            return [], 0.0
        
        user_query = user_query.strip().lower()
        best_matches = []
        best_confidence = 0.0
        
        try:
            # 1. البحث السريع في الأسئلة الشائعة (بدون AI)
            keyword_matches = self._search_by_keywords(user_query)
            if keyword_matches:
                print("🔍 تم العثور على مطابقات سريعة")
                return keyword_matches, 0.9
            
            # 2. البحث الذكي بـ embeddings (إذا لم نجد مطابقات سريعة)
            if self.embeddings_manager.client:
                similar_items = self.embeddings_manager.find_similar_embeddings(user_query, top_k)
                
                for text_content, similarity in similar_items:
                    if similarity > self.high_confidence_threshold:
                        # البحث عن الإجابة المناسبة
                        matching_qa = self._find_matching_qa(text_content)
                        if matching_qa:
                            best_matches.append(matching_qa)
                            best_confidence = max(best_confidence, similarity)
                
                if best_matches:
                    print(f"🧠 تم العثور على {len(best_matches)} إجابة بالذكاء الاصطناعي")
                    return best_matches[:top_k], best_confidence
            
            # 3. بحث احتياطي بسيط
            fallback_matches = self._simple_text_search(user_query)
            if fallback_matches:
                print("📋 استخدام البحث البسيط")
                return fallback_matches, 0.6
                
        except Exception as e:
            print(f"❌ خطأ في البحث: {e}")
        
        return [], 0.0
    
    def _search_by_keywords(self, query: str) -> List[dict]:
        """البحث السريع بالكلمات المفتاحية"""
        matches = []
        query_words = query.split()
        
        for qa in self.frequent_qa:
            score = 0
            for keyword in qa["keywords"]:
                for word in query_words:
                    if keyword in word or word in keyword:
                        score += 1
            
            if score >= 1:  # إذا وجدت كلمة مفتاحية واحدة على الأقل
                matches.append({
                    "question": qa["question"],
                    "answer": qa["answer"],
                    "confidence": min(score * 0.2, 0.9)
                })
        
        # ترتيب حسب الثقة
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        return matches[:3]
    
    def _find_matching_qa(self, text: str) -> Optional[dict]:
        """البحث عن سؤال وجواب مناسب للنص"""
        text_lower = text.lower()
        
        for qa in self.frequent_qa:
            # فحص إذا كان النص يحتوي على كلمات من السؤال أو الجواب
            if any(keyword in text_lower for keyword in qa["keywords"]):
                return {
                    "question": qa["question"],
                    "answer": qa["answer"],
                    "confidence": 0.8
                }
        
        return None
    
    def _simple_text_search(self, query: str) -> List[dict]:
        """بحث نصي بسيط كخطة احتياطية"""
        query_words = set(query.lower().split())
        matches = []
        
        for qa in self.frequent_qa:
            # فحص النص الكامل للسؤال والجواب
            all_text = (qa["question"] + " " + qa["answer"]).lower()
            all_words = set(all_text.split())
            
            # حساب التطابق
            common_words = query_words.intersection(all_words)
            if len(common_words) >= 1:
                confidence = len(common_words) / len(query_words)
                matches.append({
                    "question": qa["question"],
                    "answer": qa["answer"],
                    "confidence": min(confidence, 0.7)
                })
        
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        return matches[:2]
    
    def add_frequent_question(self, question: str, answer: str, keywords: List[str]):
        """إضافة سؤال جديد لقاعدة البيانات المحلية"""
        new_qa = {
            "question": question,
            "answer": answer,
            "keywords": keywords
        }
        self.frequent_qa.append(new_qa)
        
        # حفظ في قاعدة البيانات أيضاً
        self._save_frequent_question_to_db(new_qa)
    
    def _save_frequent_question_to_db(self, qa: dict):
        """حفظ السؤال في قاعدة البيانات"""
        if not self.customer_memory.db_pool:
            return
            
        try:
            conn = self.customer_memory.db_pool.getconn()
            with conn.cursor() as cur:
                question_hash = self.embeddings_manager.get_text_hash(qa["question"])
                
                cur.execute("""
                    INSERT INTO frequent_questions (question_hash, question, answer)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (question_hash) DO UPDATE SET
                    answer = EXCLUDED.answer
                """, (question_hash, qa["question"], qa["answer"]))
                
                conn.commit()
                
            self.customer_memory.db_pool.putconn(conn)
            
        except Exception as e:
            print(f"❌ خطأ في حفظ السؤال: {e}")
            if conn:
                self.customer_memory.db_pool.putconn(conn)
    
    def get_retriever_stats(self) -> dict:
        """إحصائيات المسترجع"""
        embeddings_stats = self.embeddings_manager.get_stats()
        
        return {
            "frequent_qa_count": len(self.frequent_qa),
            "embeddings_enabled": self.embeddings_manager.client is not None,
            **embeddings_stats
        }