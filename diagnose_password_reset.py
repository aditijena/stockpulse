"""
Password Reset Diagnostic Script - Comprehensive Debug
"""

import secrets
from db import get_connection, get_user_by_email
from datetime import datetime, timedelta

def check_database_setup():
    """Check if database and tables are properly set up"""
    print("=" * 70)
    print("1. DATABASE SETUP CHECK")
    print("=" * 70)
    
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    
    # Check if password_resets table exists
    cur.execute("""
        SELECT COUNT(*) as count
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = 'password_resets'
    """)
    result = cur.fetchone()
    print(f"✓ password_resets table exists: {result['count'] > 0}")
    
    # Check table structure
    if result['count'] > 0:
        cur.execute("DESCRIBE password_resets")
        columns = cur.fetchall()
        print("\n  Table structure:")
        for col in columns:
            print(f"    - {col['Field']}: {col['Type']}")
    
    # Check for existing password reset records
    cur.execute("SELECT COUNT(*) as count FROM password_resets")
    count = cur.fetchone()['count']
    print(f"\n✓ Existing password reset records: {count}")
    
    cur.close()
    conn.close()
    print()

def test_storage_and_retrieval():
    """Test storing and retrieving tokens"""
    print("=" * 70)
    print("2. TOKEN STORAGE & RETRIEVAL TEST")
    print("=" * 70)
    
    # Get a test user
    email = input("\nEnter test user email: ").strip()
    
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    
    # Get user
    cur.execute("SELECT user_id, name FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    
    if not user:
        print(f"❌ No user found with email: {email}")
        cur.close()
        conn.close()
        return
    
    user_id = user['user_id']
    print(f"✓ Found user: {user['name']} (ID: {user_id})")
    
    # Clear old tokens for this user
    cur.execute("DELETE FROM password_resets WHERE user_id = %s", (user_id,))
    conn.commit()
    print("✓ Cleared old tokens")
    
    # Generate new token
    token = secrets.token_urlsafe(32)
    print(f"\n✓ Generated token: {token}")
    print(f"  Token length: {len(token)}")
    print(f"  Token type: {type(token)}")
    
    # Store token
    expiry = datetime.now() + timedelta(minutes=30)
    cur.execute("""
        INSERT INTO password_resets (user_id, token, expires_at)
        VALUES (%s, %s, %s)
    """, (user_id, token, expiry))
    conn.commit()
    print("✓ Token stored in database")
    
    # Retrieve and verify
    cur.execute("""
        SELECT token, expires_at FROM password_resets 
        WHERE user_id = %s
    """, (user_id,))
    stored = cur.fetchone()
    
    if stored:
        print(f"\n✓ Retrieved from DB:")
        print(f"  Stored token: {stored['token']}")
        print(f"  Stored token length: {len(stored['token'])}")
        print(f"  Exact match: {stored['token'] == token}")
        print(f"  Expires at: {stored['expires_at']}")
        
        # Test various comparison scenarios
        print(f"\n  Comparison tests:")
        print(f"    - Direct match: {stored['token'] == token}")
        print(f"    - After strip: {stored['token'].strip() == token.strip()}")
        
        # Test URL encoding simulation
        import urllib.parse
        encoded = urllib.parse.quote(token)
        decoded = urllib.parse.unquote(encoded)
        print(f"    - URL encoded match: {decoded == token}")
        
    else:
        print("❌ Token not found after storing!")
    
    # Test validation query
    print(f"\n  Validation query test:")
    cur.execute("""
        SELECT * FROM password_resets 
        WHERE user_id = %s AND token = %s AND expires_at > NOW()
    """, (user_id, token))
    validation = cur.fetchone()
    print(f"    - Validation passes: {validation is not None}")
    
    # Create reset link
    reset_link = f"http://localhost:8501?reset_token={token}&user_id={user_id}"
    print(f"\n✓ Reset link created:")
    print(f"  {reset_link}")
    
    cur.close()
    conn.close()
    print()

def test_url_parameter_extraction():
    """Test URL parameter extraction"""
    print("=" * 70)
    print("3. URL PARAMETER EXTRACTION TEST")
    print("=" * 70)
    
    import urllib.parse
    
    # Get test data
    email = input("\nEnter test user email: ").strip()
    
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT user_id FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    
    if not user:
        print(f"❌ No user found with email: {email}")
        return
    
    user_id = user['user_id']
    token = secrets.token_urlsafe(32)
    
    # Create URL
    url = f"http://localhost:8501?reset_token={token}&user_id={user_id}"
    print(f"\n✓ Created URL: {url}")
    
    # Parse parameters
    parsed = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed.query)
    
    print(f"\n✓ Parsed parameters:")
    for key, value in params.items():
        print(f"  {key}: {value}")
    
    # Extract like Streamlit would
    reset_token = params.get("reset_token", [None])[0]
    reset_user_id = params.get("user_id", [None])[0]
    
    print(f"\n✓ After extraction (Streamlit style):")
    print(f"  reset_token type: {type(reset_token)}")
    print(f"  reset_token value: {reset_token}")
    print(f"  reset_token length: {len(reset_token) if reset_token else 0}")
    print(f"  reset_user_id: {reset_user_id}")
    
    # Test stripping
    if reset_token:
        stripped = reset_token.strip()
        print(f"\n✓ After strip():")
        print(f"  Stripped token: {stripped}")
        print(f"  Same as original: {stripped == reset_token}")
    
    print()

def test_full_flow():
    """Test the complete password reset flow"""
    print("=" * 70)
    print("4. FULL FLOW TEST (Generate → Store → Validate)")
    print("=" * 70)
    
    from db import store_password_reset_token, validate_reset_token
    
    email = input("\nEnter test user email: ").strip()
    
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT user_id FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    
    if not user:
        print(f"❌ No user found with email: {email}")
        return
    
    user_id = user['user_id']
    
    # Generate token
    token = secrets.token_urlsafe(32)
    print(f"\n✓ Step 1 - Generated token: {token[:20]}...")
    
    # Store token
    success = store_password_reset_token(user_id, token, expiry_minutes=30)
    print(f"✓ Step 2 - Store result: {success}")
    
    # Validate token
    is_valid = validate_reset_token(user_id, token)
    print(f"✓ Step 3 - Validation result: {is_valid}")
    
    if not is_valid:
        print("\n❌ VALIDATION FAILED - Check the debug output above")
    else:
        print("\n✅ FULL FLOW SUCCESSFUL")
    
    print()

def main():
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "PASSWORD RESET DIAGNOSTIC TOOL" + " " * 23 + "║")
    print("╚" + "=" * 68 + "╝")
    
    try:
        while True:
            print("\nDIAGNOSTIC MENU:")
            print("  1. Check database setup")
            print("  2. Test token storage & retrieval")
            print("  3. Test URL parameter extraction")
            print("  4. Test full flow (generate → store → validate)")
            print("  5. Run all tests")
            print("  0. Exit")
            
            choice = input("\nSelect option (0-5): ").strip()
            
            if choice == "1":
                check_database_setup()
            elif choice == "2":
                test_storage_and_retrieval()
            elif choice == "3":
                test_url_parameter_extraction()
            elif choice == "4":
                test_full_flow()
            elif choice == "5":
                check_database_setup()
                test_storage_and_retrieval()
                test_url_parameter_extraction()
                test_full_flow()
            elif choice == "0":
                print("\nExiting...")
                break
            else:
                print("Invalid option")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
