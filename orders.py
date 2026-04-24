# routes/orders.py
from flask import Blueprint, jsonify, request
from config import get_db_connection

orders_bp = Blueprint('orders', __name__)

# ── GET ALL ORDERS ───────────────────────
@orders_bp.route('/api/orders', methods=['GET'])
def get_orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            o.order_id,
            o.order_date,
            o.status,
            o.total_amount,
            c.customer_name,
            c.city
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        ORDER BY o.order_date DESC
        LIMIT 200
    """)
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(orders)

# ── GET ONE ORDER ────────────────────────
@orders_bp.route('/api/orders/<int:id>', methods=['GET'])
def get_order(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            o.order_id,
            o.order_date,
            o.status,
            o.total_amount,
            c.customer_name,
            c.city
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_id = %s
    """, (id,))
    order = cursor.fetchone()

    if order:
        cursor.execute("""
            SELECT
                oi.item_id,
                oi.quantity,
                oi.unit_price,
                p.product_name
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = %s
        """, (id,))
        order['items'] = cursor.fetchall()

    cursor.close()
    conn.close()

    if order:
        return jsonify(order)
    return jsonify({'error': 'Order not found'}), 404

# ── ADD ORDER ────────────────────────────
@orders_bp.route('/api/orders', methods=['POST'])
def add_order():
    try:
        data        = request.get_json()
        customer_id = int(data.get('customer_id', 0))
        order_date  = data.get('order_date', '')
        status      = data.get('status', 'processing')
        total       = float(data.get('total_amount', 0))

        if not customer_id:
            return jsonify({'error': 'Customer ID required'}), 400
        if not order_date:
            return jsonify({'error': 'Order date required'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders
            (customer_id, order_date, status, total_amount)
            VALUES (%s, %s, %s, %s)
        """, (customer_id, order_date, status, total))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return jsonify({
            'message':  'Order added successfully!',
            'order_id': new_id
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── UPDATE ORDER ─────────────────────────
@orders_bp.route('/api/orders/<int:id>', methods=['PUT'])
def update_order(id):
    try:
        data   = request.get_json()
        status = data.get('status', '').strip()
        total  = float(data.get('total_amount', 0))

        if not status:
            return jsonify({'error': 'Status required'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE orders
            SET status       = %s,
                total_amount = %s
            WHERE order_id = %s
        """, (status, total, id))
        conn.commit()

        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Order not found'}), 404

        cursor.close()
        conn.close()
        return jsonify({'message': 'Order updated successfully!'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── DELETE ORDER ─────────────────────────
@orders_bp.route('/api/orders/<int:id>', methods=['DELETE'])
def delete_order(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM order_items WHERE order_id = %s", (id,)
        )
        cursor.execute(
            "DELETE FROM orders WHERE order_id = %s", (id,)
        )
        conn.commit()

        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Order not found'}), 404

        cursor.close()
        conn.close()
        return jsonify({'message': 'Order deleted successfully!'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500