import streamlit as st
from db import create_user

def signup_page():
    st.title("📝 Create Account")

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

    name = st.text_input("Full Name")
    username = st.text_input("Username")
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    dob = st.date_input("Date of Birth")
    occupation = st.text_input("Occupation")
    phone = st.text_input("Phone Number")

    address = st.text_area("Address")
    city = st.text_input("City")
    state = st.text_input("State")
    country = st.text_input("Country")

    if st.button("Create Account"):
        if not name or not username or not password:
            st.error("Name, Username and Password are required")
            st.stop()

        if password != confirm:
            st.error("Passwords do not match")
            st.stop()

        # 🔴 IMPORTANT FIX: handle DB response
        success, msg = create_user(
            name, username, email, password,
            dob, occupation, phone,
            address, city, state, country
        )

        if success:
            st.success(msg)
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error(msg)

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()

    st.stop()
