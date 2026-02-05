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
            COALESCE(r.days_unsold, 
                DATEDIFF(CURDATE(), COALESCE(MAX(s.sale_date), p.added_date))
            ) AS 'Days Unsold',
            r.risk_level AS 'Risk Level',
            r.risk_score AS 'Risk Score (%)',
            r.suggested_action AS 'Suggested Action'
        FROM products p
        LEFT JOIN risk_analysis r ON p.product_id = r.product_id
        LEFT JOIN sales s ON p.product_id = s.product_id
        GROUP BY p.product_id
        ORDER BY 'Days Unsold' DESC;
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

def insert_product(name, category, cost, price, stock):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO products
        (product_name, category, cost_price, selling_price,
         initial_stock, current_stock, added_date)
        VALUES (%s, %s, %s, %s, %s, %s,CURDATE())
    """, (name, category, cost, price, stock, stock))

    product_id = cur.lastrowid

    # 2️⃣ Initialize risk_analysis
    cur.execute("""
        INSERT INTO risk_analysis
        (product_id, days_unsold, risk_level, risk_score, suggested_action)
        VALUES (%s, 0, 'Low', 10, 'Normal sales')
    """, (product_id,))

    conn.commit()
    conn.close()

# ---------------- USER AUTH ----------------

def get_user(username, password):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (username, password)
    )
    user = cur.fetchone()

    conn.close()
    return user


import mysql.connector

def create_user(name, username, password, dob, occupation, phone, address, city, state, country):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # sanitize inputs: convert empty strings to None so DB stores NULL
        def _none_if_empty(v):
            if v is None:
                return None
            if isinstance(v, str) and v.strip() == "":
                return None
            return v

        # normalize dob: if it's a date object convert to ISO string, else keep None
        dob_val = dob
        try:
            # handle streamlit date_input which returns datetime.date
            if hasattr(dob, 'isoformat'):
                dob_val = dob.isoformat()
        except Exception:
            dob_val = None

        vals = (
            _none_if_empty(name),
            _none_if_empty(username),
            _none_if_empty(password),
            _none_if_empty(dob_val),
            _none_if_empty(occupation),
            _none_if_empty(phone),
            _none_if_empty(address),
            _none_if_empty(city),
            _none_if_empty(state),
            _none_if_empty(country),
        )

        cur.execute("""
            INSERT INTO users
            (name, username, password, dob, occupation, phone, address, city, state, country)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, vals)

        conn.commit()
        return True, "Account created successfully"

    except mysql.connector.IntegrityError as e:
        conn.rollback()

        # duplicate username
        if "username" in str(e).lower():
            return False, "Username already exists"
        else:
            return False, "Database integrity error"

    except Exception as e:
        conn.rollback()
        return False, f"Error: {str(e)}"

    finally:
        cur.close()
        conn.close()



def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT user_id, name, username, password FROM users WHERE username = %s",
        (username,)
    )

    user = cursor.fetchone()
    conn.close()
    return user


def update_user_name(user_id, new_name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET name = %s WHERE user_id = %s",
        (new_name, user_id)
    )

    conn.commit()
    conn.close()


def update_user_profile(user_id, name, occupation, phone, address):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE users 
            SET name=%s, occupation=%s, phone=%s, address=%s 
            WHERE user_id=%s
        """, (name, occupation, phone, address, user_id))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()


# TEMP FUNCTION - Get all users
def get_all_users():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    
    conn.close()
    return users
