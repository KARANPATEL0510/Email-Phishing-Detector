def get_db_connection():
    try:
        return mysql.connector.connect(host="localhost", user="root", password="rootpassword", database="epd")
    except mysql.connector.Error as err:
        print(f"⚠️ Database connection error: {err}")
        return None