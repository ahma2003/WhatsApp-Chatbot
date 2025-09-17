# enhanced_app_with_postgresql.py
import os
import json
import requests
import threading
import time
import re
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from openai import OpenAI
import chromadb
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Optional
import hashlib
import psycopg2
from psycopg2.extras import RealDictCursor
import psycopg2.pool

# --- Configuration ---
ACCESS_TOKEN = os.environ.get('WHATSAPP_ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('WHATSAPP_VERIFY_TOKEN')
PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
DATABASE_URL = "postgresql://postgres:yJFsFKdulCLCFpPvBEjLQaiJcFJNijar@shinkansen.proxy.rlwy.net:40736/railway"
DATABASE_URL = os.environ.get('DATABASE_URL')
gen=False
app = Flask(__name__)

# --- 🧠 نظام Memory العملاء الذكي - محدث للعمل مع PostgreSQL ---
class CustomerMemoryManager:
    def __init__(self):
        self.customer_cache = {}  # Cache للعملاء النشطين
        self.conversation_history = {}  # تاريخ المحادثات
        self.memory_lock = threading.Lock()
        self.db_pool = self.init_database_connection()
        print(f"📊 تم الاتصال بقاعدة البيانات PostgreSQL")
    
    def init_database_connection(self):
        """إنشاء pool للاتصال بقاعدة البيانات"""
        try:
            pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=DATABASE_URL
            )
            print("✅ تم إنشاء connection pool بنجاح")
            return pool
        except Exception as e:
            print(f"❌ خطأ في الاتصال بقاعدة البيانات: {e}")
            return None
    
    def get_customer_info(self, phone_number: str) -> Optional[dict]:
        """جلب معلومات العميل من الذاكرة أو قاعدة البيانات"""
        with self.memory_lock:
            # البحث في الـ cache أولاً
            if phone_number in self.customer_cache:
                print(f"🎯 العميل موجود في الذاكرة: {phone_number}")
                return self.customer_cache[phone_number]
            
            # البحث في قاعدة البيانات
            customer_data = self.load_customer_from_db(phone_number)
            if customer_data:
                # إضافة العميل للـ cache
                self.customer_cache[phone_number] = customer_data
                print(f"✅ تم تحميل العميل للذاكرة: {customer_data.get('name', 'غير معروف')}")
                return customer_data
            
            print(f"🆕 عميل جديد: {phone_number}")
            return None
    
    def load_customer_from_db(self, phone_number: str) -> Optional[dict]:
        """تحميل بيانات العميل من قاعدة البيانات"""
        if not self.db_pool:
            return None
        
        try:
            conn = self.db_pool.getconn()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # جلب بيانات العميل الأساسية
                cur.execute("""
                    SELECT * FROM customers WHERE phone_number = %s
                """, (phone_number,))
                customer = cur.fetchone()
                
                if not customer:
                    return None
                
                customer_dict = dict(customer)
                
                # جلب الخدمات السابقة
                cur.execute("""
                    SELECT * FROM past_services WHERE customer_phone = %s
                    ORDER BY contract_date DESC
                """, (phone_number,))
                past_services = [dict(service) for service in cur.fetchall()]
                customer_dict['past_services'] = past_services
                
                # جلب الطلبات الحالية
                cur.execute("""
                    SELECT * FROM current_requests WHERE customer_phone = %s
                    ORDER BY created_at DESC
                """, (phone_number,))
                current_requests = [dict(request) for request in cur.fetchall()]
                customer_dict['current_requests'] = current_requests
                
                self.db_pool.putconn(conn)
                return customer_dict
                
        except Exception as e:
            print(f"❌ خطأ في جلب بيانات العميل: {e}")
            if conn:
                self.db_pool.putconn(conn)
            return None
    
    def add_conversation_message(self, phone_number: str, user_message: str, bot_response: str):
        """إضافة رسالة لتاريخ المحادثة"""
        with self.memory_lock:
            if phone_number not in self.conversation_history:
                self.conversation_history[phone_number] = []
            
            self.conversation_history[phone_number].append({
                'timestamp': datetime.now().isoformat(),
                'user_message': user_message,
                'bot_response': bot_response
            })
            
            # الاحتفاظ بآخر 10 رسائل فقط لكل عميل (توفير الذاكرة)
            if len(self.conversation_history[phone_number]) > 10:
                self.conversation_history[phone_number] = self.conversation_history[phone_number][-10:]
    
    def get_conversation_context(self, phone_number: str) -> str:
        """جلب سياق المحادثة السابقة"""
        with self.memory_lock:
            if phone_number not in self.conversation_history:
                return ""
            
            recent_messages = self.conversation_history[phone_number][-3:]  # آخر 3 رسائل
            context = ""
            
            for msg in recent_messages:
                context += f"العميل: {msg['user_message']}\n"
                context += f"البوت: {msg['bot_response'][:100]}...\n"
            
            return context
    
    def create_customer_summary(self, customer_data: dict) -> str:
        """إنشاء ملخص مختصر وذكي للعميل"""
        if not customer_data:
            return ""
        
        name = customer_data.get('name', 'عميل كريم')
        gender = customer_data.get('gender', '')
        preferred_nationality = customer_data.get('preferred_nationality', '')
        past_services = customer_data.get('past_services', [])
        current_requests = customer_data.get('current_requests', [])
        preferences = customer_data.get('preferences', '')
        
        summary = f"العميل: {name}"
        
        if gender == 'ذكر':
            summary += " (أخونا الكريم)"
        elif gender == 'أنثى':
            gen=True
            summary += " (أختنا الكريمة)"
        
        # الخدمات السابقة
        if past_services:
            summary += f"\n🏆 له تعامل سابق معنا - عدد {len(past_services)} خدمة"
            latest_service = past_services[0]  # أحدث خدمة (مرتبة DESC)
            summary += f"\n📝 آخر خدمة: {latest_service.get('job_title', '')} - {latest_service.get('worker_name', '')} ({latest_service.get('nationality', '')})"
        
        # الطلبات الحالية
        if current_requests:
            current_req = current_requests[0]  # أول طلب حالي
            summary += f"\n⏳ طلب حالي: {current_req.get('type', '')} - {current_req.get('status', '')}"
            if current_req.get('estimated_delivery'):
                summary += f" - متوقع: {current_req.get('estimated_delivery', '')}"
        
        # التفضيلات
        if preferred_nationality:
            summary += f"\n🌍 يفضل: {preferred_nationality}"
        
        if preferences:
            summary += f"\n💡 ملاحظات: {preferences[:100]}..."
        
        return summary
    
    def cleanup_old_cache(self):
        """تنظيف الذاكرة من العملاء القدامى"""
        # هنحتفظ بـ 50 عميل فقط في الـ cache
        if len(self.customer_cache) > 50:
            # نحذف النصف الأول (oldest)
            keys_to_remove = list(self.customer_cache.keys())[:25]
            for key in keys_to_remove:
                del self.customer_cache[key]
            print("🧹 تنظيف ذاكرة العملاء")

