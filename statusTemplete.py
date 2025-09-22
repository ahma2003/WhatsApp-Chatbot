STATUS_TEMPLATE = """
    <html><head><title>حالة النظام - الركائز البشرية</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
    body{{font-family:Arial;margin:40px;background:#f0f8ff;}}
    .box{{background:white;padding:20px;border-radius:10px;margin:10px 0;box-shadow:0 4px 8px rgba(0,0,0,0.1);}}
    .green{{color:#28a745;}} .red{{color:#dc3545;}} .blue{{color:#007bff;}} .purple{{color:#6f42c1;}} .orange{{color:#fd7e14;}}
    .stat{{background:#e3f2fd;padding:15px;margin:10px 0;border-radius:8px;border-left:4px solid #2196f3;}}
    h1{{color:#1976d2;text-align:center;}}
    .new{{background:#fff3cd;border-left:4px solid #ffc107;}}
    </style></head><body>
    
    <div class="container">
        <div class="box">
            <h1>🧠 حالة النظام الذكي التفاعلي</h1>
            <div class="text-center">
                <a href="/" class="btn btn-primary">العودة للرئيسية</a>
                <a href="/admin" class="btn btn-warning">لوحة الإدارة</a>
            </div>
        </div>
        
        <div class="box">
            <h2>📊 الحالة العامة:</h2>
            <p class="{'green' if openai_client else 'red'}">{'✅' if openai_client else '❌'} OpenAI API</p>
            <p class="{'green' if enhanced_retriever else 'red'}">{'✅' if enhanced_retriever else '❌'} قاعدة البيانات الذكية</p>
            <p class="{'green' if customer_memory.db_pool else 'red'}">{'✅' if customer_memory.db_pool else '❌'} PostgreSQL Connection</p>
            <p class="green">⚡ الردود السريعة - نشط</p>
            <p class="blue">🙏 ردود الشكر السريعة - نشط</p>
            <p class="purple">🧠 <strong>محدث!</strong> نظام الذاكرة مع PostgreSQL - نشط</p>
            <p class="orange">📱 <strong>جديد!</strong> القوائم التفاعلية في الواتساب - {'نشط' if handler_stats['interactive_menu_available'] else 'غير نشط'}</p>
        </div>
        
        <div class="stat new">
            <h2>🆕 المميزات التفاعلية الجديدة:</h2>
            <ul>
                <li>✅ <strong>قوائم تفاعلية:</strong> أزرار وقوائم منسدلة في الواتساب</li>
                <li>✅ <strong>قائمة ترحيبية للعملاء الجدد:</strong> تظهر تلقائياً</li>
                <li>✅ <strong>أزرار سريعة:</strong> عاملة منزلية، مربية أطفال، تواصل معنا</li>
                <li>✅ <strong>معالجة ذكية للتفاعل:</strong> ردود تلقائية حسب الاختيار</li>
                <li>✅ <strong>عرض قائمة بكلمة "مساعدة":</strong> وصول سريع للخدمات</li>
                <li>✅ <strong>مسارات ذكية:</strong> اختيار "أسعار" → صورة فورية</li>
            </ul>
        </div>
        
        <div class="stat">
            <h2>🧠 إحصائيات الذاكرة الذكية:</h2>
            <ul>
                <li><strong>إجمالي العملاء المسجلين:</strong> {total_customers} عميل</li>
                <li><strong>العملاء النشطين في الذاكرة:</strong> {cached_customers} عميل</li>
                <li><strong>المحادثات النشطة:</strong> {active_conversations} محادثة</li>
                <li><strong>الرسائل قيد المعالجة:</strong> {handler_stats['processing_messages_count']} رسالة</li>
                <li><strong>الأرقام المحدودة السرعة:</strong> {handler_stats['rate_limited_numbers']} رقم</li>
            </ul>
        </div>
        
        <div class="box">
            <h2>⚡ المميزات المحدثة:</h2>
            <ul>
                <li>✅ <strong>قاعدة بيانات PostgreSQL:</strong> بيانات ديناميكية ومحدثة</li>
                <li>✅ <strong>ذاكرة شخصية للعملاء:</strong> البوت يتذكر اسم العميل وتاريخه</li>
                <li>✅ <strong>ترحيب مخصص:</strong> "أهلاً أخونا أحمد الكريم مرة ثانية"</li>
                <li>✅ <strong>تتبع الخدمات السابقة:</strong> يعرف العمالة السابقة والطلبات الحالية</li>
                <li>✅ <strong>سياق المحادثة:</strong> يتذكر آخر 3 رسائل من كل عميل</li>
                <li>✅ <strong>ردود ذكية مخصصة:</strong> حسب تفضيلات كل عميل</li>
                <li>✅ <strong>كاش ذكي:</strong> سرعة عالية مع توفير الذاكرة</li>
                <li>🆕 <strong>قوائم تفاعلية:</strong> تجربة مستخدم متطورة في الواتساب</li>
                <li>🆕 <strong>أزرار سريعة:</strong> وصول فوري للخدمات والأسعار</li>
                <li>🆕 <strong>معالجة تفاعلية:</strong> ردود ذكية على الأزرار والقوائم</li>
            </ul>
        </div>
        
        <p class="green text-center"><strong>النظام يعمل بأقصى ذكاء مع القوائم التفاعلية! 🧠 📱 🚀</strong></p>
    </div>
    </body></html>"""