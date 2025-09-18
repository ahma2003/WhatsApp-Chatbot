import threading
import time
from datetime import datetime
from typing import Dict, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import psycopg2.pool
from config import DATABASE_URL, gen

class CustomerMemoryManager:
    def __init__(self):
        self.customer_cache = {}  # Cache للعملاء النشطين
        self.conversation_history = {}  # تاريخ المحادثات
        self.memory_lock = threading.Lock()
        self.db_pool = self.init_database_connection()
        print(f"📊 تم الاتصال بقاعدة البيانات PostgreSQL")
    
    def inspect_database_schema(self):
        """فحص بنية قاعدة البيانات لمعرفة أسماء الأعمدة الصحيحة"""
        if not self.db_pool:
            return
        
        try:
            conn = self.db_pool.getconn()
            with conn.cursor() as cur:
                # فحص جداول قاعدة البيانات
                tables = ['customers', 'past_services', 'current_requests']
                
                for table in tables:
                    try:
                        cur.execute(f"""
                            SELECT column_name, data_type 
                            FROM information_schema.columns 
                            WHERE table_name = '{table}'
                            ORDER BY ordinal_position;
                        """)
                        columns = cur.fetchall()
                        print(f"\n📋 جدول {table}:")
                        for col_name, col_type in columns:
                            print(f"  - {col_name}: {col_type}")
                            
                    except Exception as e:
                        print(f"❌ خطأ في فحص جدول {table}: {e}")
                        
            self.db_pool.putconn(conn)
            
        except Exception as e:
            print(f"❌ خطأ في فحص قاعدة البيانات: {e}")
            if conn:
                self.db_pool.putconn(conn)

    def normalize_phone_number(self, phone_number: str) -> str:
        """تطبيع رقم الهاتف - إزالة علامة + والمسافات"""
        if not phone_number:
            return phone_number
        
        # إزالة علامة + والمسافات والرموز الخاصة
        normalized = phone_number.replace("+", "").replace(" ", "").replace("-", "")
        
        print(f"📱 تطبيع الرقم: {phone_number} -> {normalized}")
        return normalized
    
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
        # تطبيع رقم الهاتف
        normalized_phone = self.normalize_phone_number(phone_number)
        
        with self.memory_lock:
            # البحث في الـ cache أولاً (نبحث بالرقم الأصلي والمطبع)
            cache_key = None
            if phone_number in self.customer_cache:
                cache_key = phone_number
            elif normalized_phone in self.customer_cache:
                cache_key = normalized_phone
            
            if cache_key:
                print(f"🎯 العميل موجود في الذاكرة: {cache_key}")
                return self.customer_cache[cache_key]
            
            # البحث في قاعدة البيانات بالرقم المطبع
            customer_data = self.load_customer_from_db(normalized_phone)
            if customer_data:
                # إضافة العميل للـ cache بكلا الصيغتين
                self.customer_cache[phone_number] = customer_data  # الرقم الأصلي
                self.customer_cache[normalized_phone] = customer_data  # الرقم المطبع
                print(f"✅ تم تحميل العميل للذاكرة: {customer_data.get('name', 'غير معروف')}")
                return customer_data
            
            print(f"🆕 عميل جديد: {normalized_phone}")
            return None
    
    def load_customer_from_db(self, phone_number: str) -> Optional[dict]:
        """تحميل بيانات العميل من قاعدة البيانات"""
        if not self.db_pool:
            return None
        
        # التأكد من أن الرقم مطبع قبل البحث
        normalized_phone = self.normalize_phone_number(phone_number)
        
        try:
            conn = self.db_pool.getconn()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # جلب بيانات العميل الأساسية - البحث بالرقم المطبع
                cur.execute("""
                    SELECT * FROM customers WHERE phone_number = %s
                """, (normalized_phone,))
                customer = cur.fetchone()
                
                if not customer:
                    print(f"🔍 لم يتم العثور على العميل: {normalized_phone}")
                    self.db_pool.putconn(conn)
                    return None
                
                customer_dict = dict(customer)
                print(f"✅ تم العثور على العميل: {customer_dict.get('name', 'غير معروف')}")
                
                # جلب الخدمات السابقة
                cur.execute("""
                    SELECT * FROM past_services WHERE phone_number = %s
                    ORDER BY contract_date DESC
                """, (normalized_phone,))
                past_services = [dict(service) for service in cur.fetchall()]
                customer_dict['past_services'] = past_services
                print(f"📚 عدد الخدمات السابقة: {len(past_services)}")
                
                # جلب الطلبات الحالية  
                cur.execute("""
                    SELECT * FROM current_requests WHERE phone_number = %s
                    ORDER BY id DESC
                """, (normalized_phone,))
                current_requests = [dict(request) for request in cur.fetchall()]
                customer_dict['current_requests'] = current_requests
                print(f"⏳ عدد الطلبات الحالية: {len(current_requests)}")
                
                self.db_pool.putconn(conn)
                return customer_dict
                
        except Exception as e:
            print(f"❌ خطأ في جلب بيانات العميل {normalized_phone}: {e}")
            if conn:
                self.db_pool.putconn(conn)
            return None
    
    def add_conversation_message(self, phone_number: str, user_message: str, bot_response: str):
        """إضافة رسالة لتاريخ المحادثة"""
        # استخدام الرقم المطبع كمفتاح للمحادثة
        normalized_phone = self.normalize_phone_number(phone_number)
        
        with self.memory_lock:
            if normalized_phone not in self.conversation_history:
                self.conversation_history[normalized_phone] = []
            
            self.conversation_history[normalized_phone].append({
                'timestamp': datetime.now().isoformat(),
                'user_message': user_message,
                'bot_response': bot_response
            })
            
            # الاحتفاظ بآخر 10 رسائل فقط لكل عميل (توفير الذاكرة)
            if len(self.conversation_history[normalized_phone]) > 10:
                self.conversation_history[normalized_phone] = self.conversation_history[normalized_phone][-10:]
                print(f"🧹 تنظيف تاريخ المحادثة للعميل: {normalized_phone}")
    
    def get_conversation_context(self, phone_number: str) -> str:
        """جلب سياق المحادثة السابقة"""
        normalized_phone = self.normalize_phone_number(phone_number)
        
        with self.memory_lock:
            if normalized_phone not in self.conversation_history:
                return ""
            
            recent_messages = self.conversation_history[normalized_phone][-3:]  # آخر 3 رسائل
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
            global gen
            gen = True
            summary += " (أختنا الكريمة)"
        
        # الخدمات السابقة
        if past_services:
            summary += f"\n🏆 له تعامل سابق معنا - عدد {len(past_services)} خدمة"
            latest_service = past_services[0]  # أحدث خدمة (مرتبة DESC)
            summary += f"\n📝 آخر خدمة: {latest_service.get('job_title', '')} - {latest_service.get('worker_name', '')} ({latest_service.get('nationality', '')})"
            
            # إضافة تقييم آخر خدمة إن وجد
            if latest_service.get('rating'):
                summary += f" - تقييم: {latest_service.get('rating')}/5"
        
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
        # نحتفظ بـ 100 عنصر فقط في الـ cache (50 عميل × 2 مفتاح لكل عميل)
        if len(self.customer_cache) > 100:
            # نحذف النصف الأول (oldest)
            keys_to_remove = list(self.customer_cache.keys())[:50]
            for key in keys_to_remove:
                del self.customer_cache[key]
            print("🧹 تنظيف ذاكرة العملاء")
    
    def get_customer_stats(self) -> dict:
        """إحصائيات سريعة للذاكرة"""
        return {
            'cached_customers': len(self.customer_cache),
            'active_conversations': len(self.conversation_history),
            'db_connection_active': self.db_pool is not None
        }