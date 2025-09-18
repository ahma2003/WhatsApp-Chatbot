# --- قالب HTML للوحة الإدارة ---
ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة إدارة العملاء - مكتب الركائز</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container-fluid { padding: 20px; }
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
        .btn-primary { 
            background: linear-gradient(45deg, #1e3c72, #2a5298); 
            border: none; 
            border-radius: 10px;
        }
        .btn-success { 
            background: linear-gradient(45deg, #56ab2f, #a8e6cf); 
            border: none; 
            border-radius: 10px;
        }
        .btn-info { 
            background: linear-gradient(45deg, #667eea, #764ba2); 
            border: none; 
            border-radius: 10px;
        }
        .form-control, .form-select { 
            border-radius: 10px; 
            border: 2px solid #e9ecef;
            padding: 12px 15px;
        }
        .form-control:focus, .form-select:focus { 
            border-color: #667eea; 
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        .alert { border-radius: 10px; }
        .table { border-radius: 10px; overflow: hidden; }
        .table th { background-color: #f8f9fa; font-weight: 600; }
        h1, h4 { color: #2c3e50; }
        .nav-tabs .nav-link { border-radius: 10px 10px 0 0; }
        .nav-tabs .nav-link.active { background-color: #667eea; color: white; border-color: #667eea; }
        .loading { display: none; }
        .customers-table { max-height: 400px; overflow-y: auto; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header text-center">
                        <h1 class="mb-0"><i class="fas fa-users-cog"></i> لوحة إدارة العملاء - مكتب الركائز البشرية</h1>
                    </div>
                </div>
            </div>
        </div>

        <!-- Navigation Tabs -->
        <ul class="nav nav-tabs" id="adminTabs" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link active" id="add-customer-tab" data-bs-toggle="tab" data-bs-target="#add-customer" type="button">
                    <i class="fas fa-user-plus"></i> إضافة عميل جديد
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="add-service-tab" data-bs-toggle="tab" data-bs-target="#add-service" type="button">
                    <i class="fas fa-history"></i> إضافة خدمة سابقة
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="add-request-tab" data-bs-toggle="tab" data-bs-target="#add-request" type="button">
                    <i class="fas fa-tasks"></i> إضافة طلب حالي
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="customers-list-tab" data-bs-toggle="tab" data-bs-target="#customers-list" type="button">
                    <i class="fas fa-list"></i> قائمة العملاء
                </button>
            </li>
        </ul>

        <div class="tab-content" id="adminTabsContent">
            <!-- إضافة عميل جديد -->
            <div class="tab-pane fade show active" id="add-customer" role="tabpanel">
                <div class="card">
                    <div class="card-header">
                        <h4 class="mb-0"><i class="fas fa-user-plus"></i> إضافة عميل جديد</h4>
                    </div>
                    <div class="card-body">
                        <form id="customerForm">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label"><i class="fas fa-phone"></i> رقم الهاتف *</label>
                                    <input type="text" class="form-control" name="phone_number" placeholder="مثال: 201002589923" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label"><i class="fas fa-user"></i> اسم العميل *</label>
                                    <input type="text" class="form-control" name="name" placeholder="مثال: أحمد السيد" required>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label"><i class="fas fa-venus-mars"></i> الجنس</label>
                                    <select class="form-select" name="gender">
                                        <option value="">اختر الجنس</option>
                                        <option value="ذكر">ذكر</option>
                                        <option value="أنثى">أنثى</option>
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label"><i class="fas fa-globe"></i> الجنسية المفضلة</label>
                                    <select class="form-select" name="preferred_nationality">
                                        <option value="">اختر الجنسية المفضلة</option>
                                        <option value="فلبينية">فلبينية</option>
                                        <option value="إندونيسية">إندونيسية</option>
                                        <option value="سريلانكية">سريلانكية</option>
                                        <option value="هندية">هندية</option>
                                        <option value="بنغلاديشية">بنغلاديشية</option>
                                        <option value="إثيوبية">إثيوبية</option>
                                        <option value="كينية">كينية</option>
                                    </select>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label"><i class="fas fa-clipboard-list"></i> ملاحظات وتفضيلات</label>
                                <textarea class="form-control" name="preferences" rows="3" placeholder="مثال: يبحث عن عاملة منزلية ذات خبرة، يهتم بالنظافة والترتيب"></textarea>
                            </div>
                            <button type="submit" class="btn btn-primary btn-lg">
                                <i class="fas fa-save"></i> حفظ العميل
                                <span class="loading spinner-border spinner-border-sm ms-2"></span>
                            </button>
                        </form>
                    </div>
                </div>
            </div>

            <!-- إضافة خدمة سابقة -->
            <div class="tab-pane fade" id="add-service" role="tabpanel">
                <div class="card">
                    <div class="card-header">
                        <h4 class="mb-0"><i class="fas fa-history"></i> إضافة خدمة سابقة</h4>
                    </div>
                    <div class="card-body">
                        <form id="serviceForm">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label"><i class="fas fa-phone"></i> رقم هاتف العميل *</label>
                                    <input type="text" class="form-control" name="phone_number" placeholder="201002589923" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label"><i class="fas fa-user-tie"></i> اسم العاملة *</label>
                                    <input type="text" class="form-control" name="worker_name" placeholder="لوسي" required>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-4 mb-3">
                                    <label class="form-label"><i class="fas fa-flag"></i> الجنسية</label>
                                    <select class="form-select" name="nationality">
                                        <option value="">اختر الجنسية</option>
                                        <option value="فلبينية">فلبينية</option>
                                        <option value="إندونيسية">إندونيسية</option>
                                        <option value="سريلانكية">سريلانكية</option>
                                        <option value="هندية">هندية</option>
                                        <option value="بنغلاديشية">بنغلاديشية</option>
                                        <option value="إثيوبية">إثيوبية</option>
                                        <option value="كينية">كينية</option>
                                    </select>
                                </div>
                                <div class="col-md-4 mb-3">
                                    <label class="form-label"><i class="fas fa-briefcase"></i> المهنة</label>
                                    <select class="form-select" name="job_title">
                                        <option value="">اختر المهنة</option>
                                        <option value="عاملة منزلية">عاملة منزلية</option>
                                        <option value="مربية أطفال">مربية أطفال</option>
                                        <option value="طباخة">طباخة</option>
                                        <option value="سائق">سائق</option>
                                        <option value="عامل زراعة">عامل زراعة</option>
                                    </select>
                                </div>
                                <div class="col-md-4 mb-3">
                                    <label class="form-label"><i class="fas fa-calendar"></i> تاريخ التعاقد</label>
                                    <input type="date" class="form-control" name="contract_date">
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label"><i class="fas fa-check-circle"></i> الحالة</label>
                                    <select class="form-select" name="status">
                                        <option value="مستلمة">مستلمة</option>
                                        <option value="ملغاة">ملغاة</option>
                                        <option value="مُرتجعة">مُرتجعة</option>
                                        <option value="منتهية">منتهية</option>
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label"><i class="fas fa-file-contract"></i> رقم التعاقد</label>
                                    <input type="text" class="form-control" name="contract_id" placeholder="CUST005-LUCY-001">
                                </div>
                            </div>
                            <button type="submit" class="btn btn-success btn-lg">
                                <i class="fas fa-plus"></i> إضافة الخدمة
                                <span class="loading spinner-border spinner-border-sm ms-2"></span>
                            </button>
                        </form>
                    </div>
                </div>
            </div>

            <!-- إضافة طلب حالي -->
            <div class="tab-pane fade" id="add-request" role="tabpanel">
                <div class="card">
                    <div class="card-header">
                        <h4 class="mb-0"><i class="fas fa-tasks"></i> إضافة طلب حالي</h4>
                    </div>
                    <div class="card-body">
                        <form id="requestForm">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label"><i class="fas fa-phone"></i> رقم هاتف العميل *</label>
                                    <input type="text" class="form-control" name="phone_number" placeholder="201002589923" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label"><i class="fas fa-hashtag"></i> رقم الطلب</label>
                                    <input type="text" class="form-control" name="request_id" placeholder="REQ003-AHMED-001">
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-4 mb-3">
                                    <label class="form-label"><i class="fas fa-user-cog"></i> نوع الطلب</label>
                                    <select class="form-select" name="request_type">
                                        <option value="">اختر نوع الطلب</option>
                                        <option value="عاملة منزلية">عاملة منزلية</option>
                                        <option value="مربية أطفال">مربية أطفال</option>
                                        <option value="طباخة">طباخة</option>
                                        <option value="سائق">سائق</option>
                                        <option value="عامل زراعة">عامل زراعة</option>
                                    </select>
                                </div>
                                <div class="col-md-4 mb-3">
                                    <label class="form-label"><i class="fas fa-globe"></i> الجنسية المطلوبة</label>
                                    <select class="form-select" name="nationality_preference">
                                        <option value="">اختر الجنسية</option>
                                        <option value="فلبينية">فلبينية</option>
                                        <option value="إندونيسية">إندونيسية</option>
                                        <option value="سريلانكية">سريلانكية</option>
                                        <option value="هندية">هندية</option>
                                        <option value="بنغلاديشية">بنغلاديشية</option>
                                        <option value="إثيوبية">إثيوبية</option>
                                        <option value="كينية">كينية</option>
                                    </select>
                                </div>
                                <div class="col-md-4 mb-3">
                                    <label class="form-label"><i class="fas fa-info-circle"></i> حالة الطلب</label>
                                    <select class="form-select" name="status">
                                        <option value="البحث جاري">البحث جاري</option>
                                        <option value="تم العثور">تم العثور</option>
                                        <option value="في الانتظار">في الانتظار</option>
                                        <option value="تم التسليم">تم التسليم</option>
                                        <option value="ملغي">ملغي</option>
                                    </select>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label"><i class="fas fa-calendar-alt"></i> التاريخ المتوقع للتسليم</label>
                                <input type="date" class="form-control" name="estimated_delivery">
                            </div>
                            <button type="submit" class="btn btn-info btn-lg">
                                <i class="fas fa-paper-plane"></i> إضافة الطلب
                                <span class="loading spinner-border spinner-border-sm ms-2"></span>
                            </button>
                        </form>
                    </div>
                </div>
            </div>

            <!-- قائمة العملاء -->
            <div class="tab-pane fade" id="customers-list" role="tabpanel">
                <div class="card">
                    <div class="card-header">
                        <h4 class="mb-0"><i class="fas fa-list"></i> قائمة العملاء المسجلين</h4>
                        <button class="btn btn-sm btn-outline-light mt-2" onclick="loadCustomers()">
                            <i class="fas fa-sync"></i> تحديث القائمة
                        </button>
                    </div>
                    <div class="card-body">
                        <div class="customers-table">
                            <table class="table table-striped table-hover" id="customersTable">
                                <thead>
                                    <tr>
                                        <th>رقم الهاتف</th>
                                        <th>الاسم</th>
                                        <th>الجنس</th>
                                        <th>الجنسية المفضلة</th>
                                        <th>الخدمات السابقة</th>
                                        <th>الطلبات الحالية</th>
                                    </tr>
                                </thead>
                                <tbody id="customersTableBody">
                                    <tr><td colspan="6" class="text-center">جاري التحميل...</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- منطقة الرسائل -->
        <div id="messageArea"></div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // JavaScript code remains the same as in the original
    </script>
</body>
</html>
"""