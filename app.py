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

def get_monthly_data(user_id):
    """Berechnet monatliche Einnahmen und Ausgaben für die letzten 6 Monate"""
    conn = get_connection()
    cursor = conn.cursor()
    
    today = datetime.date.today()
    months_data = []
    
    for i in range(5, -1, -1):
        if today.month - i <= 0:
            month = today.month - i + 12
            year = today.year - 1
        else:
            month = today.month - i
            year = today.year
        
        start_date = datetime.date(year, month, 1)
        if month == 12:
            end_date = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            end_date = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
        
        cursor.execute("""
            SELECT typ, SUM(betrag) FROM transaktionen 
            WHERE benutzer_id = %s AND datum >= %s AND datum <= %s 
            GROUP BY typ
        """, (user_id, start_date, end_date))
        
        results = cursor.fetchall()
        einnahmen = ausgaben = 0
        
        for typ, betrag in results:
            if typ == 'Einnahme':
                einnahmen = betrag
            elif typ == 'Ausgabe':
                ausgaben = betrag
        
        month_name = datetime.date(year, month, 1).strftime('%b')
        months_data.append({
            'month': month_name,
            'einnahmen': einnahmen,
            'ausgaben': ausgaben,
            'saldo': einnahmen - ausgaben
        })
    
    return months_data

def get_category_data(user_id):
    """Berechnet Ausgaben nach Kategorien"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT kategorie, SUM(betrag) FROM transaktionen 
        WHERE benutzer_id = %s AND typ = 'Ausgabe'
        GROUP BY kategorie ORDER BY SUM(betrag) DESC LIMIT 5
    """, (user_id,))
    
    return [{'name': k, 'amount': a, 'icon': get_kategorie_icon(k)} 
            for k, a in cursor.fetchall()]

def get_merchant_data(user_id):
    """Analysiert häufigste Merchants"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT beschreibung, COUNT(*) as freq, SUM(betrag) as total 
        FROM transaktionen 
        WHERE benutzer_id = %s AND typ = 'Ausgabe' AND beschreibung IS NOT NULL
        GROUP BY beschreibung ORDER BY freq DESC LIMIT 5
    """, (user_id,))
    
    return [{'name': b.split()[0] if b else "Unbekannt", 'frequency': f, 'total': t} 
            for b, f, t in cursor.fetchall()]

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
    cursor.execute("SELECT * FROM transaktionen WHERE benutzer_id = %s ORDER BY datum DESC", (session["user_id"],))
    rows = cursor.fetchall()
    transaktionen = [Transaktion(*row) for row in rows]

    grouped_transactions = defaultdict(list)
    for t in transaktionen:
        if isinstance(t.datum, str):
            datum_obj = datetime.datetime.strptime(t.datum, '%Y-%m-%d').date()
        else:
            datum_obj = t.datum

        month_key = datum_obj.strftime('%B %Y')
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

@app.route("/analytics")
def analytics():
    if "user_id" not in session:
        return redirect(url_for("login"))
   
    # Daten für Analytics sammeln
    monthly_data = get_monthly_data(session["user_id"])
    category_data = get_category_data(session["user_id"])
    merchant_data = get_merchant_data(session["user_id"])
   
    # Aktueller Monat Daten
    current_month = monthly_data[-1] if monthly_data else {'einnahmen': 0, 'ausgaben': 0, 'saldo': 0}
   
    return render_template("analytics.html",
                         monthly_data=monthly_data,
                         category_data=category_data,
                         merchant_data=merchant_data,
                         current_month=current_month)
 
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

@app.route("/transaktion/<int:id>/bearbeiten", methods=["GET", "POST"])
def bearbeite_transaktion(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        betrag = float(request.form["betrag"])
        datum = request.form["datum"]
        kategorie = request.form["kategorie"]
        typ = request.form["typ"]
        beschreibung = request.form["beschreibung"]

        cursor.execute("""
            UPDATE transaktionen
            SET betrag = %s, datum = %s, kategorie = %s, typ = %s, beschreibung = %s
            WHERE id = %s AND benutzer_id = %s
        """, (betrag, datum, kategorie, typ, beschreibung, id, session["user_id"]))
        conn.commit()

        flash("Transaktion aktualisiert!", "success")
        return redirect(url_for("transaktion_details", id=id))

    cursor.execute("SELECT * FROM transaktionen WHERE id = %s AND benutzer_id = %s", (id, session["user_id"]))
    row = cursor.fetchone()
    if not row:
        flash("Transaktion nicht gefunden!", "danger")
        return redirect(url_for("dashboard"))

    transaktion = Transaktion(*row)
    return render_template("edit_transaction.html", transaktion=transaktion)

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
