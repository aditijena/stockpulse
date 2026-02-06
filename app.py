from db import get_connection
from db import create_user, get_user, get_user_by_username, update_user_profile
from db import fetch_inventory, insert_product, get_user_by_email
from db import store_password_reset_token, validate_reset_token, update_user_password, create_password_reset_table
from db import fetch_sales_trend
import streamlit as st
from signup import signup_page
import numpy as np
from io import StringIO
import pydeck as pdk
import matplotlib.pyplot as plt
from datetime import datetime
from io import BytesIO
import base64
from numpy.random import default_rng as rng
import pandas as pd
import smtplib
import ssl
import secrets
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
def img_to_base64(path):
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()




def calculate_risk(df):
    def risk(row):
        if pd.isna(row["Days Unsold"]):
            return "Low", 0

        if row["Days Unsold"] >= 90:
            return "High", 80
        elif row["Days Unsold"] >= 45:
            return "Medium", 50
        else:
            return "Low", 20

    df[["Risk Level", "Risk Score (%)"]] = df.apply(
        lambda row: pd.Series(risk(row)),
        axis=1
    )
    return df    
def delete_product(product_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
    conn.commit()
    conn.close()

    
st.markdown("""
<style>            
/* Center page content */
.center-page {
    max-width: 1100px;
    margin: 0 auto;
    padding: 24px;
}

/* Card style for risk detail */
.risk-card {
    background: rgba(0,0,0,0.65);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
}

</style>
""", unsafe_allow_html=True)    
st.markdown("""
<style>

.card {
    height: 140px;
    border-radius: 16px;
    padding: 16px;
    color: white;
    background-size: cover;
    background-position: center;
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    transition: all 0.3s ease;
    cursor: pointer;
}

.card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 14px 30px rgba(0,0,0,0.45);
}

.card-title {
    font-size: 14px;
    font-weight: 600;
}

.card-value {
    font-size: 32px;
    font-weight: 700;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)



# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="StockSense Local", page_icon="📦", layout="wide")

# Initialize password reset table on startup
create_password_reset_table()

# Get URL parameters
query_params = st.query_params
reset_token = query_params.get("reset_token", None)
reset_user_id = query_params.get("user_id", None)

# Check if we have a reset token in URL
if reset_token and reset_user_id:
    try:
        import urllib.parse
        
        # Handle list format from query params
        reset_token = reset_token[0] if isinstance(reset_token, list) else reset_token
        reset_user_id = reset_user_id[0] if isinstance(reset_user_id, list) else reset_user_id
        
        # Decode URL-encoded token and strip whitespace
        reset_token = urllib.parse.unquote(reset_token.strip()) if reset_token else None
        reset_user_id = int(reset_user_id)
        
        print(f"DEBUG: Found reset token in URL. User ID: {reset_user_id}, Token length: {len(reset_token) if reset_token else 0}")
        print(f"DEBUG: Token first 30 chars: {reset_token[:30] if reset_token else 'None'}")
    except (ValueError, IndexError, TypeError) as e:
        print(f"DEBUG: Error parsing reset parameters: {e}")
        reset_token = None
        reset_user_id = None

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# ---------------- DUMMY DATA ----------------
inventory_data = fetch_inventory()

# ---------- SESSION STATE INIT ----------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "forgot" not in st.session_state:
    st.session_state.forgot = False

if "reset_password" not in st.session_state:
    st.session_state.reset_password = False

if "reset_token" not in st.session_state:
    st.session_state.reset_token = None

if "reset_user_id" not in st.session_state:
    st.session_state.reset_user_id = None

# If reset token in URL, set session state
if reset_token and reset_user_id:
    st.session_state.reset_password = True
    st.session_state.reset_token = reset_token
    st.session_state.reset_user_id = reset_user_id
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "login"

#------------------SIGNUP PAGE-----------------
elif st.session_state.page == "signup":
    signup_page()

# ---------------- LOGIN PAGE ----------------

st.markdown("""
<style>
/* Remove Streamlit default padding */
[data-testid="stAppViewContainer"] {
    background: none;
}

/* Full background image */
.stApp {
    background-image: url("https://png.pngtree.com/background/20240507/original/pngtree-contemporary-authentic-3d-renderings-of-web-login-page-templates-picture-image_8832124.jpg");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}

/* Center login card */
.login-box {
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    background: rgba(255,255,255,0.12);
    border-radius: 18px;
    padding: 32px;
    max-width: 360px;
    margin: auto;
    margin-top: 18vh;
    box-shadow: 0 30px 60px rgba(0,0,0,0.45);
    border: 1px solid rgba(255,255,255,0.18);
     color: black;
}


</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
/* Center input blocks */
div[data-testid="stTextInput"],
div[data-testid="stPasswordInput"],
div[data-testid="stSelectbox"] {
    width: 320px;
    margin-left: auto;
    margin-right: auto;
}

/* Input box itself */
input {
    text-align: center;
}
/* Center + control width of buttons */
div[data-testid="stButton"] {
    width: 320px;
    margin-left: auto;
    margin-right: auto;
}

/* Make button look clean */
div[data-testid="stButton"] button {
    width: 100%;
    border-radius: 10px;
    padding: 0.6rem;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ============= PASSWORD RESET PAGE =============
if st.session_state.reset_password and st.session_state.reset_token and st.session_state.reset_user_id:
    st.markdown("""
    <div class="login-box">
        <h2 style="text-align:center;">🔐 Reset Password</h2>
        <p style="text-align:center; opacity:0.7;color:white">
            Enter your new password
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='max-width:320px;margin:auto;'>", unsafe_allow_html=True)
    
    # Validate token
    is_valid = validate_reset_token(st.session_state.reset_user_id, st.session_state.reset_token)
    
    if not is_valid:
        st.error("❌ Reset link is invalid or expired. Please request a new one.")
        st.warning(f"DEBUG: Token validation failed for user {st.session_state.reset_user_id}")
        if st.button("Back to Login", key="reset_invalid_back"):
            st.session_state.reset_password = False
            st.session_state.reset_token = None
            st.session_state.reset_user_id = None
            # Clear URL params
            st.query_params.clear()
            st.rerun()
    else:
        st.success("✓ Reset link verified!")
        
        new_password = st.text_input("New Password", type="password", key="reset_new_pass")
        confirm_password = st.text_input("Confirm Password", type="password", key="reset_confirm_pass")
        
        if st.button("Reset Password", use_container_width=True, key="reset_submit"):
            if not new_password or not confirm_password:
                st.error("Please enter both password fields")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                # Update password
                success = update_user_password(st.session_state.reset_user_id, new_password)
                if success:
                    st.success("✅ Password reset successfully!")
                    st.info("Redirecting to login...")
                    st.session_state.reset_password = False
                    st.session_state.reset_token = None
                    st.session_state.reset_user_id = None
                    # Clear URL params
                    st.query_params.clear()
                    import time
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("Failed to reset password. Please try again.")
        
        if st.button("Back to Login", key="reset_back_login", use_container_width=True):
            st.session_state.reset_password = False
            st.session_state.reset_token = None
            st.session_state.reset_user_id = None
            # Clear URL params
            st.query_params.clear()
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

   
if not st.session_state.logged_in:

    st.markdown("""
    <div class="login-box">
        <h2 style="text-align:center;">🔐 StockSense Login</h2>
        <p style="text-align:center; opacity:0.7;color:white">
            Inventory & Dead Stock Analyzer
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='max-width:320px;margin:auto;'>", unsafe_allow_html=True)

    if not st.session_state.forgot:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password",key="login_password")

        if st.button("Login", key="login_btn",use_container_width=True):
            if username and password:
                user = get_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.success(f"Welcome {user['name']}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            else:
                st.error("Please enter username and password")

        if st.button("Forgot Password?",key="forgot_btn"):
            st.session_state.forgot = True
            st.rerun()

    else:
        email = st.text_input("Enter registered email",key="forgot_email")

        if st.button("Send Reset Link", use_container_width=True, key="send_reset"):
            if not email:
                st.error("Please enter your email address")
            else:
                # Get user by email
                user = get_user_by_email(email)
                
                if not user:
                    st.error("No account found with that email address")
                else:
                    # Generate reset token
                    reset_token = secrets.token_urlsafe(32)
                    
                    # Store token in database
                    store_password_reset_token(user['user_id'], reset_token, expiry_minutes=30)
                    
                    # Create reset link (you can add this to session state or database)
                    reset_link = f"http://localhost:8501?reset_token={reset_token}&user_id={user['user_id']}"
                    
                    # Try to send email via SMTP
                    try:
                        # Get SMTP config from environment variables
                        SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
                        SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
                        SMTP_USER = os.environ.get("SMTP_USER", "")
                        SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
                        
                        # If SMTP credentials are not set, show the link for testing
                        if not SMTP_USER or not SMTP_PASSWORD:
                            st.warning("Email service not configured. Reset link for testing:")
                            st.code(reset_link)
                            st.info("In production, set environment variables: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD")
                        else:
                            # Send email
                            sender_email = SMTP_USER
                            receiver_email = email
                            
                            message = MIMEMultipart("alternative")
                            message["Subject"] = "Password Reset Request - StockSense"
                            message["From"] = sender_email
                            message["To"] = receiver_email
                            
                            # Create email body
                            text = f"""
                            Hi {user.get('name', user['username'])},
                            
                            Click the link below to reset your password:
                            {reset_link}
                            
                            If you didn't request this, please ignore this email.
                            
                            Best regards,
                            StockSense Team
                            """
                            
                            html = f"""\
                            <html>
                              <body>
                                <p>Hi {user.get('name', user['username'])},</p>
                                <p>Click the link below to reset your password:</p>
                                <p><a href="{reset_link}">Reset Password</a></p>
                                <p>If you didn't request this, please ignore this email.</p>
                                <p>Best regards,<br>StockSense Team</p>
                              </body>
                            </html>
                            """
                            
                            part1 = MIMEText(text, "plain")
                            part2 = MIMEText(html, "html")
                            message.attach(part1)
                            message.attach(part2)
                            
                            # Send email
                            if SMTP_PORT == 465:
                                context = ssl.create_default_context()
                                with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
                                    server.login(SMTP_USER, SMTP_PASSWORD)
                                    server.sendmail(sender_email, receiver_email, message.as_string())
                            else:
                                with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                                    server.starttls()
                                    server.login(SMTP_USER, SMTP_PASSWORD)
                                    server.sendmail(sender_email, receiver_email, message.as_string())
                            
                            st.success("✓ Password reset link sent to your email! Check your inbox.")
                            
                    except Exception as e:
                        st.error(f"Failed to send email: {str(e)}")
                        st.info("Reset link for testing:")
                        st.code(reset_link)

        if st.button("Back to Login"):
            st.session_state.forgot = False
            st.rerun()
    st.markdown("Don't have an account?")
    if st.button("Sign up", key="goto_signup"):
        st.session_state.page = "signup"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------------- SIDEBAR NAVIGATION ----------------
if st.session_state.get("logged_in"):

    st.sidebar.markdown("""
    <div style="text-align:center;">
        <h2>📦 StockSense</h2>
        <p style="color:gray;">Dead Stock Analyzer</p>
    </div>
    <hr>
    """, unsafe_allow_html=True)

    menu = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Analytics",
            "Product Management",
            "Product Risk Detail",
            "Reports & Export",
            "My Account"
        ]
    )

    st.session_state.page = menu

# ---------------- DASHBOARD ----------------
img_total = img_to_base64("images/total.jpg")
img_risk = img_to_base64("images/risk.jpg")
img_dead = img_to_base64("images/dead.jpg")
img_value = img_to_base64("images/value.jpg")

if st.session_state.page == "Dashboard":
    st.markdown(
    f"""
    <style>
    .stApp {{
         background:
            url("https://images.unsplash.com/photo-1605902711622-cfb43c4437d1");
        background-size: cover;
        background-position: center;
    }}
    </style>
    """,
    unsafe_allow_html=True
)
    

    st.title("📊 Inventory Dashboard")

    
    st.markdown('<div class="block-container css-xxxxx">', unsafe_allow_html=True)


    col1, col2, col3, col4 = st.columns(4)

    # ---------- CARD 1 ----------
    with col1:
        st.markdown(f"""
        <div class="card" style="
            background-image:url('data:image/jpg;base64,{img_total}');
            background-size:cover;
            background-position:center;
            height:140px;
            border-radius:16px;
            padding:16px;
            color:black;
            box-shadow:0 8px 20px rgba(0,0,0,0.3);
        ">
            <div class="card-value" style="font-size:32px;font-weight:700;margin-top:10px;">
                {len(inventory_data)}
            </div>
        </div>
        <div class="card-title" style="font-size:20px;font-weight:600;box-sizing:border-box">📦 Total Products</div>
        """, unsafe_allow_html=True)

    # ---------- CARD 2 ----------
    with col2:
        st.markdown(f"""
        <div class="card" style="
            background-image:url('data:image/jpg;base64,{img_risk}');
            background-size:cover;
            height:140px;
            border-radius:16px;
            padding:16px;
            color:black;
            box-shadow:0 8px 20px rgba(0,0,0,0.3);
        ">
            <div "card-value" style="font-size:32px;font-weight:700;margin-top:10px;">
                {len(inventory_data[inventory_data["Risk Level"]=="Medium"])}
            </div>
        </div>
        <div class="card-title" style="font-size:20px;font-weight:600;">⚠️ At-Risk Items</div>
        """, unsafe_allow_html=True)

    # ---------- CARD 3 ----------
    with col3:
        st.markdown(f"""
        <div class="card" style="
            background-image:url('data:image/jpg;base64,{img_dead}');
            background-size:cover;
            height:140px;
            border-radius:16px;
            padding:16px;
            color:black;
            box-shadow:0 8px 20px rgba(0,0,0,0.3);
        ">
            <div "card-value" style="font-size:32px;font-weight:700;margin-top:10px;">
                {len(inventory_data[inventory_data["Risk Level"]=="High"])}
            </div>
        </div>
        <div class="card-title" style="font-size:20px;font-weight:600;">🚨 Dead Stock</div>
        """, unsafe_allow_html=True)

    # ---------- CARD 4 ----------
    with col4:
        st.markdown(f"""
        <div class="card" style="
            background-image:url('data:image/jpg;base64,{img_value}');
            background-size:cover;
            height:140px;
            border-radius:16px;
            padding:16px;
            box-shadow:0 8px 20px rgba(0,0,0,0.3);
        ">
        </div>
         <div class="card-title" style="font-size:20px;font-weight:600;">💰 Inventory Value at Risk</div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🧭 Risk Overview Table")
    

    st.dataframe(
    inventory_data,
    column_config={
        "product_id": None,  # Hide product ID
        "Product Name": st.column_config.TextColumn(
            "Product Name",
            width="medium"
        ),
        "Category": st.column_config.TextColumn(
            "Category",
            width="small"
        ),

        "Stock Quantity": st.column_config.NumberColumn(
            "Stock",
            help="Current stock available",
            format="%d"
        ),

        "Last Updated": st.column_config.DateColumn(
            "Last Updated",
            help="Last sale date or product added date",
            format="YYYY-MM-DD"
        ),

        "Days Unsold": st.column_config.NumberColumn(
            "Days Unsold",
            help="Number of days since last sale or product added",
            format="%d"
        ),

        "Risk Level": st.column_config.TextColumn(
            "Risk Level",
            width="small"
        ),

        # ✅ THIS IS THE IMPORTANT PART
        "Risk Score (%)": st.column_config.ProgressColumn(
            "Risk Score (%)",
            help="Higher means more risk",
            min_value=0,
            max_value=100,
        ),

        "Suggested Action": st.column_config.TextColumn(
            "Action",
            width="medium"
        ),
    },
    hide_index=True,
    use_container_width=True,
    height=450
)

    # Display refresh timestamp with better styling
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.caption(f"🔄 Last Updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    with col3:
        if st.button("🔁 Refresh", use_container_width=True, key="refresh_table"):
            st.rerun()

# ---------------- ANALYTICS PAGE ----------------
elif st.session_state.page == "Analytics":

    # --- Page-scoped Background (NO UI bleeding) ---
    st.markdown(
        """
        <style>
        .stApp {
            background: url("https://images.unsplash.com/photo-1605902711622-cfb43c4437d1");
            background-size: cover;
            background-position: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("📈 Inventory Analytics")

    # --- Fetch inventory (no risk dependency) ---
    inventory_df = fetch_inventory()

    if inventory_df.empty:
        st.warning("No inventory data available")
        st.stop()

    col1, col2 = st.columns(2)

    # ---------------- LEFT COLUMN ----------------
    with col1:
        st.subheader("📦 Stock Distribution by Category")

        category_summary = (
            inventory_df
            .groupby("Category")["Stock Quantity"]
            .sum()
            .reset_index()
        )

        st.bar_chart(
            category_summary.set_index("Category")["Stock Quantity"]
        )

    # ---------------- RIGHT COLUMN ----------------
    with col2:
        st.subheader("📉 Sales Trend")

        # Fetch real sales trend data from database
        sales_trend_df = fetch_sales_trend()
        
        if sales_trend_df.empty:
            st.info("No sales data available yet")
        else:
            # Display sales trend line chart
            st.line_chart(
                sales_trend_df.set_index("Date")["Total Sales"],
                use_container_width=True
            )

  
    st.markdown("---")
    st.subheader("🗺️ India Activity Map")

    rng = np.random.default_rng(42)

    map_df = pd.DataFrame({
        "lat": rng.standard_normal(500) / 15 + 22.5,   # India latitude
        "lon": rng.standard_normal(500) / 15 + 78.9,   # India longitude
        "size": rng.random(500) * 100
    })

    st.map(map_df, latitude="lat", longitude="lon", size="size")

    st.stop()

# ---------------- PRODUCT MANAGEMENT ----------------
elif st.session_state.page == "Product Management":

    st.markdown(
        """
        <style>
        .stApp {
            background: url("https://images.unsplash.com/photo-1605902711622-cfb43c4437d1");
            background-size: cover;
            background-position: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("📦 Product Management")

    st.markdown(
        """
        <style>
        .pm-container {
            background: rgba(0, 0, 0, 0.8);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            border: 1px solid rgba(0, 212, 255, 0.2);
        }
        .pm-title {
            color: #00d4ff;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 20px;
        }
        .pm-table {
            background: rgba(0, 0, 0, 0.5);
            border-radius: 10px;
            padding: 15px;
            border: 1px solid rgba(0, 212, 255, 0.2);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Create tabs
    tab1, tab2 = st.tabs(["➕ Add Product", "📋 View Products"])
    
    # ============= TAB 1: ADD PRODUCT =============
    with tab1:
        st.markdown(
            "<div class='pm-container'><div class='pm-title'>📦 Add New Product</div>",
            unsafe_allow_html=True
        )
        
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Product Name", placeholder="e.g., Laptop")
                cost = st.number_input("Cost Price", min_value=0, step=1)
            
            with col2:
                category = st.text_input("Category", placeholder="e.g., Electronics")
                price = st.number_input("Selling Price", min_value=0, step=1)
            
            stock = st.number_input("Initial Stock Quantity", min_value=0, step=1)
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
            
            with col_btn1:
                submitted = st.form_submit_button("✅ Add Product", use_container_width=True)
        
        if submitted:
            if name.strip() == "" or category.strip() == "":
                st.error("❌ Product Name and Category are required")
            elif cost <= 0 or price <= 0:
                st.error("❌ Cost and Selling Price must be greater than 0")
            else:
                insert_product(name, category, cost, price, stock)
                st.success("✅ Product added successfully!")
                st.balloons()
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # ============= TAB 2: VIEW PRODUCTS =============
    with tab2:
        st.markdown(
            "<div class='pm-container'><div class='pm-title'>📋 Product List</div>",
            unsafe_allow_html=True
        )
        
        inventory_df = fetch_inventory()
        inventory_data = calculate_risk(inventory_df)
        
        if inventory_data.empty:
            st.warning("📄 No products found. Add a product first.")
        else:
            # Prepare data for table
            table_data = []
            for _, row in inventory_data.iterrows():
                days = int(row.get("Days Unsold", 0))
                risk_level = row['Risk Level']
                
                # Color coding for risk
                if risk_level == "High":
                    risk_display = f"🔴 {risk_level}"
                elif risk_level == "Medium":
                    risk_display = f"🟡 {risk_level}"
                else:
                    risk_display = f"🟢 {risk_level}"
                
                table_data.append({
                    "ID": row['product_id'],
                    "Product Name": row["Product Name"],
                    "Category": row["Category"],
                    "Stock": row["Stock Quantity"],
                    "Days Unsold": days,
                    "Risk Level": risk_display,
                    "Risk Score": f"{int(row.get('Risk Score (%)', 0))}%"
                })
            
            # Display table
            st.markdown("<div class='pm-table'>", unsafe_allow_html=True)
            table_df = pd.DataFrame(table_data)
            
            # Remove ID column from display but keep for delete function
            display_df = table_df.drop(columns=['ID'])
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                height=400
            )
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Delete section
            st.markdown("---")
            st.markdown(
                "<div class='pm-container'><div class='pm-title'>🗑️ Delete Product</div>",
                unsafe_allow_html=True
            )
            
            col_del1, col_del2, col_del3 = st.columns([2, 0.6, 3])
            
            with col_del1:
                product_to_delete = st.selectbox(
                    "Select Product to Delete",
                    options=table_df['ID'].tolist(),
                    format_func=lambda x: table_df[table_df['ID'] == x]['Product Name'].values[0],
                    key="delete_select"
                )
            
            with col_del2:
                if st.button("🗑️ Delete", use_container_width=True):
                    delete_product(int(product_to_delete))
                    st.warning("📋 Product deleted successfully!")
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
# ---------------- PRODUCT RISK DETAIL ----------------
elif st.session_state.page == "Product Risk Detail":
    st.markdown("## 📊 Product Risk Analysis", unsafe_allow_html=True)
    
    # --- Custom CSS for metric cards ---
    st.markdown("""
    <style>
    .stApp {
        background: #000000 !important;
    }
    .metric-card {
        background: rgba(0, 0, 0, 0.6);
        border: 2px solid #00d4ff;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
    }
    .metric-label {
        color: #b0b0b0;
        font-size: 14px;
        margin-bottom: 8px;
    }
    .metric-value {
        color: #00d4ff;
        font-size: 32px;
        font-weight: bold;
        margin: 10px 0;
    }
    .risk-high { color: #ff6b6b; }
    .risk-medium { color: #ffd93d; }
    .risk-low { color: #6bcf7f; }
    .product-info {
        background: rgba(0, 0, 0, 0.5);
        border-left: 4px solid #00d4ff;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
    }
    .risk-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # --- Product selector ---
    product = st.selectbox(
        "📦 Select Product",
        inventory_data["Product Name"].unique(),
        key="risk_product_selector"
    )

    product_data = inventory_data[
        inventory_data["Product Name"] == product
    ].iloc[0]

    # --- Metric Cards Row 1 ---
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📦 Current Stock</div>
            <div class="metric-value">{int(product_data['Stock Quantity'])}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⏳ Days Unsold</div>
            <div class="metric-value">{int(product_data['Days Unsold'])}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🎯 Risk Score</div>
            <div class="metric-value">{int(product_data['Risk Score (%)'])}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        risk_level = product_data['Risk Level']
        risk_class = "risk-high" if risk_level == "High" else "risk-medium" if risk_level == "Medium" else "risk-low"
        risk_icon = "🔴" if risk_level == "High" else "🟡" if risk_level == "Medium" else "🟢"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⚠️ Risk Level</div>
            <div class="metric-value {risk_class}">{risk_icon} {risk_level}</div>
        </div>
        """, unsafe_allow_html=True)

    # --- Product Information ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📋 Product Information")
    
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.markdown(f"""
        <div class="product-info">
            <b>Product Name:</b> {product_data['Product Name']}<br>
            <b>Category:</b> {product_data['Category']}<br>
            <b>Current Stock:</b> {int(product_data['Stock Quantity'])} units
        </div>
        """, unsafe_allow_html=True)
    
    with info_col2:
        st.markdown(f"""
        <div class="product-info">
            <b>Days Without Sale:</b> {int(product_data['Days Unsold'])} days<br>
            <b>Risk Level:</b> {product_data['Risk Level']}<br>
            <b>Last Updated:</b> Today
        </div>
        """, unsafe_allow_html=True)

    # --- Risk Assessment ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🔍 Risk Assessment")
    
    risk_level = product_data['Risk Level']
    suggested_action = product_data['Suggested Action']
    
    if risk_level == "High":
        risk_message = "🚨 **HIGH PRIORITY** - This product requires immediate attention. Consider promotional discount or clearance sale."
        bg_color = "rgba(255, 107, 107, 0.1)"
        border_color = "#ff6b6b"
    elif risk_level == "Medium":
        risk_message = "⚠️ **MEDIUM PRIORITY** - Monitor this product closely. Plan promotional activities or bundling strategies."
        bg_color = "rgba(255, 217, 61, 0.1)"
        border_color = "#ffd93d"
    else:
        risk_message = "✅ **LOW RISK** - This product is performing well. Continue with current strategy."
        bg_color = "rgba(107, 207, 127, 0.1)"
        border_color = "#6bcf7f"
    
    st.markdown(f"""
    <div style="background: {bg_color}; border: 2px solid {border_color}; border-radius: 8px; padding: 15px; margin: 15px 0;">
        {risk_message}<br><br>
        <b>Suggested Action:</b> {suggested_action}
    </div>
    """, unsafe_allow_html=True)

    # --- Risk Score Progress ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📈 Risk Score Analysis")
    
    risk_score = int(product_data['Risk Score (%)'])
    st.progress(risk_score / 100)
    
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.metric("Days Without Sale", int(product_data['Days Unsold']), "days")
    with col_s2:
        st.metric("Units in Stock", int(product_data['Stock Quantity']), "units")
    with col_s3:
        st.metric("Risk Score", f"{risk_score}%", "percentile")

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------- REPORTS & EXPORT ----------------
elif st.session_state.page == "Reports & Export":
    # --- Transparent background ---
    st.markdown(
        """
        <style>
        .stApp {
             background:
                url("https://images.unsplash.com/photo-1605902711622-cfb43c4437d1");
             background-color: rgba(255, 255, 255, 0.0);
            background-size: cover;
            background-position: center;
        }
         /* Make main container transparent */
        .css-18e3th9 {
            background-color: rgba(255, 255, 255, 0.0);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("🗂️ Reports & Export")

    # --- Fetch inventory data ---
    inventory_data = fetch_inventory()  # make sure it has a 'date' column

    # --- Date filters ---
    start = st.date_input("Start Date", datetime.today())
    end = st.date_input("End Date", datetime.today())

    if start > end:
        st.error("End date must be after start date")
        st.stop()

    # --- Filtered DataFrame ---
    if "date" not in inventory_data.columns:
        filtered_data = inventory_data.copy()
    else:
       filtered_data = inventory_data[
       (inventory_data["date"].dt.date >= start) &
       (inventory_data["date"].dt.date <= end)
]

    st.subheader(f"📊 Records from {start} to {end}")
    st.dataframe(filtered_data)

    # --- CSV Export (no openpyxl needed) ---
    csv_buffer = StringIO()
    filtered_data.to_csv(csv_buffer, index=False)

    st.download_button(
          label="💾 Export CSV",
          data=csv_buffer.getvalue().encode("utf-8"),  # Fix: Convert to bytes
          file_name=f"inventory_report_{start}_{end}.csv",
          mime="text/csv"
    )

    # --- Optional: CSV uploader ---
    uploaded_files = st.file_uploader(
        "Upload data", accept_multiple_files=True, type="csv"
    )
#-----------------Router-----------------
def login_page():
    st.title("Login")

def dashboard_page():
    st.title("Dashboard")

def analytics_page():
    st.title("Analytics")

def product_management_page():
    st.title("Product Management")

def product_risk_page():
    st.title("Product Risk Detail")

def reports_page():
    st.title("Reports & Export")

# 🔐 Auth guard
if not st.session_state.logged_in and st.session_state.page not in ["login", "signup"]:
    login_page()
    st.stop()

# 📍 Page routing
if st.session_state.page == "login":
    login_page()

elif st.session_state.page == "signup":
    st.title("📝 Sign Up")

    name = st.text_input("Full Name")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("Create Account", key="signup_btn"):
        if password != confirm:
            st.error("Passwords do not match")
        else:
            create_user(name, username, password)
            st.success("Account created! Please login.")
            st.session_state.page = "login"
            st.rerun()

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()

elif st.session_state.page == "Dashboard":
    dashboard_page()

#------------------ACCOUNT PAGE-------------------

elif st.session_state.page == "My Account":
    st.markdown(
        """
        <style>
        .stApp {
             background:
                url("https://images.unsplash.com/photo-1605902711622-cfb43c4437d1");
             background-color: rgba(255, 255, 255, 0.0);
            background-size: cover;
            background-position: center;
        }
         /* Make main container transparent */
        .css-18e3th9 {
            background-color: rgba(255, 255, 255, 0.0);
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("""
    <style>
    .profile-card {
        background: rgba(0,0,0,0.6);
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
        border-left: 5px solid #00d4ff;
    }
    .info-box {
        background: rgba(255,255,255,0.05);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 1px solid rgba(0,212,255,0.3);
    }
    .section-title {
        color: #00d4ff;
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("👤 My Account")

    user = st.session_state.get("user")

    if not user:
        st.warning("User data not found. Please re-login.")
        st.stop()
    
    # Create tabs for View and Edit
    tab1, tab2 = st.tabs(["📋 View Profile", "✏️ Edit Profile"])
    
    # ============= TAB 1: VIEW PROFILE =============
    with tab1:
        st.markdown(
            f"""
            <div class="profile-card">
                <div class="section-title">👤 Personal Information</div>
                <div class="info-box">
                    <b>Name:</b> {user['name']}
                </div>
                <div class="info-box">
                    <b>Username:</b> {user['username']}
                </div>
                <div class="info-box">
                    <b>Email:</b> {user.get('email', 'Not provided') if user.get('email') else 'Not provided'}
                </div>
                <div class="info-box">
                    <b>Role:</b> <span style="color:#00d4ff;">{user['role'].upper()}</span>
                </div>
                <div class="info-box">
                    <b>Date of Birth:</b> {user['dob'] if user['dob'] else 'Not provided'}
                </div>
            </div>
            """, unsafe_allow_html=True
        )
        
        st.markdown(
            f"""
            <div class="profile-card">
                <div class="section-title">💼 Professional & Contact</div>
                <div class="info-box">
                    <b>Occupation:</b> {user['occupation'] if user['occupation'] else 'Not provided'}
                </div>
                <div class="info-box">
                    <b>Phone:</b> {user['phone'] if user['phone'] else 'Not provided'}
                </div>
            </div>
            """, unsafe_allow_html=True
        )
        
        st.markdown(
            f"""
            <div class="profile-card">
                <div class="section-title">📍 Address & Location</div>
                <div class="info-box">
                    <b>Address:</b> {user['address'] if user['address'] else 'Not provided'}
                </div>
                <div class="info-box">
                    <b>City:</b> {user['city'] if user['city'] else 'Not provided'}
                </div>
                <div class="info-box">
                    <b>State:</b> {user['state'] if user['state'] else 'Not provided'}
                </div>
                <div class="info-box">
                    <b>Country:</b> {user['country'] if user['country'] else 'Not provided'}
                </div>
            </div>
            """, unsafe_allow_html=True
        )
        
        # Account info
        st.markdown(
            f"""
            <div class="profile-card">
                <div class="section-title">ℹ️ Account Details</div>
                <div class="info-box">
                    <b>Member Since:</b> {user['created_at']}
                </div>
            </div>
            """, unsafe_allow_html=True
        )
    
    # ============= TAB 2: EDIT PROFILE =============
    with tab2:
        st.markdown(
            "<div class='profile-card'><div class='section-title'>✏️ Update Your Information</div></div>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='section-title' style='margin-top:20px;margin-bottom:15px;'>👤 Personal Details</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("Full Name", value=user["name"], key="edit_name")
        
        with col2:
            dob = st.date_input("Date of Birth", value=user["dob"] if user["dob"] else None, key="edit_dob")
        
        new_email = st.text_input("Email Address", value=user.get("email", "") or "", key="edit_email")
        
        new_occupation = st.text_input("Occupation", value=user["occupation"] or "", key="edit_occupation")
        
        st.markdown("<div class='section-title' style='margin-top:25px;margin-bottom:15px;'>📞 Contact Information</div>", unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        
        with col3:
            new_phone = st.text_input("Phone Number", value=user["phone"] or "", key="edit_phone")
        
        with col4:
            pass
        
        new_address = st.text_area("Address", value=user["address"] or "", height=100, key="edit_address")
        
        st.markdown("<div class='section-title' style='margin-top:25px;margin-bottom:15px;'>📍 Location</div>", unsafe_allow_html=True)
        col5, col6, col7 = st.columns(3)
        
        with col5:
            new_city = st.text_input("City", value=user["city"] or "", key="edit_city")
        
        with col6:
            new_state = st.text_input("State", value=user["state"] or "", key="edit_state")
        
        with col7:
            new_country = st.text_input("Country", value=user["country"] or "", key="edit_country")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        col_btn1, col_spacer, col_btn2, col_spacer2, col_btn3 = st.columns([1.2, 0.3, 1, 0.3, 1])
        
        with col_btn1:
            if st.button("💾 Save Changes", key="save_btn"):
                # Sanitize inputs
                def _clean(val):
                    if val is None or (isinstance(val, str) and val.strip() == ""):
                        return None
                    return val.strip() if isinstance(val, str) else val
                
                clean_name = _clean(new_name)
                clean_occupation = _clean(new_occupation)
                clean_phone = _clean(new_phone)
                clean_address = _clean(new_address)
                clean_city = _clean(new_city)
                clean_state = _clean(new_state)
                clean_country = _clean(new_country)
                clean_email = _clean(new_email)
                clean_dob = dob.isoformat() if dob else None
                
                conn = get_connection()
                cur = conn.cursor()
                try:
                    cur.execute("""
                        UPDATE users 
                        SET name=%s, email=%s, occupation=%s, phone=%s, address=%s, city=%s, state=%s, country=%s, dob=%s
                        WHERE user_id=%s
                    """, (clean_name, clean_email, clean_occupation, clean_phone, clean_address, clean_city, clean_state, clean_country, clean_dob, user["user_id"]))
                    conn.commit()
                    
                    st.session_state.user.update({
                        "name": clean_name,
                        "email": clean_email,
                        "occupation": clean_occupation,
                        "phone": clean_phone,
                        "address": clean_address,
                        "city": clean_city,
                        "state": clean_state,
                        "country": clean_country,
                        "dob": clean_dob
                    })
                    st.success("✅ Profile updated successfully!")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error updating profile: {str(e)}")
                finally:
                    cur.close()
                    conn.close()
        
        with col_btn2:
            if st.button("🔄 Reset", key="reset_btn"):
                st.rerun()
        
        with col_btn3:
            if st.button("🚪 Logout", key="logout_btn"):
                st.session_state.clear()
                st.rerun()



# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("StockSense Local – Frontend Prototype | MySQL Backend Planned")