# --- 🚀 نظام ذاكرة محادثات محسّن ---
class ConversationManager:
    def __init__(self, customer_memory):
        self.conversations = {}
        self.message_lock = threading.Lock()
        self.cleanup_interval = 3600
        self.customer_memory = customer_memory
        
    def is_first_message(self, phone_number: str) -> bool:
        with self.message_lock:
            return phone_number not in self.conversations
    
    def register_conversation(self, phone_number: str):
        with self.message_lock:
            # جلب معلومات العميل عند بداية المحادثة
            customer_info = self.customer_memory.get_customer_info(phone_number)
            
            self.conversations[phone_number] = {
                'first_message_time': datetime.now(),
                'last_activity': datetime.now(),
                'message_count': 1,
                'is_existing_customer': customer_info is not None,
                'customer_name': customer_info.get('name', '') if customer_info else ''
            }
    
    def update_activity(self, phone_number: str):
        with self.message_lock:
            if phone_number in self.conversations:
                self.conversations[phone_number]['last_activity'] = datetime.now()
                self.conversations[phone_number]['message_count'] += 1
    
    def cleanup_old_conversations(self):
        """تنظيف المحادثات القديمة (أكثر من 24 ساعة)"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        with self.message_lock:
            expired = [phone for phone, data in self.conversations.items() 
                      if data['last_activity'] < cutoff_time]
            for phone in expired:
                del self.conversations[phone]
            if expired:
                print(f"🧹 تم تنظيف {len(expired)} محادثة قديمة")

# --- ⚡ نظام الردود السريعة المطور ---
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
        
        # 🙏 كلمات وعبارات الشكر بالهجة السعودية
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
        
        # كلمات دلالية للأسعار - محسّنة
        self.price_keywords = [
            'سعر', 'اسعار', 'أسعار', 'تكلفة', 'كلفة', 'تكاليف','اسعاركم',
            'فلوس', 'ريال', 'مبلغ', 'رسوم','عروضكم',
            'عرض', 'عروض', 'باقة', 'باقات', 'خصم', 'خصومات','خصوماتكم',
            'ثمن', 'مصاريف', 'مصروف', 'دفع', 'يكلف', 'تكلف', 'بكام'
        ]
        
        # جمل كاملة للأسعار
        self.price_phrases = [
            'كم السعر', 'ايش السعر', 'وش السعر', 'كم التكلفة','ايش اسعاركم','ايش اسعاركم',
            'وش التكلفة', 'كم الكلفة', 'ايش الكلفة', 'وش الكلفة',
            'كم التكاليف', 'ايش التكاليف', 'وش التكاليف',   
        
            'كم الثمن', 'ابغى اعرف السعر',
            'عايز اعرف السعر', 'ايه الاسعار', 'وش الاسعار',
            'رسوم الاستقدام', 'اسعار الاستقدام', 'تكلفة الاستقدام',
            
        ]
    
    def is_greeting_message(self, message: str) -> bool:
        """فحص سريع للرسائل الترحيبية"""
        if not message or len(message.strip()) == 0:
            return False
            
        message_clean = message.lower().strip()
        words = message_clean.split()
        
        # إذا الرسالة قصيرة وتحتوي على ترحيب
        if len(words) <= 6:
            for word in words:
                clean_word = ''.join(c for c in word if c.isalnum() or c in 'أابتثجحخدذرزسشصضطظعغفقكلمنهويىءآإ')
                if clean_word in self.welcome_patterns:
                    return True
                    
        return False
    
    def is_thanks_message(self, message: str) -> bool:
        """🙏 فحص سريع ودقيق لرسائل الشكر بالهجة السعودية"""
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
        
        # إذا وجد كلمة واحدة أو أكثر تدل على الشكر
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
        
        # إذا وجد كلمة واحدة أو أكثر تدل على السعر
        return price_word_count >= 1
    
    def get_welcome_response(self, customer_name: str = None) -> str:
        """رد الترحيب السريع (مع التخصيص للعملاء المسجلين)"""
        if customer_name and gen:
            return f"""أهلاً وسهلاً أختنا {customer_name} الكريمة مرة ثانية 🌟

