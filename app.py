from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from db import get_connection
from models import Benutzer, Transaktion
import datetime
from collections import defaultdict

app = Flask(__name__)
app.secret_key = "geheim"  # Für Sessions

# Kategorie-Icons Mapping
KATEGORIE_ICONS = {
    'groceries': '🥕',
    'restaurants': '☕',
    'cafés': '☕',
    'restaurants & cafés': '☕',
    'transport': '🚗',
    'entertainment': '🎬',
    'shopping': '🛍️',
    'health': '🏥',
    'utilities': '💡',
    'salary': '💰',
    'freelance': '💻',
    'other': '📋'
}

def get_kategorie_icon(kategorie):
    """Gibt das passende Icon für eine Kategorie zurück"""
    kategorie_lower = kategorie.lower()
    for key, icon in KATEGORIE_ICONS.items():
        if key in kategorie_lower:
            return icon
    return '📋'  # Default Icon

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        passwort = request.form["passwort"]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM benutzer WHERE email = %s", (email,))
        if cursor.fetchone():
            flash("E-Mail bereits registriert!", "danger")
            return redirect(url_for("register"))

        cursor.execute("INSERT INTO benutzer (name, email, passwort) VALUES (%s, %s, %s)", (name, email, passwort))
        conn.commit()
        flash("Registrierung erfolgreich!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        passwort = request.form["passwort"]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM benutzer WHERE email=%s AND passwort=%s", (email, passwort))
        result = cursor.fetchone()

        if result:
            session["user_id"] = result[0]
            session["user_name"] = result[1]
            return redirect(url_for("dashboard"))
        else:
            flash("Login fehlgeschlagen!", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()
    # Sortiere nach Datum ASC (älteste zuerst)
    cursor.execute("SELECT * FROM transaktionen WHERE benutzer_id = %s ORDER BY datum ASC", (session["user_id"],))
    rows = cursor.fetchall()
    transaktionen = [Transaktion(*row) for row in rows]

    # Gruppiere Transaktionen nach Jahr-Monat
    grouped_transactions = defaultdict(list)
    for t in transaktionen:
        # Konvertiere Datum zu datetime falls es ein String ist
        if isinstance(t.datum, str):
            datum_obj = datetime.datetime.strptime(t.datum, '%Y-%m-%d').date()
        else:
            datum_obj = t.datum
        
        month_key = datum_obj.strftime('%B %Y')  # z.B. "June 2025"
        # Füge Icon zur Transaktion hinzu
        t.icon = get_kategorie_icon(t.kategorie)
        grouped_transactions[month_key].append(t)

    einnahmen = sum(t.betrag for t in transaktionen if t.typ == "Einnahme")
    ausgaben = sum(t.betrag for t in transaktionen if t.typ == "Ausgabe")
    saldo = einnahmen - ausgaben

    return render_template("dashboard.html", 
                         grouped_transactions=dict(grouped_transactions),
                         einnahmen=einnahmen, 
                         ausgaben=ausgaben, 
                         saldo=saldo)

@app.route("/transaktion/neu", methods=["GET", "POST"])
def neue_transaktion():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        betrag = float(request.form["betrag"])
        datum = request.form["datum"] or datetime.date.today().isoformat()
        kategorie = request.form["kategorie"]
        typ = request.form["typ"]
        beschreibung = request.form["beschreibung"]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transaktionen (benutzer_id, betrag, datum, kategorie, typ, beschreibung)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (session["user_id"], betrag, datum, kategorie, typ, beschreibung))
        conn.commit()

        return redirect(url_for("dashboard"))

    return render_template("new_transaction.html")

@app.route("/transaktion/<int:id>")
def transaktion_details(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transaktionen WHERE id = %s AND benutzer_id = %s", (id, session["user_id"]))
    row = cursor.fetchone()
    
    if not row:
        flash("Transaktion nicht gefunden!", "danger")
        return redirect(url_for("dashboard"))
    
    transaktion = Transaktion(*row)
    transaktion.icon = get_kategorie_icon(transaktion.kategorie)
    
    return render_template("transaction_details.html", transaktion=transaktion)

@app.route("/transaktion/<int:id>/loeschen")
def loesche_transaktion(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transaktionen WHERE id = %s AND benutzer_id = %s", (id, session["user_id"]))
    conn.commit()

    flash("Transaktion gelöscht.", "info")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True)