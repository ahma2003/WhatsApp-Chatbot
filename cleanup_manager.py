import threading
import time

def smart_cleanup_with_memory(conversation_manager, customer_memory, whatsapp_handler):
    """تنظيف دوري ذكي مع إدارة الذاكرة"""
    while True:
        time.sleep(900)  # كل 15 دقيقة
        
        conversation_manager.cleanup_old_conversations()
        customer_memory.cleanup_old_cache()
        
        # تنظيف الذاكرة
        if len(whatsapp_handler.processing_messages) > 500:
            whatsapp_handler.processing_messages.clear()
            print("🧹 تنظيف ذاكرة الرسائل")
        
        # تنظيف rate limiting
        current_time = time.time()
        expired_numbers = [
            number for number, last_time in whatsapp_handler.rate_limit.items() 
            if current_time - last_time > 1800  # 30 دقيقة
        ]
        for number in expired_numbers:
            del whatsapp_handler.rate_limit[number]
        
        print(f"🧠 إحصائيات الذاكرة: {len(customer_memory.customer_cache)} عميل نشط")

def start_cleanup_thread(conversation_manager, customer_memory, whatsapp_handler):
    """تشغيل التنظيف الذكي"""
    cleanup_thread = threading.Thread(
        target=smart_cleanup_with_memory, 
        args=(conversation_manager, customer_memory, whatsapp_handler),
        daemon=True
    )
    cleanup_thread.start()
    return cleanup_thread