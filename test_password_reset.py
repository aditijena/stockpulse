"""
Test script for password reset functionality
"""

import secrets
from db import (
    store_password_reset_token,
    validate_reset_token,
    get_connection,
    get_user_by_email
)

def test_password_reset():
    """Test the password reset flow"""
    
    print("=" * 60)
    print("PASSWORD RESET FLOW TEST")
    print("=" * 60)
    
    # Step 1: Get a test user
    email = input("Enter test user email: ").strip()
    
    user = get_user_by_email(email)
    if not user:
        print(f"❌ No user found with email: {email}")
        return
    
    user_id = user['user_id']
    print(f"\n✅ Found user: {user['name']} (ID: {user_id})")
    
    # Step 2: Generate and store token
    print("\n--- Step 1: Generating Reset Token ---")
    reset_token = secrets.token_urlsafe(32)
    print(f"Generated token: {reset_token}")
    print(f"Token length: {len(reset_token)}")
    
    # Step 3: Store token in database
    print("\n--- Step 2: Storing Token in Database ---")
    success = store_password_reset_token(user_id, reset_token, expiry_minutes=30)
    if success:
        print("✅ Token stored successfully")
    else:
        print("❌ Failed to store token")
        return
    
    # Step 4: Verify token is in database
    print("\n--- Step 3: Verifying Token in Database ---")
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT token, expires_at FROM password_resets WHERE user_id = %s", (user_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    
    if result:
        stored_token = result['token']
        print(f"Stored token in DB: {stored_token}")
        print(f"Stored token length: {len(stored_token)}")
        print(f"Token match: {stored_token == reset_token}")
        print(f"Expires at: {result['expires_at']}")
    else:
        print("❌ No token found in database!")
        return
    
    # Step 5: Test validation with original token
    print("\n--- Step 4: Testing Token Validation (Original) ---")
    is_valid = validate_reset_token(user_id, reset_token)
    if is_valid:
        print("✅ Token validation PASSED")
    else:
        print("❌ Token validation FAILED")
    
    # Step 6: Test validation with stripped token
    print("\n--- Step 5: Testing Token Validation (Stripped) ---")
    stripped_token = reset_token.strip()
    is_valid = validate_reset_token(user_id, stripped_token)
    if is_valid:
        print("✅ Token validation PASSED")
    else:
        print("❌ Token validation FAILED")
    
    # Step 7: Create reset link
    print("\n--- Step 6: Creating Reset Link ---")
    reset_link = f"http://localhost:8501?reset_token={reset_token}&user_id={user_id}"
    print(f"Reset link:\n{reset_link}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_password_reset()
