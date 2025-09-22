import hashlib
import json
import threading
import time
from typing import List, Optional, Tuple
from openai import OpenAI
from config import OPENAI_API_KEY, EMBEDDING_MODEL

class OpenAIEmbeddingsManager:
    def __init__(self, customer_memory):
        self.client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
        self.customer_memory = customer_memory
        self.cache_lock = threading.Lock()
        self.daily_stats = {
            'api_calls': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'cost_saved': 0.0
        }
        
        # تكلفة OpenAI embeddings (أسعار حقيقية)
        self.cost_per_1k_tokens = 0.00002  # text-embedding-3-small
        
        print("✅ نظام OpenAI Embeddings محمل (RAM صفر!)")
    
    def get_text_hash(self, text: str) -> str:
        """إنشاء hash للنص لاستخدامه كمفتاح cache"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def get_cached_embedding(self, text_hash: str) -> Optional[List[float]]:
        """جلب embedding من الـ cache"""
        if not self.customer_memory.db_pool:
            return None
            
        try:
            conn = self.customer_memory.db_pool.getconn()
            with conn.cursor() as cur:
                # البحث في الـ cache مع تحديث آخر استخدام
                cur.execute("""
                    UPDATE embeddings_cache 
                    SET accessed_at = NOW(), access_count = access_count + 1
                    WHERE text_hash = %s
                    RETURNING embedding_vector
                """, (text_hash,))
                
                result = cur.fetchone()
                if result:
                    conn.commit()
                    self.daily_stats['cache_hits'] += 1
                    return json.loads(result[0])
                    
            self.customer_memory.db_pool.putconn(conn)
            
        except Exception as e:
            print(f"❌ خطأ في جلب embedding من cache: {e}")
            if conn:
                self.customer_memory.db_pool.putconn(conn)
        
        return None
    
    def save_embedding_to_cache(self, text_hash: str, text: str, embedding: List[float]):
        """حفظ embedding في الـ cache"""
        if not self.customer_memory.db_pool:
            return
            
        try:
            conn = self.customer_memory.db_pool.getconn()
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO embeddings_cache (text_hash, text_content, embedding_vector)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (text_hash) 
                    DO UPDATE SET accessed_at = NOW(), access_count = embeddings_cache.access_count + 1
                """, (text_hash, text[:1000], json.dumps(embedding)))  # نحفظ أول 1000 حرف فقط
                
                conn.commit()
            self.customer_memory.db_pool.putconn(conn)
            
        except Exception as e:
            print(f"❌ خطأ في حفظ embedding للـ cache: {e}")
            if conn:
                self.customer_memory.db_pool.putconn(conn)
    
    def get_embedding(self, text: str, use_cache: bool = True) -> Optional[List[float]]:
        """الحصول على embedding للنص (مع cache ذكي)"""
        if not self.client:
            print("❌ OpenAI client غير متوفر")
            return None
        
        # تنظيف النص
        text = text.strip()
        if len(text) < 3:
            return None
            
        text_hash = self.get_text_hash(text)
        
        # البحث في الـ cache أولاً
        if use_cache:
            with self.cache_lock:
                cached_embedding = self.get_cached_embedding(text_hash)
                if cached_embedding:
                    print(f"💾 Cache hit للنص: {text[:50]}...")
                    return cached_embedding
        
        # إذا لم يوجد في الـ cache، نطلب من OpenAI
        try:
            print(f"🔄 طلب embedding من OpenAI: {text[:50]}...")
            
            response = self.client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=text,
                encoding_format="float"
            )
            
            embedding = response.data[0].embedding
            
            # حفظ في الـ cache للمرات القادمة
            if use_cache:
                with self.cache_lock:
                    self.save_embedding_to_cache(text_hash, text, embedding)
            
            # تحديث الإحصائيات
            self.daily_stats['api_calls'] += 1
            self.daily_stats['cache_misses'] += 1
            
            # تقدير التكلفة (تقريبي)
            estimated_tokens = len(text.split()) * 1.3
            cost = (estimated_tokens / 1000) * self.cost_per_1k_tokens
            print(f"💰 تكلفة تقريبية: ${cost:.6f}")
            
            return embedding
            
        except Exception as e:
            print(f"❌ خطأ في OpenAI embeddings: {e}")
            return None
    
    def get_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """حساب التشابه بين embedding vectors"""
        if not embedding1 or not embedding2:
            return 0.0
        
        try:
            # Cosine similarity
            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
            magnitude1 = sum(a * a for a in embedding1) ** 0.5
            magnitude2 = sum(b * b for b in embedding2) ** 0.5
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
                
            return dot_product / (magnitude1 * magnitude2)
            
        except Exception as e:
            print(f"❌ خطأ في حساب التشابه: {e}")
            return 0.0
    
    def find_similar_embeddings(self, query_text: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """البحث عن نصوص مشابهة من الـ cache"""
        query_embedding = self.get_embedding(query_text)
        if not query_embedding:
            return []
        
        if not self.customer_memory.db_pool:
            return []
            
        similar_items = []
        
        try:
            conn = self.customer_memory.db_pool.getconn()
            with conn.cursor() as cur:
                # جلب آخر 50 embedding من الـ cache للمقارنة
                cur.execute("""
                    SELECT text_content, embedding_vector 
                    FROM embeddings_cache 
                    ORDER BY accessed_at DESC 
                    LIMIT 50
                """)
                
                results = cur.fetchall()
                
                for text_content, embedding_json in results:
                    try:
                        stored_embedding = json.loads(embedding_json)
                        similarity = self.get_similarity(query_embedding, stored_embedding)
                        
                        if similarity > 0.7:  # عتبة تشابه عالية
                            similar_items.append((text_content, similarity))
                            
                    except Exception as e:
                        continue
            
            self.customer_memory.db_pool.putconn(conn)
            
            # ترتيب حسب درجة التشابه
            similar_items.sort(key=lambda x: x[1], reverse=True)
            return similar_items[:top_k]
            
        except Exception as e:
            print(f"❌ خطأ في البحث المشابه: {e}")
            if conn:
                self.customer_memory.db_pool.putconn(conn)
            return []
    
    def cleanup_old_cache(self):
        """تنظيف الـ cache القديم"""
        if not self.customer_memory.db_pool:
            return
            
        try:
            conn = self.customer_memory.db_pool.getconn()
            with conn.cursor() as cur:
                # استدعاء دالة التنظيف
                cur.execute("SELECT cleanup_old_embeddings()")
                deleted_count = cur.fetchone()[0]
                conn.commit()
                
                if deleted_count > 0:
                    print(f"🧹 تم حذف {deleted_count} embedding قديم من الـ cache")
                    
            self.customer_memory.db_pool.putconn(conn)
            
        except Exception as e:
            print(f"❌ خطأ في تنظيف الـ cache: {e}")
            if conn:
                self.customer_memory.db_pool.putconn(conn)
    
    def get_stats(self) -> dict:
        """إحصائيات الاستخدام"""
        cache_stats = {'total_cached': 0, 'total_size_mb': 0}
        
        if self.customer_memory.db_pool:
            try:
                conn = self.customer_memory.db_pool.getconn()
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*), pg_total_relation_size('embeddings_cache') FROM embeddings_cache")
                    result = cur.fetchone()
                    if result:
                        cache_stats['total_cached'] = result[0]
                        cache_stats['total_size_mb'] = result[1] / (1024 * 1024) if result[1] else 0
                        
                self.customer_memory.db_pool.putconn(conn)
                
            except Exception as e:
                print(f"❌ خطأ في جلب الإحصائيات: {e}")
                if conn:
                    self.customer_memory.db_pool.putconn(conn)
        
        return {
            **self.daily_stats,
            **cache_stats,
            'cache_hit_rate': self.daily_stats['cache_hits'] / max(1, self.daily_stats['cache_hits'] + self.daily_stats['cache_misses']) * 100
        }