import mysql.connector
import pandas as pd
from datetime import datetime



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
            COALESCE(
                (SELECT MAX(s.sale_date) FROM sales s WHERE s.product_id = p.product_id),
                p.added_date
            ) AS 'Last Updated',
            DATEDIFF(CURDATE(), COALESCE(
                (SELECT MAX(s.sale_date) FROM sales s WHERE s.product_id = p.product_id),
                p.added_date
            )) AS 'Days Unsold',
            r.risk_level AS 'Risk Level',
            r.risk_score AS 'Risk Score (%)',
            r.suggested_action AS 'Suggested Action'
        FROM products p
        LEFT JOIN risk_analysis r ON p.product_id = r.product_id
        ORDER BY 'Days Unsold' DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def fetch_sales_trend():
    """Fetch sales trend data grouped by date"""
    conn = get_connection()
    query = """
        SELECT 
            s.sale_date AS 'Date',
            SUM(s.quantity_sold) AS 'Total Sales',
            COUNT(DISTINCT s.product_id) AS 'Products Sold'
        FROM sales s
        WHERE s.sale_date IS NOT NULL
        GROUP BY s.sale_date
        ORDER BY s.sale_date DESC
        LIMIT 30
    """
    try:
        df = pd.read_sql(query, conn)
        conn.close()
        if df.empty:
            # Return empty dataframe with correct columns
            return pd.DataFrame(columns=['Date', 'Total Sales', 'Products Sold'])
        # Sort by date ascending for trend visualization
        df = df.sort_values('Date')
        return df
    except Exception as e:
        print(f"Error fetching sales trend: {e}")
        conn.close()
        return pd.DataFrame(columns=['Date', 'Total Sales', 'Products Sold'])


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

def create_user(name, username, email, password, dob, occupation, phone, address, city, state, country):
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
            _none_if_empty(email),
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
            (name, username, email, password, dob, occupation, phone, address, city, state, country)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
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


def delete_user_by_username(username):
    """Delete a user and related password reset tokens by username.

    Returns (True, message) on success or (False, error_message) on failure.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        # find user
        cur.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        if not row:
            return False, "User not found"

        user_id = row["user_id"]

        # delete password reset tokens for this user
        cur.execute("DELETE FROM password_resets WHERE user_id = %s", (user_id,))

        # delete user
        cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))

        conn.commit()
        return True, f"Deleted user '{username}' (id={user_id}) and related tokens"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
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


def get_user_by_email(email):
    """Get user by email address"""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        return user
    except Exception as e:
        print(f"Error fetching user by email: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def store_password_reset_token(user_id, token, expiry_minutes=30):
    """Store password reset token for user"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Clean the token: strip whitespace and decode URL encoding
        import urllib.parse
        token = urllib.parse.unquote(token.strip()) if token else token
        
        # First ensure table exists
        create_password_reset_table()
        
        # Delete old tokens for this user
        cur.execute("DELETE FROM password_resets WHERE user_id = %s", (user_id,))
        
        # Insert new token
        cur.execute("""
            INSERT INTO password_resets (user_id, token, expires_at)
            VALUES (%s, %s, DATE_ADD(NOW(), INTERVAL %s MINUTE))
        """, (user_id, token, expiry_minutes))
        
        conn.commit()
        print(f"✅ Reset token stored for user {user_id}")
        print(f"   Token length: {len(token)}")
        print(f"   Token first 30 chars: {token[:30]}")
        print(f"   Expires in {expiry_minutes} minutes")
        return True
    except Exception as e:
        print(f"❌ Error storing reset token: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()


def validate_reset_token(user_id, token):
    """Check if reset token is valid and not expired"""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        # Strip whitespace and handle URL encoding
        import urllib.parse
        
        token = token.strip() if token else None
        if not token:
            print("Token is empty")
            return False
        
        # Try to decode if it looks URL encoded
        try:
            decoded_token = urllib.parse.unquote(token)
            if decoded_token != token:
                print(f"Token was URL encoded. Decoded from: {token[:20]}... to: {decoded_token[:20]}...")
                token = decoded_token
        except:
            pass
        
        # First check if table exists (use alias so dictionary cursor returns a predictable key)
        cur.execute("""
            SELECT COUNT(*) AS cnt
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'password_resets'
        """)
        row = cur.fetchone()
        # Support both dict-row and tuple-row depending on cursor settings
        try:
            count = row['cnt'] if isinstance(row, dict) and 'cnt' in row else row[0]
        except Exception:
            count = 0

        if count == 0:
            print("password_resets table does not exist")
            return False
        
        # Debug: Check all tokens for this user
        cur.execute("SELECT token, expires_at FROM password_resets WHERE user_id = %s", (user_id,))
        stored_tokens = cur.fetchall()
        print(f"Tokens in DB for user {user_id}: {len(stored_tokens)} records")
        for i, record in enumerate(stored_tokens):
            print(f"  Record {i+1}:")
            print(f"    Stored token: '{record['token'][:30]}...' (len={len(record['token'])})")
            print(f"    Provided token: '{token[:30]}...' (len={len(token)})")
            print(f"    Match: {record['token'] == token}")
            print(f"    Expires: {record['expires_at']}")
            print(f"    Expired: {record['expires_at'] < datetime.now()}")
        
        # Validate token
        cur.execute("""
            SELECT * FROM password_resets 
            WHERE user_id = %s AND token = %s AND expires_at > NOW()
        """, (user_id, token))
        
        result = cur.fetchone()
        if result:
            print(f"✅ Token validated successfully for user {user_id}")
            return True
        else:
            print(f"❌ Token validation failed for user {user_id}")
            # Check if token exists but is expired
            cur.execute("""
                SELECT * FROM password_resets 
                WHERE user_id = %s AND token = %s
            """, (user_id, token))
            expired_result = cur.fetchone()
            if expired_result:
                print(f"   Reason: Token exists but is EXPIRED (expired at {expired_result['expires_at']})")
            else:
                print(f"   Reason: Token NOT FOUND in database")
            return False
    except Exception as e:
        print(f"Error validating token: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cur.close()
        conn.close()


def update_user_password(user_id, new_password):
    """Update user password"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        # First check if user exists
        cur.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        if not cur.fetchone():
            print(f"User {user_id} not found")
            return False
        
        # Update password
        cur.execute("UPDATE users SET password = %s WHERE user_id = %s", (new_password, user_id))
        
        # Delete used reset tokens
        cur.execute("DELETE FROM password_resets WHERE user_id = %s", (user_id,))
        
        conn.commit()
        print(f"Password updated successfully for user {user_id}")
        return True
    except Exception as e:
        print(f"Error updating password: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()


def create_password_reset_table():
    """Create password_resets table if it doesn't exist"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS password_resets (
                reset_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                token VARCHAR(255) NOT NULL UNIQUE,
                expires_at DATETIME NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating password_resets table: {e}")
        return False
    finally:
        cur.close()
        conn.close()

