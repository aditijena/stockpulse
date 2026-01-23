import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="aditi123",     
    database="stockpulse_db"
)

cursor = conn.cursor()
cursor.execute("SELECT VERSION()")
print(cursor.fetchone())
