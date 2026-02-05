from db import get_connection
from db import create_user, get_user, get_user_by_username, update_user_profile
from db import fetch_inventory, insert_product
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
            st.experimental_rerun()

    else:
        email = st.text_input("Enter registered email",key="forgot_email")

        if st.button("Send Reset Link", use_container_width=True, key="send_reset"):
            st.success("Password reset link sent")

        if st.button("Back to Login"):
            st.session_state.forgot = False
            st.experimental_rerun()
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
        "Product Name": st.column_config.TextColumn("Product"),
        "Category": st.column_config.TextColumn("Category"),

        "Stock Quantity": st.column_config.NumberColumn(
            "Stock",
            help="Current stock available",
            format="%d"
        ),

        "Days Unsold": st.column_config.NumberColumn(
            "Days Unsold",
            help="Number of days product has not sold",
            format="%d days"
        ),

        "Risk Level": st.column_config.TextColumn(
            "Risk Level"
        ),

        # ✅ THIS IS THE IMPORTANT PART
        "Risk Score (%)": st.column_config.ProgressColumn(
            "Risk Score (%)",
            help="Higher means more risk",
            min_value=0,
            max_value=100,

        ),

        "Suggested Action": st.column_config.TextColumn(
            "Suggested Action"
        ),
    },
    hide_index=True,
    use_container_width=True
)

    st.caption(f"Last refresh: {pd.Timestamp.now()}")

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

        sales_demo = {
            "Jan": 120,
            "Feb": 100,
            "Mar": 90,
            "Apr": 60,
            "May": 40
        }

        sales_df = pd.DataFrame.from_dict(
            sales_demo, orient="index", columns=["Sales"]
        )

        st.line_chart(sales_df)

  
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

    # ---------- ADD PRODUCT ----------
    st.subheader("➕ Add Product")

    with st.form("add_product_form"):
        name = st.text_input("Product Name")
        category = st.text_input("Category")

        col1, col2, col3 = st.columns(3)
        with col1:
            cost = st.number_input("Cost Price", min_value=0)
        with col2:
            price = st.number_input("Selling Price", min_value=0)
        with col3:
            stock = st.number_input("Initial Stock", min_value=0)

        submitted = st.form_submit_button("Add Product")

    if submitted:
        if name.strip() == "" or category.strip() == "":
            st.error("Product Name and Category are required")
        else:
            insert_product(name, category, cost, price, stock)
            st.success("Product added successfully")
            st.rerun()

    # ---------- PRODUCT LIST ----------
    st.markdown("---")
    st.subheader("📋 Product List")

    inventory_df = fetch_inventory()
    inventory_data = calculate_risk(inventory_df)

    # Header
    h1, h2, h3, h4, h5 = st.columns([3, 2, 2, 2, 1])
    h1.markdown("**Product**")
    h2.markdown("**Category**")
    h3.markdown("**Stock**")
    h4.markdown("**Risk**")
    h5.markdown("**Delete**")

    for _, row in inventory_data.iterrows():
        c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 1])

        c1.write(row["Product Name"])
        c2.write(row["Category"])
        c3.write(row["Stock Quantity"])
        
        
        with c4:
            # Get the score (default to 0 if missing)
            score = float(row.get("Risk Score", 0))
            
            progress_val = np.clip(score / 100, 0.0, 1.0)
           
            st.write(f"**{row['Risk Level']}**")
            st.progress(progress_val)

        # Delete Button
        if c5.button("🗑️", key=f"del_{int(row['product_id'])}"):
            delete_product(int(row["product_id"]))
            st.warning("Product deleted")
            st.rerun()
# ---------------- PRODUCT RISK DETAIL ----------------
elif st.session_state.page == "Product Risk Detail":
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
    st.markdown('<div class="center-page">', unsafe_allow_html=True)

    st.markdown("## 📌 Product Risk Detail", unsafe_allow_html=True)

    # --- Product selector ---
    product = st.selectbox(
        "Select Product",
        inventory_data["Product Name"].unique()
    )

    product_data = inventory_data[
        inventory_data["Product Name"] == product
    ].iloc[0]

    # --- Info cards ---
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="risk-card">
            <h4>📦 Stock</h4>
            <h2>{product_data['Stock Quantity']}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="risk-card">
            <h4>⏳ Days Unsold</h4>
            <h2>{product_data['Days Unsold']}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="risk-card">
            <h4>⚠️ Risk Level</h4>
            <h2>{product_data['Risk Level']}</h2>
        </div>
        """, unsafe_allow_html=True)

    # --- Detailed info ---
    st.markdown(f"""
    <div class="risk-card">
        <h4>📊 Risk Score</h4>
        <progress value="{product_data['Risk Score (%)']}" max="100"></progress>
        <p style="margin-top:12px;">
            Suggested Action: <b>{product_data['Suggested Action']}</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

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
    st.title("👤 My Account")

    user = st.session_state.get("user")

    if not user:
        st.warning("User data not found. Please re-login.")
        st.stop()

    st.subheader("📄 Profile Information")

    st.write("**Name:**", user["name"])
    st.write("**Username:**", user["username"])
    st.write("**Role:**", user["role"])
    st.write("**Date of Birth:**", user["dob"])
    st.write("**Occupation:**", user["occupation"])
    st.write("**Phone:**", user["phone"])
    st.write("**Address:**", user["address"])
    st.write("**City:**", user["city"])
    st.write("**State:**", user["state"])
    st.write("**Country:**", user["country"])

    st.markdown("---")
    st.subheader("✏️ Edit Profile")

    new_name = st.text_input("Full Name", value=user["name"])
    new_occupation = st.text_input("Occupation", value=user["occupation"])
    new_phone = st.text_input("Phone", value=user["phone"])
    new_address = st.text_area("Address", value=user["address"])

    if st.button("Update Profile"):
        update_user_profile(
            user["user_id"],
            new_name,
            new_occupation,
            new_phone,
            new_address
        )

        st.session_state.user.update({
            "name": new_name,
            "occupation": new_occupation,
            "phone": new_phone,
            "address": new_address
        })

        st.success("Profile updated")

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()



# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("StockSense Local – Frontend Prototype | MySQL Backend Planned")
