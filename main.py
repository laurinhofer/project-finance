import datetime
from db import get_connection
from models import Benutzer, Transaktion

def registriere_benutzer(conn):
    print("\n📝 --- Registrierung ---")
    name = input("👤 Name: ")
    
    while True:
        email = input("📧 E-Mail: ")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM benutzer WHERE email=%s", (email,))
        if cursor.fetchone():
            print("❌ E-Mail bereits vergeben!")
        else:
            break
    
    passwort = input("🔒 Passwort: ")
    cursor.execute("INSERT INTO benutzer (name, email, passwort) VALUES (%s, %s, %s)", (name, email, passwort))
    conn.commit()
    print("✅ Registrierung erfolgreich!")
    return Benutzer(cursor.lastrowid, name, email)

def login(conn):
    print("\n🔑 --- Login ---")
    email = input("📧 E-Mail: ")
    passwort = input("🔒 Passwort: ")
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM benutzer WHERE email=%s AND passwort=%s", (email, passwort))
    result = cursor.fetchone()
    
    if result:
        print(f"✅ Willkommen, {result[1]}! 👋")
        return Benutzer(*result)
    else:
        print("❌ Login fehlgeschlagen.")
        return None

def neue_transaktion(conn, benutzer_id):
    print("\n💰 --- Neue Transaktion ---")
    
    # Betrag
    while True:
        try:
            betrag = float(input("💰 Betrag (€): "))
            break
        except ValueError:
            print("❌ Ungültiger Betrag!")

    # Datum im Format YYYY-MM-DD oder Enter für heute
    while True:
        datum_input = input("📅 Datum (YYYY-MM-DD, Enter für heute): ").strip()
        if datum_input == "":
            datum = datetime.date.today()
            break
        try:
            datum = datetime.datetime.strptime(datum_input, "%Y-%m-%d").date()
            break
        except ValueError:
            print("❌ Ungültiges Format! Bitte YYYY-MM-DD eingeben oder Enter für das heutige Datum.")
    
    # Kategorie
    kategorie = input("🏷️ Kategorie: ")
    
    # Typ
    while True:
        typ = input("📊 [E]innahme oder [A]usgabe: ").upper()
        if typ == "E":
            typ = "Einnahme"
            break
        elif typ == "A":
            typ = "Ausgabe"
            break
        print("❌ Bitte E oder A eingeben!")
    
    # Beschreibung
    beschreibung = input("📝 Beschreibung: ")
    
    # Speichern
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO transaktionen (benutzer_id, betrag, datum, kategorie, typ, beschreibung)
                      VALUES (%s, %s, %s, %s, %s, %s)""", 
                   (benutzer_id, betrag, datum, kategorie, typ, beschreibung))
    conn.commit()
    print("✅ Gespeichert!")


def zeige_transaktionen(conn, benutzer_id):
    while True:
        print("\n📊 --- Transaktionen ---")
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transaktionen WHERE benutzer_id = %s ORDER BY datum DESC", (benutzer_id,))
        rows = cursor.fetchall()
        
        if not rows:
            print("📭 Keine Transaktionen.")
            return
        
        transaktionen = [Transaktion(*row) for row in rows]
        
        # Übersicht
        einnahmen = sum(t.betrag for t in transaktionen if t.typ == "Einnahme")
        ausgaben = sum(t.betrag for t in transaktionen if t.typ == "Ausgabe")
        saldo = einnahmen - ausgaben
        print(f"💚 +{einnahmen:.2f}€ | 💸 -{ausgaben:.2f}€ | 💰 {saldo:.2f}€")
        print("-" * 40)
        
        # Liste
        for i, t in enumerate(transaktionen, 1):
            icon = "💚" if t.typ == "Einnahme" else "💸"
            print(f"{i}. {icon} {t.kategorie} | {t.betrag:.2f}€ | {t.datum}")
        
        # Auswahl
        wahl = input(f"\n[1-{len(transaktionen)}] Details | [0] Zurück: ")
        
        if wahl == "0":
            break
        elif wahl.isdigit() and 1 <= int(wahl) <= len(transaktionen):
            zeige_details(transaktionen[int(wahl)-1], conn)

def zeige_details(transaktion, conn):
    print(f"\n📋 --- Details ---")
    icon = "💚" if transaktion.typ == "Einnahme" else "💸"
    print(f"{icon} {transaktion.betrag:.2f}€")
    print(f"📅 {transaktion.datum}")
    print(f"🏷️ {transaktion.kategorie}")
    print(f"📝 {transaktion.beschreibung}")
    
    wahl = input("\n[L]öschen | [Enter] Zurück: ")
    if wahl.lower() == "l":
        if input("❓ Wirklich löschen? [j/n]: ").lower() == "j":
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transaktionen WHERE id = %s", (transaktion.id,))
            conn.commit()
            print("✅ Gelöscht!")

def hauptmenu(conn, benutzer):
    while True:
        print(f"\n🏠 --- {benutzer.name} ---")
        print("1. 💰 Neue Transaktion")
        print("2. 📊 Transaktionen")
        print("3. 🚪 Abmelden")
        
        wahl = input("Auswahl: ")
        if wahl == "1":
            neue_transaktion(conn, benutzer.id)
        elif wahl == "2":
            zeige_transaktionen(conn, benutzer.id)
        elif wahl == "3":
            print("👋 Tschüss!")
            break

def main():
    print("📊 Finanzplaner 📊")
    
    conn = get_connection()
    if not conn:
        print("❌ Keine Datenbankverbindung!")
        return
    
    while True:
        print("\n1. 📝 Registrieren")
        print("2. 🔑 Login")
        print("3. 🚪 Beenden")
        
        wahl = input("Auswahl: ")
        if wahl == "1":
            benutzer = registriere_benutzer(conn)
            if benutzer:
                hauptmenu(conn, benutzer)
        elif wahl == "2":
            benutzer = login(conn)
            if benutzer:
                hauptmenu(conn, benutzer)
        elif wahl == "3":
            print("👋 Bye!")
            break

if __name__ == "__main__":
    main()
