# routes/customers.py
from flask import Blueprint, jsonify, request
from config import get_db_connection

customers_bp = Blueprint('customers', __name__)

# ── GET ALL CUSTOMERS ────────────────────
@customers_bp.route('/api/customers', methods=['GET'])
def get_customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            customer_id,
            customer_name,
            email,
            city,
            state,
            zip_code,
            created_at
        FROM customers
        ORDER BY customer_id DESC
        LIMIT 200
    """)
    customers = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(customers)

# ── GET ONE CUSTOMER ─────────────────────
@customers_bp.route('/api/customers/<int:id>', methods=['GET'])
def get_customer(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            customer_id,
            customer_name,
            email,
            city,
            state,
            zip_code,
            created_at
        FROM customers
        WHERE customer_id = %s
    """, (id,))
    customer = cursor.fetchone()

    if customer:
        # Also get their orders
        cursor.execute("""
            SELECT
                order_id,
                order_date,
                status,
                total_amount
            FROM orders
            WHERE customer_id = %s
            ORDER BY order_date DESC
            LIMIT 10
        """, (id,))
        customer['orders'] = cursor.fetchall()

    cursor.close()
    conn.close()

    if customer:
        return jsonify(customer)
    return jsonify({'error': 'Customer not found'}), 404

# ── ADD NEW CUSTOMER ─────────────────────
@customers_bp.route('/api/customers', methods=['POST'])
def add_customer():
    try:
        data  = request.get_json()
        name  = data.get('customer_name', '').strip()
        email = data.get('email', '').strip()
        city  = data.get('city', '').strip()
        state = data.get('state', '').strip()
        zip_code = data.get('zip_code', '').strip()

        if not name:
            return jsonify({'error': 'Name is required'}), 400
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        if not city:
            return jsonify({'error': 'City is required'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO customers
            (customer_name, email, city, state, zip_code)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, email, city, state, zip_code))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return jsonify({
            'message':     'Customer added successfully!',
            'customer_id': new_id
        }), 201

    except Exception as e:
        if 'Duplicate entry' in str(e):
            return jsonify({
                'error': 'Email already exists!'
            }), 400
        return jsonify({'error': str(e)}), 500

# ── UPDATE CUSTOMER ──────────────────────
@customers_bp.route('/api/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    try:
        data  = request.get_json()
        name  = data.get('customer_name', '').strip()
        email = data.get('email', '').strip()
        city  = data.get('city', '').strip()
        state = data.get('state', '').strip()

        if not name:
            return jsonify({'error': 'Name is required'}), 400
        if not email:
            return jsonify({'error': 'Email is required'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE customers
            SET customer_name = %s,
                email         = %s,
                city          = %s,
                state         = %s
            WHERE customer_id = %s
        """, (name, email, city, state, id))
        conn.commit()

        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Customer not found'}), 404

        cursor.close()
        conn.close()
        return jsonify({'message': 'Customer updated successfully!'})

    except Exception as e:
        if 'Duplicate entry' in str(e):
            return jsonify({
                'error': 'Email already exists!'
            }), 400
        return jsonify({'error': str(e)}), 500

# ── DELETE CUSTOMER ──────────────────────
@customers_bp.route('/api/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # First delete order_items for this customer's orders
        cursor.execute("""
            DELETE oi FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE o.customer_id = %s
        """, (id,))

        # Then delete orders
        cursor.execute(
            "DELETE FROM orders WHERE customer_id = %s", (id,)
        )

        # Then delete customer
        cursor.execute(
            "DELETE FROM customers WHERE customer_id = %s", (id,)
        )
        conn.commit()

        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Customer not found'}), 404

        cursor.close()
        conn.close()
        return jsonify({'message': 'Customer deleted successfully!'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── SEARCH CUSTOMERS ─────────────────────
@customers_bp.route('/api/customers/search/<string:query>',
                    methods=['GET'])
def search_customers(query):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            customer_id,
            customer_name,
            email,
            city,
            state
        FROM customers
        WHERE customer_name LIKE %s
           OR email LIKE %s
           OR city  LIKE %s
        LIMIT 50
    """, (f'%{query}%', f'%{query}%', f'%{query}%'))
    customers = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(customers)