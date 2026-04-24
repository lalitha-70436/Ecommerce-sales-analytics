# routes/analytics.py
from flask import Blueprint, jsonify
from config import get_db_connection

analytics_bp = Blueprint('analytics', __name__)

# ── SUMMARY ──────────────────────────────
@analytics_bp.route('/api/analytics/summary', methods=['GET'])
def summary():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM customers")
    customers = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM products")
    products = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM orders")
    orders = cursor.fetchone()['total']

    cursor.execute("""
        SELECT ROUND(SUM(total_amount), 2) AS total
        FROM orders
        WHERE status != 'cancelled'
    """)
    revenue = cursor.fetchone()['total'] or 0

    cursor.close()
    conn.close()
    return jsonify({
        'total_customers': customers,
        'total_products':  products,
        'total_orders':    orders,
        'total_revenue':   revenue
    })

# ── MONTHLY REVENUE ──────────────────────
@analytics_bp.route('/api/analytics/monthly-revenue',
                    methods=['GET'])
def monthly_revenue():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            DATE_FORMAT(order_date, '%Y-%m') AS month,
            ROUND(SUM(total_amount), 2)      AS revenue,
            COUNT(order_id)                  AS total_orders
        FROM orders
        WHERE status != 'cancelled'
        GROUP BY DATE_FORMAT(order_date, '%Y-%m')
        ORDER BY month ASC
    """)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

# ── TOP 5 PRODUCTS ────────────────────────
@analytics_bp.route('/api/analytics/top-products',
                    methods=['GET'])
def top_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            p.product_name,
            SUM(oi.quantity) AS total_sold,
            ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY p.product_id, p.product_name
        ORDER BY total_sold DESC
        LIMIT 5
    """)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

# ── TOP 5 CUSTOMERS ───────────────────────
@analytics_bp.route('/api/analytics/top-customers',
                    methods=['GET'])
def top_customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            c.customer_name,
            c.city,
            COUNT(o.order_id)              AS total_orders,
            ROUND(SUM(o.total_amount), 2)  AS total_spent
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        WHERE o.status != 'cancelled'
        GROUP BY c.customer_id, c.customer_name, c.city
        ORDER BY total_spent DESC
        LIMIT 5
    """)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

# ── CATEGORY SALES ────────────────────────
@analytics_bp.route('/api/analytics/category-sales',
                    methods=['GET'])
def category_sales():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            c.category_name,
            COUNT(oi.item_id) AS total_items_sold,
            ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
        FROM order_items oi
        JOIN products    p ON oi.product_id  = p.product_id
        JOIN categories  c ON p.category_id  = c.category_id
        GROUP BY c.category_id, c.category_name
        ORDER BY revenue DESC
        LIMIT 10
    """)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

# ── ORDER STATUS ──────────────────────────
@analytics_bp.route('/api/analytics/order-status',
                    methods=['GET'])
def order_status():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            status,
            COUNT(order_id)               AS total_orders,
            ROUND(SUM(total_amount), 2)   AS total_amount
        FROM orders
        GROUP BY status
        ORDER BY total_orders DESC
    """)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

# ── MONTHLY ORDERS COUNT ──────────────────
@analytics_bp.route('/api/analytics/monthly-orders',
                    methods=['GET'])
def monthly_orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            DATE_FORMAT(order_date, '%Y-%m') AS month,
            COUNT(order_id)                  AS total_orders
        FROM orders
        GROUP BY DATE_FORMAT(order_date, '%Y-%m')
        ORDER BY month ASC
    """)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)