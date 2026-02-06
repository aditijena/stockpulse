"""
Migration script to create the password_resets table
Run this if the table doesn't get created automatically
"""

from db import create_password_reset_table

if __name__ == "__main__":
    print("Creating password_resets table...")
    success = create_password_reset_table()
    if success:
        print("✓ Successfully created password_resets table!")
    else:
        print("✗ Failed to create table. Check your database connection.")
