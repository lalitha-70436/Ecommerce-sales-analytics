# routes/auth.py
from flask import Blueprint, request, jsonify, session
from config import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

# ── CUSTOMER SIGNUP ──────────────────────
@auth_bp.route('/api/auth/signup', methods=['POST'])
def signup():
    try:
        data     = request.get_json()
        name     = data.get('customer_name', '').strip()
        email    = data.get('email', '').strip()
        password = data.get('password', '').strip()
        city     = data.get('city', '').strip()
        state    = data.get('state', '').strip()

        if not name or not email or not password:
            return jsonify({'error': 'Name, email and password are required!'}), 400

        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters!'}), 400

        # Hash the password before saving
        hashed = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO customers
            (customer_name, email, password, city, state, role)
            VALUES (%s, %s, %s, %s, %s, 'customer')
        """, (name, email, hashed, city, state))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return jsonify({
            'message': 'Account created successfully!',
            'customer_id': new_id
        }), 201

    except Exception as e:
        if 'Duplicate entry' in str(e):
            return jsonify({'error': 'Email already registered!'}), 400
        return jsonify({'error': str(e)}), 500

# ── CUSTOMER LOGIN ───────────────────────
@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data     = request.get_json()
        email    = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({'error': 'Email and password required!'}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT customer_id, customer_name,
                   email, password, role
            FROM customers
            WHERE email = %s
        """, (email,))
        customer = cursor.fetchone()
        cursor.close()
        conn.close()

        if not customer:
            return jsonify({'error': 'Email not found!'}), 404

        if not customer['password']:
            return jsonify({'error': 'Please reset your password!'}), 400

        if not check_password_hash(customer['password'], password):
            return jsonify({'error': 'Wrong password!'}), 401

        # Save to session
        session['user_id']   = customer['customer_id']
        session['user_name'] = customer['customer_name']
        session['user_email']= customer['email']
        session['role']      = 'customer'

        return jsonify({
            'message':  'Login successful!',
            'name':     customer['customer_name'],
            'email':    customer['email'],
            'role':     'customer',
            'id':       customer['customer_id']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── ADMIN LOGIN ──────────────────────────
@auth_bp.route('/api/auth/admin-login', methods=['POST'])
def admin_login():
    try:
        data     = request.get_json()
        email    = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({'error': 'Email and password required!'}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT admin_id, username, email, password
            FROM admins
            WHERE email = %s
        """, (email,))
        admin = cursor.fetchone()
        cursor.close()
        conn.close()

        if not admin:
            return jsonify({'error': 'Admin not found!'}), 404

        # Check password (plain text for now)
        if admin['password'] != password:
            return jsonify({'error': 'Wrong password!'}), 401

        session['user_id']   = admin['admin_id']
        session['user_name'] = admin['username']
        session['user_email']= admin['email']
        session['role']      = 'admin'

        return jsonify({
            'message': 'Admin login successful!',
            'name':    admin['username'],
            'email':   admin['email'],
            'role':    'admin'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── LOGOUT ───────────────────────────────
@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully!'})

# ── CHECK SESSION ─────────────────────────
@auth_bp.route('/api/auth/me', methods=['GET'])
def me():
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'name':      session.get('user_name'),
            'email':     session.get('user_email'),
            'role':      session.get('role')
        })
    return jsonify({'logged_in': False})