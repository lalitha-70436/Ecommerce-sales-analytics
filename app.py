# app.py
from flask import Flask, jsonify, render_template
from flask_cors import CORS
import os

from routes.products  import products_bp
from routes.customers import customers_bp
from routes.orders    import orders_bp
from routes.analytics import analytics_bp
from routes.auth      import auth_bp

app = Flask(__name__)
CORS(app)

# Secret key for sessions
app.secret_key = 'ecommerce_secret_key_2024'

# Register blueprints
app.register_blueprint(products_bp)
app.register_blueprint(customers_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(auth_bp)

# HTML pages
@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    return render_template('index.html')

@app.route('/products')
def products_page():
    return render_template('products.html')

@app.route('/customers')
def customers_page():
    return render_template('customers.html')

@app.route('/orders')
def orders_page():
    return render_template('orders.html')

@app.route('/charts')
def charts_page():
    return render_template('charts.html')

@app.route('/test-db')
def test_db():
    from config import get_db_connection
    conn = get_db_connection()
    if conn:
        conn.close()
        return jsonify({'message': 'Database connected!', 'status': 'success'})
    return jsonify({'message': 'Database connection failed!', 'status': 'error'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)