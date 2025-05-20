from mysql.connector import connect, Error

def get_connection():
    try:
        connection = connect(
            host="localhost",
            user="root",
            password="",
            database="project-finance"
        )
        return connection
    except Error as e:
        print(f"Verbindungsfehler: {e}")
        return None