حياك الله مرة ثانية في مكتب الركائز البشرية للاستقدام

كيف يمكنني مساعدتك اليوم؟ 😊"""
        elif customer_name and not gen:
             return f"""أهلاً وسهلاً أخونا {customer_name} الكريم مرة ثانية 🌟

حياك الله مرة ثانية في مكتب الركائز البشرية للاستقدام

كيف يمكنني مساعدتك اليوم؟ 😊"""        
        
        return """أهلاً وسهلاً بك في مكتب الركائز البشرية للاستقدام 🌟

نحن هنا لخدمتك ومساعدتك في جميع احتياجاتك من العمالة المنزلية المدربة والمؤهلة.

كيف يمكنني مساعدتك اليوم؟ 😊"""

    def get_thanks_response(self, customer_name: str = None) -> str:
        """🙏 رد الشكر السريع بالهجة السعودية (مع التخصيص)"""
        if customer_name and not gen:
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
        elif customer_name and  gen:
            responses = [
                f"""العفو أختنا {customer_name} ةالكريم 🌟

الله يعطيك العافية.. نحن في خدمتك دائماً في مكتب الركائز البشرية

هل تحتاج أي مساعدة أخرى؟ 😊""",
                
                f"""أهلاً وسهلاً أختنا {customer_name}.. هذا واجبنا 🤝

نحن سعداء بخدمتك في مكتب الركائز البشرية للاستقدام

الله يوفقك.. ولا تترددي في التواصل معنا متى شئتي! 💙""",
                
                f"""حياك الله أختنا {customer_name}.. ما قصرنا شي 🌟

خدمتك شرف لنا في مكتب الركائز البشرية

تواصلي معنا في أي وقت.. نحن هنا لخدمتك! 📞"""
            ]
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
        
        import random
        return random.choice(responses)

    def get_price_response(self) -> tuple:
        """رد الأسعار المختصر مع الصورة"""
        text_response = """إليك عروضنا الحالية للعمالة المنزلية المدربة 💼

🎉 عرض خاص بمناسبة اليوم الوطني السعودي 95

