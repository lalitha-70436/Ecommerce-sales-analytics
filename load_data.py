# database/load_data.py
import pandas as pd
import mysql.connector
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG

# ── Change this to where your Superstore CSV is ──
CSV_FILE = "C:/Users/LENOVO/Desktop/Sample - Superstore.csv"

def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

# ── CLEAR ALL OLD DATA ───────────────────
def clear_all():
    print("Clearing old data...")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SET FOREIGN_KEY_CHECKS=0")
    cur.execute("TRUNCATE TABLE order_items")
    cur.execute("TRUNCATE TABLE orders")
    cur.execute("TRUNCATE TABLE products")
    cur.execute("TRUNCATE TABLE customers")
    cur.execute("TRUNCATE TABLE categories")
    cur.execute("SET FOREIGN_KEY_CHECKS=1")
    conn.commit()
    cur.close()
    conn.close()
    print("  Done!")

# ── READ CSV ─────────────────────────────
def read_csv():
    print("Reading Superstore CSV...")
    # Try different encodings
    for enc in ['utf-8', 'latin-1', 'cp1252']:
        try:
            df = pd.read_csv(CSV_FILE, encoding=enc)
            print(f"  Read {len(df)} rows with {enc} encoding")
            print(f"  Columns: {list(df.columns)}")
            return df
        except Exception as e:
            continue
    print("ERROR: Could not read CSV!")
    return None

# ── LOAD CATEGORIES ──────────────────────
def load_categories(df):
    print("Loading categories...")
    cats = df['Category'].dropna().unique()
    conn = get_conn()
    cur = conn.cursor()
    cat_map = {}
    for cat in cats:
        cur.execute(
            "INSERT INTO categories(category_name) VALUES(%s)",
            (str(cat),)
        )
        cat_map[cat] = cur.lastrowid
    conn.commit()
    cur.close()
    conn.close()
    print(f"  {len(cat_map)} categories loaded!")
    return cat_map

# ── LOAD PRODUCTS ────────────────────────
def load_products(df, cat_map):
    print("Loading products...")
    # Get unique products
    products_df = df[['Product Name', 'Category', 'Sales', 'Quantity']].copy()
    products_df = products_df.drop_duplicates(subset=['Product Name'])

    conn = get_conn()
    cur = conn.cursor()
    prod_map = {}
    count = 0

    for _, row in products_df.iterrows():
        try:
            product_name = str(row['Product Name'])[:200]
            cat_id = cat_map.get(row['Category'], 1)
            # Price = Sales / Quantity
            price = round(float(row['Sales']) / max(int(row['Quantity']), 1), 2)
            price = max(price, 10.0)  # minimum price 10
            stock = 100  # default stock

            cur.execute("""
                INSERT INTO products
                (product_name, category_id, price, stock_quantity)
                VALUES(%s, %s, %s, %s)
            """, (product_name, cat_id, price, stock))

            prod_map[product_name] = (cur.lastrowid, price)
            count += 1
        except Exception as e:
            pass

    conn.commit()
    cur.close()
    conn.close()
    print(f"  {count} products loaded!")
    return prod_map

# ── LOAD CUSTOMERS ───────────────────────
def load_customers(df):
    print("Loading customers...")
    # Get unique customers
    customers_df = df[['Customer Name', 'City', 'State',
                        'Postal Code']].copy()
    customers_df = customers_df.drop_duplicates(subset=['Customer Name'])

    conn = get_conn()
    cur = conn.cursor()
    cust_map = {}
    count = 0

    for i, row in customers_df.iterrows():
        try:
            name  = str(row['Customer Name'])
            email = name.lower().replace(" ", ".") + str(i) + "@mail.com"
            city  = str(row['City'])
            state = str(row['State'])
            zip_code = str(row['Postal Code'])

            cur.execute("""
                INSERT INTO customers
                (customer_name, email, city, state, zip_code)
                VALUES(%s, %s, %s, %s, %s)
            """, (name, email, city, state, zip_code))

            cust_map[name] = cur.lastrowid
            count += 1
        except Exception as e:
            pass

    conn.commit()
    cur.close()
    conn.close()
    print(f"  {count} customers loaded!")
    return cust_map

# ── LOAD ORDERS ──────────────────────────
def load_orders(df, cust_map, prod_map):
    print("Loading orders...")
    conn = get_conn()
    cur = conn.cursor()

    # Group by Order ID
    order_groups = df.groupby('Order ID')
    order_count = 0
    item_count  = 0
    order_id_map = {}

    for order_id_str, group in order_groups:
        try:
            # Get customer
            cust_name = group['Customer Name'].iloc[0]
            cust_id   = cust_map.get(cust_name)
            if not cust_id:
                continue

            # Get date
            order_date = pd.to_datetime(
                group['Order Date'].iloc[0]
            ).strftime('%Y-%m-%d')

            # Get status from Ship Mode
            ship_mode = str(group['Ship Mode'].iloc[0]).lower()
            if 'same day' in ship_mode:
                status = 'delivered'
            elif 'first class' in ship_mode:
                status = 'delivered'
            elif 'second class' in ship_mode:
                status = 'shipped'
            else:
                status = 'processing'

            # Total = sum of Sales
            total = round(float(group['Sales'].sum()), 2)

            # Insert order
            cur.execute("""
                INSERT INTO orders
                (customer_id, order_date, status, total_amount)
                VALUES(%s, %s, %s, %s)
            """, (cust_id, order_date, status, total))

            db_order_id = cur.lastrowid
            order_id_map[order_id_str] = db_order_id
            order_count += 1

            # Insert order items
            for _, item in group.iterrows():
                prod_name = str(item['Product Name'])[:200]
                prod_info = prod_map.get(prod_name)
                if prod_info:
                    prod_db_id = prod_info[0]
                    unit_price = round(
                        float(item['Sales']) / max(int(item['Quantity']), 1),
                        2
                    )
                    qty = int(item['Quantity'])
                    cur.execute("""
                        INSERT INTO order_items
                        (order_id, product_id, quantity, unit_price)
                        VALUES(%s, %s, %s, %s)
                    """, (db_order_id, prod_db_id, qty, unit_price))
                    item_count += 1

        except Exception as e:
            pass

    conn.commit()
    cur.close()
    conn.close()
    print(f"  {order_count} orders loaded!")
    print(f"  {item_count} order items loaded!")

# ── RUN ALL ──────────────────────────────
if __name__ == '__main__':
    print("=" * 45)
    print("   SUPERSTORE DATA LOADER")
    print("=" * 45)

    df = read_csv()
    if df is None:
        exit()

    clear_all()
    cat_map  = load_categories(df)
    prod_map = load_products(df, cat_map)
    cust_map = load_customers(df)
    load_orders(df, cust_map, prod_map)

    print("=" * 45)
    print("   ALL DONE!")
    print("=" * 45)