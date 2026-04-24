# analytics/charts.py
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_db_connection

# Output folder for charts
OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'static', 'charts'
)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Dark theme colors
DARK_BG     = '#0d0f14'
CARD_BG     = '#181c26'
ACCENT      = '#ff4d6d'
ACCENT2     = '#00d4aa'
ACCENT3     = '#7c6af7'
ACCENT4     = '#ffa94d'
TEXT        = '#eef0f6'
TEXT_MUTED  = '#8b92a9'
COLORS      = [ACCENT3, ACCENT2, ACCENT, ACCENT4,
               '#5bc4f5', '#f7a8d4', '#a8f7c1', '#f7d4a8']

def set_dark_style():
    plt.rcParams.update({
        'figure.facecolor':  DARK_BG,
        'axes.facecolor':    CARD_BG,
        'axes.edgecolor':    '#2a2f3e',
        'axes.labelcolor':   TEXT_MUTED,
        'xtick.color':       TEXT_MUTED,
        'ytick.color':       TEXT_MUTED,
        'text.color':        TEXT,
        'grid.color':        '#1e2333',
        'grid.linestyle':    '--',
        'grid.alpha':        0.5,
        'font.family':       'DejaVu Sans',
        'font.size':         11,
    })

def get_df(query):
    conn = get_db_connection()
    df   = pd.read_sql(query, conn)
    conn.close()
    return df

# ── CHART 1: Monthly Revenue ─────────────
def chart_monthly_revenue():
    df = get_df("""
        SELECT DATE_FORMAT(order_date,'%Y-%m') AS month,
               ROUND(SUM(total_amount),2) AS revenue
        FROM orders
        WHERE status != 'cancelled'
        GROUP BY month
        ORDER BY month
    """)

    set_dark_style()
    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor(DARK_BG)

    ax.fill_between(df['month'], df['revenue'],
                    alpha=0.15, color=ACCENT3)
    ax.plot(df['month'], df['revenue'],
            color=ACCENT3, linewidth=2.5,
            marker='o', markersize=6,
            markerfacecolor=DARK_BG,
            markeredgecolor=ACCENT3,
            markeredgewidth=2)

    ax.set_title('Monthly Revenue', color=TEXT,
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Month', labelpad=10)
    ax.set_ylabel('Revenue (₹)', labelpad=10)
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f'₹{x:,.0f}')
    )
    plt.xticks(rotation=45, ha='right')
    ax.grid(True, axis='y')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'monthly_revenue.png')
    plt.savefig(path, dpi=150, bbox_inches='tight',
                facecolor=DARK_BG)
    plt.close()
    print("  monthly_revenue.png saved!")

# ── CHART 2: Top Products ────────────────
def chart_top_products():
    df = get_df("""
        SELECT p.product_name,
               SUM(oi.quantity) AS total_sold
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY p.product_id, p.product_name
        ORDER BY total_sold DESC
        LIMIT 8
    """)
    # Shorten long names
    df['short_name'] = df['product_name'].apply(
        lambda x: x[:30] + '...' if len(x) > 30 else x
    )

    set_dark_style()
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor(DARK_BG)

    bars = ax.barh(df['short_name'][::-1],
                   df['total_sold'][::-1],
                   color=COLORS[:len(df)],
                   height=0.6, edgecolor='none')

    for bar, val in zip(bars,
                        df['total_sold'][::-1]):
        ax.text(bar.get_width() + 0.3,
                bar.get_y() + bar.get_height()/2,
                f'{int(val)}',
                va='center', color=TEXT,
                fontsize=10, fontweight='bold')

    ax.set_title('Top Selling Products', color=TEXT,
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Units Sold', labelpad=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, axis='x', alpha=0.3)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'top_products.png')
    plt.savefig(path, dpi=150, bbox_inches='tight',
                facecolor=DARK_BG)
    plt.close()
    print("  top_products.png saved!")

# ── CHART 3: Category Sales Pie ──────────
def chart_category_sales():
    df = get_df("""
        SELECT c.category_name,
               ROUND(SUM(oi.quantity * oi.unit_price),2) AS revenue
        FROM order_items oi
        JOIN products p  ON oi.product_id  = p.product_id
        JOIN categories c ON p.category_id = c.category_id
        GROUP BY c.category_id, c.category_name
        ORDER BY revenue DESC
    """)

    set_dark_style()
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor(DARK_BG)

    wedges, texts, autotexts = ax.pie(
        df['revenue'],
        labels=df['category_name'],
        colors=COLORS[:len(df)],
        autopct='%1.1f%%',
        startangle=90,
        pctdistance=0.82,
        wedgeprops=dict(width=0.6,
                        edgecolor=DARK_BG,
                        linewidth=2)
    )

    for text in texts:
        text.set_color(TEXT)
        text.set_fontsize(11)
    for autotext in autotexts:
        autotext.set_color(DARK_BG)
        autotext.set_fontsize(9)
        autotext.set_fontweight('bold')

    ax.set_title('Category-wise Revenue',
                 color=TEXT, fontsize=16,
                 fontweight='bold', pad=20)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'category_sales.png')
    plt.savefig(path, dpi=150, bbox_inches='tight',
                facecolor=DARK_BG)
    plt.close()
    print("  category_sales.png saved!")

# ── CHART 4: Order Status ────────────────
def chart_order_status():
    df = get_df("""
        SELECT status,
               COUNT(order_id) AS total_orders
        FROM orders
        GROUP BY status
        ORDER BY total_orders DESC
    """)

    status_colors = {
        'delivered':  ACCENT2,
        'shipped':    ACCENT3,
        'processing': ACCENT4,
        'cancelled':  ACCENT
    }
    colors = [status_colors.get(s, ACCENT3)
              for s in df['status']]

    set_dark_style()
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor(DARK_BG)

    bars = ax.bar(df['status'], df['total_orders'],
                  color=colors, width=0.5,
                  edgecolor='none')

    for bar, val in zip(bars, df['total_orders']):
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 2,
                str(int(val)),
                ha='center', color=TEXT,
                fontsize=12, fontweight='bold')

    ax.set_title('Order Status Distribution',
                 color=TEXT, fontsize=16,
                 fontweight='bold', pad=20)
    ax.set_xlabel('Status', labelpad=10)
    ax.set_ylabel('Number of Orders', labelpad=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, axis='y', alpha=0.3)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'order_status.png')
    plt.savefig(path, dpi=150, bbox_inches='tight',
                facecolor=DARK_BG)
    plt.close()
    print("  order_status.png saved!")

# ── RUN ALL CHARTS ───────────────────────
if __name__ == '__main__':
    print("Generating charts...")
    chart_monthly_revenue()
    chart_top_products()
    chart_category_sales()
    chart_order_status()
    print("All charts saved to static/charts/")