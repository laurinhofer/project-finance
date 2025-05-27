from db import get_connection
from models import Benutzer, Transaktion
import datetime

def registriere_benutzer(conn):
    print("\n--- Benutzer registrieren ---")
    name = input("Benutzername: ")
    email = input("E-Mail: ")
    passwort = input("Passwort: ")

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO benutzer (name, email, passwort) VALUES (%s, %s, %s)",
        (name, email, passwort)
    )
    conn.commit()

    print("Registrierung erfolgreich!")
    return Benutzer(cursor.lastrowid, name, email)

def login_benutzer(conn):
    print("\n--- Benutzer Login ---")
    email = input("E-Mail: ")
    passwort = input("Passwort: ")

    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM benutzer WHERE email = %s AND passwort = %s",
        (email, passwort)
    )
    row = cursor.fetchone()
    if row:
        print("Login erfolgreich!")
        return Benutzer(row[0], row[1], row[2])
    else:
        print("Login fehlgeschlagen.")
        return None

def transaktion_hinzufuegen(conn, benutzer):
    print("\n--- Neue Transaktion hinzufügen ---")
    try:
        betrag = float(input("Betrag (€): "))
    except ValueError:
        print("Ungültiger Betrag.")
        return
    datum = input("Datum (YYYY-MM-DD): ") or datetime.date.today().isoformat()
    kategorie = input("Kategorie: ")
    typ = input("Typ (Einnahme/Ausgabe): ")
    beschreibung = input("Beschreibung (optional): ")

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transaktionen (benutzer_id, betrag, datum, kategorie, typ, beschreibung) VALUES (%s, %s, %s, %s, %s, %s)",
        (benutzer.id, betrag, datum, kategorie, typ, beschreibung)
    )
    conn.commit()
    print("Transaktion hinzugefügt.")

def transaktion_loeschen(conn, benutzer):
    print("\n--- Transaktion löschen ---")
    id = input("Gib die ID der zu löschenden Transaktion ein: ")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transaktionen WHERE id = %s AND benutzer_id = %s", (id, benutzer.id))
    conn.commit()
    print("Transaktion gelöscht (falls vorhanden).")

def transaktions_uebersicht(conn, benutzer):
    print("\n--- Transaktionsübersicht ---")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, betrag, datum FROM transaktionen WHERE benutzer_id = %s ORDER BY datum DESC",
        (benutzer.id,)
    )
    rows = cursor.fetchall()

    if not rows:
        print("Keine Transaktionen gefunden.")
        return

    for row in rows:
        print(f"ID: {row[0]}, Betrag: {row[1]} €, Datum: {row[2]}")

    auswahl = input("Gib eine ID ein, um Details zu sehen (Enter zum Überspringen): ")
    if auswahl:
        cursor.execute("SELECT * FROM transaktionen WHERE id = %s AND benutzer_id = %s", (auswahl, benutzer.id))
        row = cursor.fetchone()
        if row:
            trans = Transaktion(*row)
            print(f"""
--- Transaktionsdetails ---
ID:           {trans.id}
Betrag:       {trans.betrag} €
Datum:        {trans.datum}
Kategorie:    {trans.kategorie}
Typ:          {trans.typ}
Beschreibung: {trans.beschreibung if trans.beschreibung else "-"}
----------------------------
""")
        else:
            print("Keine Transaktion mit dieser ID gefunden.")

def hauptmenue(conn, benutzer):
    while True:
        print(f"\nEingeloggt als: {benutzer.name} ({benutzer.email})")
        print("1. Transaktion hinzufügen")
        print("2. Transaktion löschen")
        print("3. Transaktionen anzeigen")
        print("4. Logout")

        wahl = input("Auswahl: ")

        if wahl == "1":
            transaktion_hinzufuegen(conn, benutzer)
        elif wahl == "2":
            transaktion_loeschen(conn, benutzer)
        elif wahl == "3":
            transaktions_uebersicht(conn, benutzer)
        elif wahl == "4":
            print("Logout...")
            break
        else:
            print("Ungültige Eingabe.")

def main():
    print("Finanzplaner gestartet")

    conn = get_connection()
    if not conn:
        print("Verbindung zur Datenbank fehlgeschlagen.")
        return

    while True:
        print("\n1. Registrieren")
        print("2. Login")
        print("3. Beenden")
        auswahl = input("Auswahl: ")

        if auswahl == "1":
            benutzer = registriere_benutzer(conn)
            hauptmenue(conn, benutzer)
        elif auswahl == "2":
            benutzer = login_benutzer(conn)
            if benutzer:
                hauptmenue(conn, benutzer)
        elif auswahl == "3":
            print("Programm beendet.")
            break
        else:
            print("Ungültige Eingabe.")

    conn.close()

if __name__ == "__main__":
    main()
