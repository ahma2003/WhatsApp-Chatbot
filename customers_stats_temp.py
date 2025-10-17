Customers_TEMP="""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إحصائيات العملاء - مكتب الركائز البشرية</title>
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
        .stat-box {
            background: linear-gradient(45deg, #56ab2f, #a8e6cf);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin: 10px 0;
        }
        .customer-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            border-left: 4px solid #007bff;
        }
        .loading {
            text-align: center;
            padding: 50px;
        }
        .error-box {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            border-left: 4px solid #dc3545;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="card-header text-center">
                <h1><i class="fas fa-chart-line"></i> إحصائيات العملاء - مكتب الركائز البشرية</h1>
                <div class="mt-3">
                    <a href="/" class="btn btn-light me-2"><i class="fas fa-home"></i> الرئيسية</a>
                    <a href="/admin" class="btn btn-warning me-2"><i class="fas fa-cog"></i> لوحة الإدارة</a>
                    <button class="btn btn-success" onclick="loadStats()"><i class="fas fa-sync"></i> تحديث</button>
                </div>
            </div>
            <div class="card-body">
                <div id="statsContent" class="loading">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">جاري التحميل...</span>
                    </div>
                    <p>جاري تحميل الإحصائيات...</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        function loadStats() {
            document.getElementById('statsContent').innerHTML = `
                <div class="loading">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">جاري التحميل...</span>
                    </div>
                    <p>جاري تحميل الإحصائيات...</p>
                </div>
            `;
            
            fetch('/api/customers-stats')
                .then(response => response.json())
                .then(data => {
                    displayStats(data);
                })
                .catch(error => {
                    document.getElementById('statsContent').innerHTML = `
                        <div class="error-box">
                            <h4><i class="fas fa-exclamation-triangle"></i> خطأ في تحميل البيانات</h4>
                            <p>حدث خطأ: ${error.message}</p>
                            <button class="btn btn-danger" onclick="loadStats()">إعادة المحاولة</button>
                        </div>
                    `;
                });
        }

        function displayStats(data) {
            const content = document.getElementById('statsContent');
            
            let html = `
                <div class="row">
                    <div class="col-md-3">
                        <div class="stat-box">
                            <h3>${data.total_customers || 0}</h3>
                            <p><i class="fas fa-users"></i> إجمالي العملاء</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-box">
                            <h3>${data.active_customers_in_memory || 0}</h3>
                            <p><i class="fas fa-memory"></i> في الذاكرة</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-box">
                            <h3>${data.active_conversations || 0}</h3>
                            <p><i class="fas fa-comments"></i> المحادثات النشطة</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-box">
                            <h3>${data.interaction_stats?.processing_messages_count || 0}</h3>
                            <p><i class="fas fa-cogs"></i> رسائل قيد المعالجة</p>
                        </div>
                    </div>
                </div>

                <div class="card mt-4">
                    <div class="card-header">
                        <h4><i class="fas fa-list"></i> آخر العملاء المسجلين</h4>
                    </div>
                    <div class="card-body">
            `;

            if (data.registered_customers && data.registered_customers.length > 0) {
                data.registered_customers.forEach(customer => {
                    html += `
                        <div class="customer-card">
                            <div class="row">
                                <div class="col-md-3">
                                    <strong><i class="fas fa-phone"></i> ${customer.phone_number}</strong>
                                </div>
                                <div class="col-md-2">
                                    <i class="fas fa-user"></i> ${customer.name}
                                </div>
                                <div class="col-md-2">
                                    <i class="fas fa-venus-mars"></i> ${customer.gender}
                                </div>
                                <div class="col-md-2">
                                    <span class="badge bg-primary">${customer.services_count} خدمات</span>
                                </div>
                                <div class="col-md-2">
                                    <span class="badge bg-info">${customer.requests_count} طلبات</span>
                                </div>
                                <div class="col-md-1">
                                    <small class="text-muted">${customer.created_at.split('T')[0]}</small>
                                </div>
                            </div>
                        </div>
                    `;
                });
            } else {
                html += '<p class="text-center">لا يوجد عملاء مسجلون</p>';
            }

            html += `
                    </div>
                </div>

                <div class="card mt-4">
                    <div class="card-header">
                        <h4><i class="fas fa-info-circle"></i> معلومات النظام</h4>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <p><strong>حالة قاعدة البيانات:</strong> 
                                   <span class="badge ${data.system_info?.database_connected ? 'bg-success' : 'bg-danger'}">
                                       ${data.system_info?.database_connected ? 'متصلة' : 'غير متصلة'}
                                   </span>
                                </p>
                                <p><strong>حالة النظام:</strong> 
                                   <span class="badge bg-info">${data.system_info?.status || 'غير معروف'}</span>
                                </p>
                            </div>
                            <div class="col-md-6">
                                <p><strong>وقت الاستعلام:</strong> ${data.system_info?.query_time || 'غير محدد'}</p>
                                ${data.interaction_stats?.whatsapp_config_ready ? 
                                    '<p><span class="badge bg-success">واتساب جاهز</span></p>' : 
                                    '<p><span class="badge bg-warning">واتساب غير جاهز</span></p>'
                                }
                            </div>
                        </div>
                    </div>
                </div>
            `;

            content.innerHTML = html;
        }

        // تحميل الإحصائيات عند تحميل الصفحة
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
        });
    </script>
</body>
</html>
    """