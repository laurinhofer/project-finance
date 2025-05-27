class Benutzer:
    def __init__(self, id, name, email, passwort=None):
        self.id = id
        self.name = name
        self.email = email
        self.passwort = passwort  # optional für Login-Zwecke

    def __str__(self):
        return f"{self.name} ({self.email})"

class Transaktion:
    def __init__(self, id, benutzer_id, betrag, datum, kategorie, typ, beschreibung=""):
        self.id = id
        self.benutzer_id = benutzer_id
        self.betrag = betrag
        self.datum = datum
        self.kategorie = kategorie
        self.typ = typ  # "Einnahme" oder "Ausgabe"
        self.beschreibung = beschreibung

    def __str__(self):
        return f"[{self.typ}] {self.kategorie}: {self.betrag}€ am {self.datum}"

class Budget:
    def __init__(self, id, benutzer_id, kategorie, betrag, monat, jahr):
        self.id = id
        self.benutzer_id = benutzer_id
        self.kategorie = kategorie
        self.betrag = betrag
        self.monat = monat
        self.jahr = jahr

    def __str__(self):
        return f"{self.kategorie}: {self.betrag}€ ({self.monat}/{self.jahr})"
