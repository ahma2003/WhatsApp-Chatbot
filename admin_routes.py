from flask import request, jsonify
from psycopg2.extras import RealDictCursor

def setup_admin_routes(app, customer_memory):
    """إعداد جميع مسارات لوحة الإدارة"""
    
    @app.route('/admin/add-service', methods=['POST'])
    def add_past_service():
        """إضافة خدمة سابقة لعميل"""
        try:
            phone_number = request.form.get('phone_number', '').strip()
            worker_name = request.form.get('worker_name', '').strip()
            nationality = request.form.get('nationality', '')
            job_title = request.form.get('job_title', '')
            contract_date = request.form.get('contract_date', '')
            status = request.form.get('status', 'مستلمة')
            contract_id = request.form.get('contract_id', '').strip()
            
            if not phone_number or not worker_name:
                return jsonify({
                    'success': False, 
                    'message': 'رقم الهاتف واسم العاملة مطلوبان'
                }), 400
            
            if customer_memory.db_pool:
                conn = customer_memory.db_pool.getconn()
                try:
                    with conn.cursor() as cur:
                        # التحقق من وجود العميل
                        cur.execute("SELECT name FROM customers WHERE phone_number = %s", (phone_number,))
                        customer = cur.fetchone()
                        if not customer:
                            return jsonify({
                                'success': False, 
                                'message': f'العميل {phone_number} غير موجود في قاعدة البيانات'
                            }), 404
                        
                        # إضافة الخدمة السابقة
                        cur.execute("""
                            INSERT INTO past_services (phone_number, worker_name, nationality, job_title, 
                                                     contract_date, status, contract_id, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                        """, (phone_number, worker_name, nationality, job_title, contract_date, status, contract_id))
                        
                        conn.commit()
                        
                        # تنظيف الكاش
                        if phone_number in customer_memory.customer_cache:
                            del customer_memory.customer_cache[phone_number]
                        
                        return jsonify({
                            'success': True, 
                            'message': f'تم إضافة خدمة {worker_name} للعميل {customer[0]} بنجاح!'
                        })
                        
                finally:
                    customer_memory.db_pool.putconn(conn)
            else:
                return jsonify({
                    'success': False, 
                    'message': 'خطأ في الاتصال بقاعدة البيانات'
                }), 500
                
        except Exception as e:
            print(f"خطأ في إضافة الخدمة: {e}")
            return jsonify({
                'success': False, 
                'message': f'حدث خطأ: {str(e)}'
            }), 500

    @app.route('/admin/add-request', methods=['POST'])
    def add_current_request():
        """إضافة طلب حالي لعميل"""
        try:
            phone_number = request.form.get('phone_number', '').strip()
            request_id = request.form.get('request_id', '').strip()
            request_type = request.form.get('request_type', '')
            nationality_preference = request.form.get('nationality_preference', '')
            status = request.form.get('status', 'البحث جاري')
            estimated_delivery = request.form.get('estimated_delivery', '')
            
            if not phone_number:
                return jsonify({
                    'success': False, 
                    'message': 'رقم الهاتف مطلوب'
                }), 400
            
            if customer_memory.db_pool:
                conn = customer_memory.db_pool.getconn()
                try:
                    with conn.cursor() as cur:
                        # التحقق من وجود العميل
                        cur.execute("SELECT name FROM customers WHERE phone_number = %s", (phone_number,))
                        customer = cur.fetchone()
                        if not customer:
                            return jsonify({
                                'success': False, 
                                'message': f'العميل {phone_number} غير موجود في قاعدة البيانات'
                            }), 404
                        
                        # إضافة الطلب الحالي
                        cur.execute("""
                            INSERT INTO current_requests (phone_number, request_id, type, nationality_preference, 
                                                        status, estimated_delivery, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s, NOW())
                        """, (phone_number, request_id, request_type, nationality_preference, status, estimated_delivery))
                        
                        conn.commit()
                        
                        # تنظيف الكاش
                        if phone_number in customer_memory.customer_cache:
                            del customer_memory.customer_cache[phone_number]
                        
                        return jsonify({
                            'success': True, 
                            'message': f'تم إضافة طلب جديد للعميل {customer[0]} بنجاح!'
                        })
                        
                finally:
                    customer_memory.db_pool.putconn(conn)
            else:
                return jsonify({
                    'success': False, 
                    'message': 'خطأ في الاتصال بقاعدة البيانات'
                }), 500
                
        except Exception as e:
            print(f"خطأ في إضافة الطلب: {e}")
            return jsonify({
                'success': False, 
                'message': f'حدث خطأ: {str(e)}'
            }), 500

    @app.route('/admin/customers-list')
    def get_customers_list():
        """جلب قائمة العملاء للعرض في لوحة الإدارة"""
        try:
            customers = []
            if customer_memory.db_pool:
                conn = customer_memory.db_pool.getconn()
                try:
                    with conn.cursor(cursor_factory=RealDictCursor) as cur:
                        cur.execute("""
                            SELECT c.*, 
                                   (SELECT COUNT(*) FROM past_services WHERE phone_number = c.phone_number) as services_count,
                                   (SELECT COUNT(*) FROM current_requests WHERE phone_number = c.phone_number) as requests_count
                            FROM customers c 
                            ORDER BY c.created_at DESC 
                            LIMIT 50
                        """)
                        
                        customers = [dict(row) for row in cur.fetchall()]
                        
                finally:
                    customer_memory.db_pool.putconn(conn)
            
            return jsonify({
                'success': True,
                'customers': customers
            })
            
        except Exception as e:
            print(f"خطأ في جلب قائمة العملاء: {e}")
            return jsonify({
                'success': False, 
                'message': f'حدث خطأ: {str(e)}'
            }), 500