import mysql.connector
import pandas as pd

# ---------------- DB CONNECTION ----------------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="ASQL$1623",     # change if needed
        database="stockpulse_db"
    )

# ---------------- FETCH INVENTORY ----------------
def fetch_inventory():
    conn = get_connection()
    query = """
       SELECT
            p.product_id AS product_id,
            p.product_name AS 'Product Name',
            p.category AS 'Category',
            p.current_stock AS 'Stock Quantity',
            r.days_unsold AS 'Days Unsold',
            r.risk_level AS 'Risk Level',
            r.risk_score AS 'Risk Score (%)',
            r.suggested_action AS 'Suggested Action'
        FROM products p
        LEFT JOIN risk_analysis r
        ON p.product_id = r.product_id;

    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ---------------- ADD PRODUCT ----------------
def calculate_risk(stock):
    # Your logic to determine score and level
    if stock > 50:
        risk_score = 10
        risk_level = "Low"
    else:
        risk_score = 80
        risk_level = "High"
        
    return risk_level, risk_score  # <--- MUST return both separated by a comma

def calculate_inventory_risk(df):
    # This logic applies the risk calculation to every row in your dataframe
    # Assuming 'Stock Quantity' is the column name
    df['Risk Level'] = df['Stock Quantity'].apply(lambda x: "High" if x < 10 else "Low")
    return df

    return df  
def insert_product(name, category, cost, price, stock):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO products
        (product_name, category, cost_price, selling_price, initial_stock, current_stock)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (name, category, cost, price, stock, stock))

    conn.commit()
    conn.close()
