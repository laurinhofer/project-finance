from db import get_connection
from models import Benutzer

def main():
    print("Finanzplaner gestartet")

    connection = get_connection()
    if not connection:
        print("Verbindung fehlgeschlagen")
        return

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM benutzer;")
    rows = cursor.fetchall()

    for row in rows:
        benutzer = Benutzer(*row)
        print(benutzer)

    connection.close()

if __name__ == "__main__":
    main()