للاستفسار والحجز اتصل بنا:
📞 0556914447 / 0506207444 / 0537914445"""
        
        # ضع رابط صورتك هنا بعد رفعها
        image_url = "https://i.imghippo.com/files/La2232xjc.jpg"  # استبدل برابط صورتك
        
        return text_response, image_url
# --- 🔍 نظام البحث المحسن ---
class EnhancedRetriever:
    def __init__(self, model, collection):
        self.model = model
        self.collection = collection
        self.high_confidence_threshold = 0.75
    
    def retrieve_best_matches(self, user_query: str, top_k: int = 3) -> tuple:
        """استرجاع سريع للمطابقات"""
        if not self.model or not self.collection:
            return [], 0.0
        
        try:
            # بحث سريع
            query_embedding = self.model.encode([f"query: {user_query}"], normalize_embeddings=True)
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=min(top_k, 5)
            )
            
            if not results.get('metadatas') or not results['metadatas'][0]:
                return [], 0.0
            
            # حساب الثقة
            best_score = 1 - results['distances'][0][0] if 'distances' in results else 0
            results_data = results['metadatas'][0]
            
            return results_data, best_score
            
        except Exception as e:
            print(f"❌ خطأ في البحث: {e}")
            return [], 0.0

# --- 🤖 نظام الردود الذكي مع الذاكرة الشخصية ---
class SmartResponseGenerator:
    def __init__(self, openai_client, retriever, quick_system, customer_memory):
        self.openai_client = openai_client
        self.retriever = retriever
        self.quick_system = quick_system
        self.customer_memory = customer_memory
    
    def generate_response(self, user_message: str, phone_number: str, is_first: bool) -> tuple:
        """إنتاج الرد الذكي مع الذاكرة الشخصية"""
        
        print(f"🔍 معالجة: '{user_message}' من {phone_number}")
        
        # جلب معلومات العميل من الذاكرة
        customer_info = self.customer_memory.get_customer_info(phone_number)
        customer_name = customer_info.get('name', '') if customer_info else None
        
        # 1. أولوية عليا للترحيب (مع التخصيص)
        if self.quick_system.is_greeting_message(user_message):
            print(f"⚡ رد ترحيب فوري مخصص")
            response = self.quick_system.get_welcome_response(customer_name)
            self.customer_memory.add_conversation_message(phone_number, user_message, response)
            return response, False, None
        
        # 2. أولوية عليا للشكر (مع التخصيص) 🙏
        if self.quick_system.is_thanks_message(user_message):
            print(f"🙏 رد شكر فوري مخصص")
            response = self.quick_system.get_thanks_response(customer_name)
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
                if customer_name:
                    response = f"أهلاً بك مرة ثانية أخونا {customer_name} في مكتب الركائز البشرية! 🌟\nسيتواصل معك أحد موظفينا قريباً للمساعدة.\n\nهل تريد معرفة أسعارنا الحالية؟"
                else:
                    response = "أهلاً بك في مكتب الركائز البشرية! 🌟\nسيتواصل معك أحد موظفينا قريباً للمساعدة.\n\nهل تريد معرفة أسعارنا الحالية؟"
            
            self.customer_memory.add_conversation_message(phone_number, user_message, response)
            return response, False, None
        
        try:
            # إنشاء رد ذكي مع الذاكرة الشخصية
            context = self.generate_context_string(retrieved_data)
            conversation_context = self.customer_memory.get_conversation_context(phone_number)
            customer_summary = self.customer_memory.create_customer_summary(customer_info)
            
            # تحديد نوع الترحيب حسب العميل
            if is_first and customer_name:
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
            # رد احتياطي سريع مع التخصيص
            if retrieved_data:
                if customer_name:
                    response = f"عميلنا الكريم أخونا {customer_name}، بناءً على خبرتنا:\n\n{retrieved_data[0]['answer']}\n\nللمزيد من المساعدة، اتصل بنا: 📞 0556914447"
                else:
                    response = f"عميلنا العزيز، بناءً على خبرتنا:\n\n{retrieved_data[0]['answer']}\n\nللمزيد من المساعدة، اتصل بنا: 📞 0556914447"
            else:
                if customer_name:
                    response = f"أهلاً أخونا {customer_name}! 🌟 سيتواصل معك أحد متخصصينا قريباً.\n\nهل تريد معرفة عروضنا الحالية؟"
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

# --- 📱 نظام WhatsApp السريع ---
class WhatsAppHandler:
    def __init__(self, quick_system):
        self.processing_messages = set()
        self.rate_limit = {}
        self.quick_system = quick_system
    
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

# --- 🎯 تهيئة النظام الذكي مع الذاكرة ---
customer_memory = CustomerMemoryManager()
conversation_manager = ConversationManager(customer_memory)
quick_system = QuickResponseSystem()
whatsapp_handler = WhatsAppHandler(quick_system)

# تحميل مكونات الذكاء الاصطناعي
openai_client = None
enhanced_retriever = None
response_generator = None

if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    print("✅ OpenAI جاهز")

# تحميل ChromaDB (اختياري - للسرعة)
try:
    MODEL_NAME = 'intfloat/multilingual-e5-large'
    PERSIST_DIRECTORY = "my_chroma_db"
    COLLECTION_NAME = "recruitment_qa"
    
    print("📄 تحميل نموذج الذكاء الاصطناعي...")
    model = SentenceTransformer(MODEL_NAME)
    
    print("📄 الاتصال بقاعدة البيانات...")
    chroma_client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
    collection = chroma_client.get_collection(name=COLLECTION_NAME)
    
    enhanced_retriever = EnhancedRetriever(model, collection)
    response_generator = SmartResponseGenerator(openai_client, enhanced_retriever, quick_system, customer_memory)
    
    print(f"✅ النظام جاهز مع الذاكرة الذكية! قاعدة البيانات: {collection.count()} مستند")

except Exception as e:
    print(f"❌ فشل تحميل AI: {e}")
    print("💡 سيعمل بالردود السريعة والذاكرة فقط")
    response_generator = SmartResponseGenerator(openai_client, None, quick_system, customer_memory)

# --- 🚀 المسارات الرئيسية ---
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # [نفس الكود السابق - لم يتغير]
    pass

def process_user_message_with_memory(phone_number: str, user_message: str):
    # [نفس الكود السابق - لم يتغير]
    pass

@app.route('/')
def status():
    """صفحة حالة سريعة مع إحصائيات الذاكرة"""
    active_conversations = len(conversation_manager.conversations)
    cached_customers = len(customer_memory.customer_cache)
    
    # جلب إجمالي العملاء من قاعدة البيانات
    total_customers = 0
    try:
        if customer_memory.db_pool:
            conn = customer_memory.db_pool.getconn()
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM customers")
                total_customers = cur.fetchone()[0]
            customer_memory.db_pool.putconn(conn)
    except Exception as e:
        print(f"خطأ في جلب عدد العملاء: {e}")
    
    return f"""
    <html><head><title>بوت الركائز - نظام الذاكرة الذكي مع PostgreSQL</title>
    <style>body{{font-family:Arial;margin:40px;background:#f0f8ff;}}
    .box{{background:white;padding:20px;border-radius:10px;margin:10px 0;box-shadow:0 4px 8px rgba(0,0,0,0.1);}}
    .green{{color:#28a745;}} .red{{color:#dc3545;}} .blue{{color:#007bff;}} .purple{{color:#6f42c1;}}
    .stat{{background:#e3f2fd;padding:15px;margin:10px 0;border-radius:8px;border-left:4px solid #2196f3;}}
    h1{{color:#1976d2;text-align:center;}}
    </style></head><body>
    
    <div class="box">
    <h1>🧠 مكتب الركائز - بوت ذكي مع PostgreSQL</h1>
    </div>
    
    <div class="box">
    <h2>📊 الحالة العامة:</h2>
    <p class="{'green' if openai_client else 'red'}">{'✅' if openai_client else '❌'} OpenAI API</p>
    <p class="{'green' if enhanced_retriever else 'red'}">{'✅' if enhanced_retriever else '❌'} قاعدة البيانات</p>
    <p class="{'green' if customer_memory.db_pool else 'red'}">{'✅' if customer_memory.db_pool else '❌'} PostgreSQL Connection</p>
    <p class="green">⚡ الردود السريعة - نشط</p>
    <p class="blue">🙏 ردود الشكر السريعة - نشط</p>
    <p class="purple">🧠 <strong>محدث!</strong> نظام الذاكرة مع PostgreSQL - نشط</p>
    </div>
    
    <div class="stat">
    <h2>🧠 إحصائيات الذاكرة الذكية:</h2>
    <ul>
    <li><strong>إجمالي العملاء المسجلين:</strong> {total_customers} عميل</li>
    <li><strong>العملاء النشطين في الذاكرة:</strong> {cached_customers} عميل</li>
    <li><strong>المحادثات النشطة:</strong> {active_conversations} محادثة</li>
    </ul>
    </div>
    
    <div class="box">
    <h2>⚡ المميزات الجديدة:</h2>
    <ul>
    <li>✅ <strong>قاعدة بيانات PostgreSQL:</strong> بيانات ديناميكية ومحدثة</li>
    <li>✅ <strong>ذاكرة شخصية للعملاء:</strong> البوت يتذكر اسم العميل وتاريخه</li>
    <li>✅ <strong>ترحيب مخصص:</strong> "أهلاً أخونا أحمد الكريم مرة ثانية"</li>
    <li>✅ <strong>تتبع الخدمات السابقة:</strong> يعرف العمالة السابقة والطلبات الحالية</li>
    <li>✅ <strong>سياق المحادثة:</strong> يتذكر آخر 3 رسائل من كل عميل</li>
    <li>✅ <strong>ردود ذكية مخصصة:</strong> حسب تفضيلات كل عميل</li>
    <li>✅ <strong>كاش ذكي:</strong> سرعة عالية مع توفير الذاكرة</li>
    </ul>
    </div>
    
    <p class="green"><strong>النظام يعمل بأقصى ذكاء مع PostgreSQL! 🧠 🚀</strong></p>
    </body></html>"""

@app.route('/test-customer/<phone_number>/<message>')
def test_customer_memory(phone_number, message):
    # [نفس الكود السابق - لم يتغير]
    pass

@app.route('/customers-stats')
def customers_stats():
    """إحصائيات مفصلة عن العملاء من PostgreSQL"""
    stats = {
        "إجمالي_العملاء_المسجلين": 0,
        "العملاء_النشطين_في_الذاكرة": len(customer_memory.customer_cache),
        "المحادثات_النشطة": len(conversation_manager.conversations),
        "العملاء_المسجلون": []
    }
    
    try:
        if customer_memory.db_pool:
            conn = customer_memory.db_pool.getconn()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # جلب عدد العملاء
                cur.execute("SELECT COUNT(*) FROM customers")
                stats["إجمالي_العملاء_المسجلين"] = cur.fetchone()[0]
                
                # جلب أول 10 عملاء مع تفاصيلهم
                cur.execute("""
                    SELECT c.*, 
                           (SELECT COUNT(*) FROM past_services WHERE customer_phone = c.phone_number) as services_count,
                           (SELECT COUNT(*) FROM current_requests WHERE customer_phone = c.phone_number) as requests_count
                    FROM customers c 
                    ORDER BY c.created_at DESC 
                    LIMIT 10
                """)
                
                customers = cur.fetchall()
                for customer in customers:
                    stats["العملاء_المسجلون"].append({
                        "رقم_الهاتف": customer['phone_number'],
                        "الاسم": customer.get('name', 'غير معروف'),
                        "الجنس": customer.get('gender', 'غير محدد'),
                        "عدد_الخدمات_السابقة": customer['services_count'],
                        "عدد_الطلبات_الحالية": customer['requests_count'],
                        "الجنسية_المفضلة": customer.get('preferred_nationality', 'غير محدد')
                    })
            
            customer_memory.db_pool.putconn(conn)
    
    except Exception as e:
        print(f"خطأ في جلب إحصائيات العملاء: {e}")
    
    return jsonify(stats, ensure_ascii=False)

# --- 🧹 تنظيف ذكي مع الذاكرة ---
def smart_cleanup_with_memory():
    # [نفس الكود السابق - لم يتغير]
    pass

# تشغيل التنظيف الذكي
cleanup_thread = threading.Thread(target=smart_cleanup_with_memory, daemon=True)
cleanup_thread.start()

if __name__ == '__main__':
    print("🧠 تشغيل بوت الركائز الذكي مع PostgreSQL...")
    print("⚡ المميزات:")
    print("   - ردود فورية للترحيب والأسعار")
    print("   - 🙏 ردود شكر فورية بالهجة السعودية")
    print("   - 🧠 ذاكرة شخصية لكل عميل")
    print("   - 💤 تخزين بيانات ديناميكي مع PostgreSQL")
    print("   - 📊 تتبع الخدمات السابقة والطلبات الحالية")
    print("   - 💬 سياق المحادثة الذكي")
    print("   - 🎯 ردود مخصصة حسب تفضيلات العميل")
    print("   - ⚡ كاش ذكي للسرعة العالية")
    print("=" * 60)
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
