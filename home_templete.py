HOME_TEMPLETE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مكتب الركائز البشرية - النظام الذكي التفاعلي</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .hero-section {
            padding: 60px 0;
            color: white;
            text-align: center;
        }
        .feature-card {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        .feature-card:hover {
            transform: translateY(-5px);
        }
        .btn-custom {
            padding: 15px 30px;
            font-size: 18px;
            border-radius: 50px;
            margin: 10px;
            transition: all 0.3s;
        }
        .btn-custom:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        .stats-box {
            background: rgba(255,255,255,0.9);
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .new-feature {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="hero-section">
        <div class="container">
            <h1 class="display-3 mb-4">🧠 مكتب الركائز البشرية</h1>
            <p class="lead mb-4">النظام الذكي التفاعلي مع القوائم التفاعلية والذاكرة الشخصية</p>
            
            <!-- إعلان الميزة الجديدة -->
            <div class="new-feature">
                <h4>🆕 جديد! القوائم التفاعلية في الواتساب</h4>
                <p>الآن العملاء يمكنهم استخدام قوائم تفاعلية وأزرار سريعة للوصول لخدماتنا!</p>
            </div>
            
            <div class="row justify-content-center">
                <div class="col-md-3">
                    <a href="/status" class="btn btn-light btn-custom">
                        <i class="fas fa-chart-line"></i><br>حالة النظام
                    </a>
                </div>
                <div class="col-md-3">
                    <a href="/admin" class="btn btn-warning btn-custom">
                        <i class="fas fa-cog"></i><br>لوحة الإدارة
                    </a>
                </div>
                <div class="col-md-3">
                    <a href="/customers-stats" class="btn btn-info btn-custom">
                        <i class="fas fa-users"></i><br>إحصائيات العملاء
                    </a>
                </div>
                <div class="col-md-3">
                    <a href="/performance-analytics" class="btn btn-success btn-custom">
                        <i class="fas fa-chart-bar"></i><br>تحليل الأداء
                    </a>
                </div>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="row">
            <div class="col-md-4">
                <div class="feature-card">
                    <i class="fas fa-mobile-alt fa-3x text-primary mb-3"></i>
                    <h4>قوائم تفاعلية</h4>
                    <p>أزرار وقوائم منسدلة في الواتساب للوصول السريع للخدمات</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="feature-card">
                    <i class="fas fa-brain fa-3x text-success mb-3"></i>
                    <h4>ذاكرة شخصية</h4>
                    <p>يتذكر اسم كل عميل وتاريخه مع المكتب</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="feature-card">
                    <i class="fas fa-lightning-bolt fa-3x text-warning mb-3"></i>
                    <h4>ردود فورية</h4>
                    <p>استجابة سريعة للترحيب والأسعار والشكر</p>
                </div>
            </div>
        </div>
        
        <div class="stats-box text-center">
            <h3>النظام يعمل بأقصى ذكاء مع القوائم التفاعلية! 🚀</h3>
            <p>متكامل مع WhatsApp Business API وOpenAI وPostgreSQL</p>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """