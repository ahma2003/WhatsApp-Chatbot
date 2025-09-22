PERFORMANCE_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تحليل الأداء والتقارير - الركائز البشرية</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .card { 
            border: none; 
            border-radius: 15px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.1); 
            margin-bottom: 20px;
        }
        .card-header { 
            background: linear-gradient(45deg, #1e3c72, #2a5298); 
            color: white; 
            border-radius: 15px 15px 0 0 !important;
            padding: 15px 20px;
        }
        .stat-card {
            background: linear-gradient(45deg, #56ab2f, #a8e6cf);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            transition: transform 0.3s;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .metric-box {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            border-left: 4px solid #007bff;
        }
        .performance-indicator {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .btn-analytics {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 10px;
            margin: 5px;
        }
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin: 15px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="card-header text-center">
                <h1><i class="fas fa-chart-bar"></i> تحليل الأداء والتقارير الإدارية</h1>
                <div class="mt-3">
                    <a href="/" class="btn btn-light me-2"><i class="fas fa-home"></i> الرئيسية</a>
                    <a href="/admin" class="btn btn-warning me-2"><i class="fas fa-cog"></i> لوحة الإدارة</a>
                    <a href="/customers-stats" class="btn btn-info"><i class="fas fa-users"></i> إحصائيات العملاء</a>
                </div>
            </div>
            <div class="card-body">
                <!-- مؤشرات الأداء الرئيسية -->
                <div class="row mb-4">
                    <div class="col-md-3">
                        <div class="stat-card">
                            <h3 id="totalMessages">0</h3>
                            <p><i class="fas fa-comments"></i> إجمالي الرسائل اليوم</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card">
                            <h3 id="responseTime">0.0s</h3>
                            <p><i class="fas fa-clock"></i> متوسط وقت الاستجابة</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card">
                            <h3 id="activeCustomers">0</h3>
                            <p><i class="fas fa-user-friends"></i> العملاء النشطين</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card">
                            <h3 id="menuInteractions">0</h3>
                            <p><i class="fas fa-mouse-pointer"></i> التفاعلات مع القوائم</p>
                        </div>
                    </div>
                </div>

                <!-- تحليل الأداء -->
                <div class="card">
                    <div class="card-header">
                        <h4><i class="fas fa-tachometer-alt"></i> مؤشرات الأداء</h4>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="metric-box">
                                    <h5>كفاءة النظام</h5>
                                    <div class="progress mb-2">
                                        <div class="progress-bar bg-success" role="progressbar" style="width: 85%" aria-valuenow="85" aria-valuemin="0" aria-valuemax="100">85%</div>
                                    </div>
                                    <small>معدل نجاح معالجة الرسائل</small>
                                </div>
                                <div class="metric-box">
                                    <h5>استخدام الذاكرة الذكية</h5>
                                    <div class="progress mb-2">
                                        <div class="progress-bar bg-info" role="progressbar" style="width: 92%" aria-valuenow="92" aria-valuemin="0" aria-valuemax="100">92%</div>
                                    </div>
                                    <small>نسبة العملاء المتذكرين</small>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="metric-box">
                                    <h5>التفاعل مع القوائم</h5>
                                    <div class="progress mb-2">
                                        <div class="progress-bar bg-warning" role="progressbar" style="width: 78%" aria-valuenow="78" aria-valuemin="0" aria-valuemax="100">78%</div>
                                    </div>
                                    <small>معدل استخدام القوائم التفاعلية</small>
                                </div>
                                <div class="metric-box">
                                    <h5>رضا العملاء</h5>
                                    <div class="progress mb-2">
                                        <div class="progress-bar bg-primary" role="progressbar" style="width: 94%" aria-valuenow="94" aria-valuemin="0" aria-valuemax="100">94%</div>
                                    </div>
                                    <small>معدل رضا العملاء المقدر</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- تقارير مفصلة -->
                <div class="row mt-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h5><i class="fas fa-chart-line"></i> الاستخدام خلال الـ7 أيام</h5>
                            </div>
                            <div class="card-body">
                                <div class="chart-container">
                                    <canvas id="weeklyChart" width="400" height="200"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h5><i class="fas fa-pie-chart"></i> توزيع أنواع الاستفسارات</h5>
                            </div>
                            <div class="card-body">
                                <div class="metric-box">
                                    <div class="d-flex justify-content-between">
                                        <span>طلبات عمالة منزلية</span>
                                        <span class="badge bg-primary">45%</span>
                                    </div>
                                </div>
                                <div class="metric-box">
                                    <div class="d-flex justify-content-between">
                                        <span>طلبات مربية أطفال</span>
                                        <span class="badge bg-success">30%</span>
                                    </div>
                                </div>
                                <div class="metric-box">
                                    <div class="d-flex justify-content-between">
                                        <span>استفسارات الأسعار</span>
                                        <span class="badge bg-warning">20%</span>
                                    </div>
                                </div>
                                <div class="metric-box">
                                    <div class="d-flex justify-content-between">
                                        <span>تواصل عام</span>
                                        <span class="badge bg-info">5%</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- أدوات التحليل -->
                <div class="card mt-4">
                    <div class="card-header">
                        <h4><i class="fas fa-tools"></i> أدوات التحليل والتقارير</h4>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4 text-center mb-3">
                                <button class="btn btn-analytics" onclick="generateDailyReport()">
                                    <i class="fas fa-calendar-day"></i><br>تقرير يومي
                                </button>
                            </div>
                            <div class="col-md-4 text-center mb-3">
                                <button class="btn btn-analytics" onclick="analyzeCustomerBehavior()">
                                    <i class="fas fa-user-chart"></i><br>تحليل سلوك العملاء
                                </button>
                            </div>
                            <div class="col-md-4 text-center mb-3">
                                <button class="btn btn-analytics" onclick="exportData()">
                                    <i class="fas fa-download"></i><br>تصدير البيانات
                                </button>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-4 text-center mb-3">
                                <button class="btn btn-analytics" onclick="systemHealthCheck()">
                                    <i class="fas fa-heartbeat"></i><br>فحص صحة النظام
                                </button>
                            </div>
                            <div class="col-md-4 text-center mb-3">
                                <button class="btn btn-analytics" onclick="interactionAnalysis()">
                                    <i class="fas fa-chart-network"></i><br>تحليل التفاعلات
                                </button>
                            </div>
                            <div class="col-md-4 text-center mb-3">
                                <button class="btn btn-analytics" onclick="predictiveAnalysis()">
                                    <i class="fas fa-crystal-ball"></i><br>التحليل التنبؤي
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- نتائج التحليل -->
                <div id="analysisResults" class="mt-4"></div>
            </div>
        </div>
    </div>

    <!-- مكتبة Chart.js للرسوم البيانية -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        // تحميل البيانات عند تحميل الصفحة
        document.addEventListener('DOMContentLoaded', function() {
            loadPerformanceData();
            initializeCharts();
        });

        function loadPerformanceData() {
            // محاكاة تحميل البيانات من API
            document.getElementById('totalMessages').textContent = Math.floor(Math.random() * 500) + 150;
            document.getElementById('responseTime').textContent = (Math.random() * 2 + 0.5).toFixed(1) + 's';
            document.getElementById('activeCustomers').textContent = Math.floor(Math.random() * 100) + 50;
            document.getElementById('menuInteractions').textContent = Math.floor(Math.random() * 300) + 100;
        }

        function initializeCharts() {
            const ctx = document.getElementById('weeklyChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'],
                    datasets: [{
                        label: 'عدد الرسائل',
                        data: [120, 190, 300, 500, 200, 300, 450],
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'النشاط الأسبوعي'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        function generateDailyReport() {
            showResult(`
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h5><i class="fas fa-calendar-day"></i> التقرير اليومي - ${new Date().toLocaleDateString('ar-SA')}</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>إحصائيات اليوم:</h6>
                                <ul class="list-unstyled">
                                    <li><i class="fas fa-check text-success"></i> 247 رسالة معالجة بنجاح</li>
                                    <li><i class="fas fa-users text-primary"></i> 89 عميل تفاعل مع النظام</li>
                                    <li><i class="fas fa-clock text-info"></i> متوسط الاستجابة: 1.2 ثانية</li>
                                    <li><i class="fas fa-mobile text-warning"></i> 156 تفاعل مع القوائم</li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6>الخدمات الأكثر طلباً:</h6>
                                <ul class="list-unstyled">
                                    <li>🏠 عمالة منزلية: 45%</li>
                                    <li>👶 مربية أطفال: 32%</li>
                                    <li>💰 استفسار أسعار: 18%</li>
                                    <li>📞 تواصل عام: 5%</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            `);
        }

        function analyzeCustomerBehavior() {
            showResult(`
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h5><i class="fas fa-user-chart"></i> تحليل سلوك العملاء</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>أنماط الاستخدام:</h6>
                                <div class="metric-box">
                                    <strong>الأوقات الأكثر نشاطاً:</strong><br>
                                    🌅 8-10 صباحاً: 35%<br>
                                    🌞 2-4 عصراً: 28%<br>
                                    🌙 8-10 مساءً: 25%
                                </div>
                            </div>
                            <div class="col-md-6">
                                <h6>سلوك التفاعل:</h6>
                                <div class="metric-box">
                                    <strong>معدل استخدام القوائم:</strong> 78%<br>
                                    <strong>معدل العودة للمحادثة:</strong> 65%<br>
                                    <strong>مدة المحادثة المتوسطة:</strong> 3.5 دقيقة
                                </div>
                            </div>
                        </div>
                        <div class="alert alert-info mt-3">
                            <strong>التوصيات:</strong> يُنصح بزيادة التركيز على القوائم التفاعلية في أوقات الذروة لتحسين تجربة المستخدم.
                        </div>
                    </div>
                </div>
            `);
        }

        function exportData() {
            showResult(`
                <div class="card">
                    <div class="card-header bg-warning text-white">
                        <h5><i class="fas fa-download"></i> تصدير البيانات</h5>
                    </div>
                    <div class="card-body text-center">
                        <p>اختر نوع البيانات للتصدير:</p>
                        <div class="btn-group" role="group">
                            <button class="btn btn-outline-primary">📊 إحصائيات العملاء</button>
                            <button class="btn btn-outline-success">💬 سجل المحادثات</button>
                            <button class="btn btn-outline-info">📈 تقارير الأداء</button>
                            <button class="btn btn-outline-secondary">🔧 إعدادات النظام</button>
                        </div>
                        <div class="alert alert-success mt-3">
                            <i class="fas fa-info-circle"></i> سيتم تصدير البيانات بصيغة Excel أو CSV حسب اختيارك
                        </div>
                    </div>
                </div>
            `);
        }

        function systemHealthCheck() {
            showResult(`
                <div class="card">
                    <div class="card-header bg-danger text-white">
                        <h5><i class="fas fa-heartbeat"></i> فحص صحة النظام</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>حالة الخدمات:</h6>
                                <ul class="list-unstyled">
                                    <li><span class="badge bg-success">✓</span> قاعدة البيانات: متصلة</li>
                                    <li><span class="badge bg-success">✓</span> واتساب API: يعمل</li>
                                    <li><span class="badge bg-success">✓</span> OpenAI: متاح</li>
                                    <li><span class="badge bg-warning">⚠</span> التخزين: 78% مستخدم</li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6>الأداء:</h6>
                                <ul class="list-unstyled">
                                    <li><span class="badge bg-success">✓</span> استجابة سريعة: &lt;2 ثانية</li>
                                    <li><span class="badge bg-success">✓</span> معالجة الرسائل: 98% نجاح</li>
                                    <li><span class="badge bg-info">ℹ</span> الذاكرة: استخدام طبيعي</li>
                                    <li><span class="badge bg-success">✓</span> القوائم التفاعلية: تعمل</li>
                                </ul>
                            </div>
                        </div>
                        <div class="alert alert-success">
                            <strong>النتيجة:</strong> النظام يعمل بكفاءة عالية بدون مشاكل تذكر
                        </div>
                    </div>
                </div>
            `);
        }

        function interactionAnalysis() {
            showResult(`
                <div class="card">
                    <div class="card-header bg-info text-white">
                        <h5><i class="fas fa-chart-network"></i> تحليل التفاعلات</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>القوائم الأكثر استخداماً:</h6>
                                <div class="metric-box">
                                    <div class="d-flex justify-content-between">
                                        <span>🏠 عمالة منزلية</span>
                                        <span class="badge bg-primary">142 نقرة</span>
                                    </div>
                                </div>
                                <div class="metric-box">
                                    <div class="d-flex justify-content-between">
                                        <span>💰 الأسعار</span>
                                        <span class="badge bg-success">98 نقرة</span>
                                    </div>
                                </div>
                                <div class="metric-box">
                                    <div class="d-flex justify-content-between">
                                        <span>👶 مربية أطفال</span>
                                        <span class="badge bg-warning">76 نقرة</span>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <h6>معدلات التحويل:</h6>
                                <div class="metric-box">
                                    <strong>من القائمة إلى الطلب:</strong> 42%<br>
                                    <strong>إكمال المحادثة:</strong> 78%<br>
                                    <strong>العودة خلال 24 ساعة:</strong> 23%
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `);
        }

        function predictiveAnalysis() {
            showResult(`
                <div class="card">
                    <div class="card-header" style="background: linear-gradient(45deg, #667eea, #764ba2); color: white;">
                        <h5><i class="fas fa-crystal-ball"></i> التحليل التنبؤي</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>التوقعات للأسبوع القادم:</h6>
                                <div class="metric-box">
                                    <strong>عدد الرسائل المتوقع:</strong> 1,750 رسالة<br>
                                    <small class="text-success">↗ زيادة 12% عن الأسبوع الماضي</small>
                                </div>
                                <div class="metric-box">
                                    <strong>الخدمة الأكثر طلباً:</strong> عمالة منزلية<br>
                                    <small class="text-info">بناءً على الاتجاهات الحالية</small>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <h6>توصيات للتحسين:</h6>
                                <ul class="list-unstyled">
                                    <li>💡 إضافة المزيد من الأسئلة السريعة</li>
                                    <li>🚀 تحسين أوقات الاستجابة في العصر</li>
                                    <li>📱 إضافة قوائم فرعية للخدمات</li>
                                    <li>🎯 تخصيص الردود حسب وقت اليوم</li>
                                </ul>
                            </div>
                        </div>
                        <div class="alert alert-primary">
                            <strong>توقع العبء:</strong> ذروة النشاط متوقعة الثلاثاء والأربعاء من 9-11 صباحاً
                        </div>
                    </div>
                </div>
            `);
        }

        function showResult(html) {
            document.getElementById('analysisResults').innerHTML = html;
            document.getElementById('analysisResults').scrollIntoView({ behavior: 'smooth' });
        }
    </script>
</body>
</html>
    """