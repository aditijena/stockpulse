from db import get_connection


def main():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'users'
              AND COLUMN_NAME = 'email'
        """)
        cnt = cur.fetchone()[0]
        if cnt > 0:
            print("Column 'email' already exists on users table.")
            return

        cur.execute("ALTER TABLE users ADD COLUMN email VARCHAR(255)")
        conn.commit()
        print("Added column 'email' to users table.")
    except Exception as e:
        print("Error adding column:", e)
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


if __name__ == '__main__':
    main()
