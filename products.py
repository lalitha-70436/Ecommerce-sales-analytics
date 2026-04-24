# routes/products.py
from flask import Blueprint, jsonify, request
from config import get_db_connection

products_bp = Blueprint('products', __name__)

# ── GET ALL PRODUCTS ─────────────────────
@products_bp.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            p.product_id,
            p.product_name,
            p.price,
            p.stock_quantity,
            c.category_name
        FROM products p
        LEFT JOIN categories c 
            ON p.category_id = c.category_id
        ORDER BY p.product_id DESC
        LIMIT 200
    """)
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(products)

# ── GET ONE PRODUCT ──────────────────────
@products_bp.route('/api/products/<int:id>', methods=['GET'])
def get_product(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            p.product_id,
            p.product_name,
            p.price,
            p.stock_quantity,
            c.category_name,
            c.category_id
        FROM products p
        LEFT JOIN categories c 
            ON p.category_id = c.category_id
        WHERE p.product_id = %s
    """, (id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    if product:
        return jsonify(product)
    return jsonify({'error': 'Product not found'}), 404

# ── ADD NEW PRODUCT ──────────────────────
@products_bp.route('/api/products', methods=['POST'])
def add_product():
    try:
        data          = request.get_json()
        name          = data.get('product_name', '').strip()
        price         = float(data.get('price', 0))
        stock         = int(data.get('stock_quantity', 0))
        category_id   = int(data.get('category_id', 1))

        if not name:
            return jsonify({'error': 'Product name is required'}), 400
        if price <= 0:
            return jsonify({'error': 'Price must be greater than 0'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products
            (product_name, price, stock_quantity, category_id)
            VALUES (%s, %s, %s, %s)
        """, (name, price, stock, category_id))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return jsonify({
            'message':    'Product added successfully!',
            'product_id': new_id
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── UPDATE PRODUCT ───────────────────────
@products_bp.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    try:
        data  = request.get_json()
        name  = data.get('product_name', '').strip()
        price = float(data.get('price', 0))
        stock = int(data.get('stock_quantity', 0))

        if not name:
            return jsonify({'error': 'Product name is required'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE products
            SET product_name   = %s,
                price          = %s,
                stock_quantity = %s
            WHERE product_id = %s
        """, (name, price, stock, id))
        conn.commit()

        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Product not found'}), 404

        cursor.close()
        conn.close()
        return jsonify({'message': 'Product updated successfully!'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── DELETE PRODUCT ───────────────────────
@products_bp.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # First delete related order_items
        cursor.execute(
            "DELETE FROM order_items WHERE product_id = %s", (id,)
        )

        # Then delete product
        cursor.execute(
            "DELETE FROM products WHERE product_id = %s", (id,)
        )
        conn.commit()

        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Product not found'}), 404

        cursor.close()
        conn.close()
        return jsonify({'message': 'Product deleted successfully!'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── GET ALL CATEGORIES ───────────────────
@products_bp.route('/api/categories', methods=['GET'])
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT category_id, category_name
        FROM categories
        ORDER BY category_name
    """)
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(categories)

# ── SEARCH PRODUCTS ──────────────────────
@products_bp.route('/api/products/search/<string:query>',
                   methods=['GET'])
def search_products(query):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            p.product_id,
            p.product_name,
            p.price,
            p.stock_quantity,
            c.category_name
        FROM products p
        LEFT JOIN categories c 
            ON p.category_id = c.category_id
        WHERE p.product_name LIKE %s
        LIMIT 50
    """, (f'%{query}%',))
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(products)