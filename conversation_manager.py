import threading
from datetime import datetime, timedelta

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