"""
Quick Password Reset Test - Run this to verify the fix
"""

import secrets
from db import get_connection, get_user_by_email, store_password_reset_token, validate_reset_token

def quick_test():
    """Quick test of password reset functionality"""
    
    print("\n" + "=" * 60)
    print("PASSWORD RESET - QUICK TEST")
    print("=" * 60)
    
    # Get user
    email = input("\nEnter your test user email: ").strip()
    
    user = get_user_by_email(email)
    if not user:
        print(f"❌ No user found with email: {email}")
        return False
    
    user_id = user['user_id']
    print(f"✓ Found user: {user['name']} (ID: {user_id})")
    
    # Generate token
    token = secrets.token_urlsafe(32)
    print(f"\n✓ Generated token: {token[:30]}...")
    
    # Store token
    print("\nStoring token in database...")
    success = store_password_reset_token(user_id, token, expiry_minutes=30)
    if not success:
        print("❌ Failed to store token")
        return False
    
    # Validate immediately
    print("\nValidating token...")
    is_valid = validate_reset_token(user_id, token)
    
    print("\n" + "=" * 60)
    if is_valid:
        print("✅ SUCCESS! Password reset flow works!")
        print("\nYour reset link:")
        print(f"http://localhost:8501?reset_token={token}&user_id={user_id}")
        return True
    else:
        print("❌ FAILED! Token validation did not pass")
        print("Check the debug output above for more details")
        return False

if __name__ == "__main__":
    try:
        result = quick_test()
        print("=" * 60 + "\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
