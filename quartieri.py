#!/usr/bin/env python3
"""Assegna gli atti ai quartieri di Rivoli leggendo solo l'oggetto dell'atto.

Uso: python3 quartieri.py atti.csv regole_quartieri.csv territorio.csv

Un atto finisce in territorio.csv se cita almeno una via, piazza o zona.
- quartiere/riferimento sono compilati solo se una regola documentata lo permette
  (nome del quartiere nell'oggetto, oppure via/luogo collegato dal Comune o da un atto);
- vie elenca le vie e piazze citate, anche quando non attribuibili a un quartiere.
"""
import csv, re, sys

TIPI = r"VIA|VIALE|CORSO|C\.SO|PIAZZA|P\.ZZA|PIAZZALE|LARGO|STRADA|VICOLO"
PART = r"(?:DEI |DEGLI |DELLE |DELLA |DEL |DI |DA |DE |D'|AL |ALLE |ALLA |ALL')?"
STRADA = re.compile(r"\b(" + TIPI + r")\s+(" + PART + r"[A-ZÀ-Ü\.'][A-ZÀ-Ü\.']{2,}(?: [A-ZÀ-Ü\.'][A-ZÀ-Ü\.']{2,})?)")
CODA = re.compile(r"\s+(N|N\.|NN|NN\.|CIVICO|N°|NUMERO|DAL|DALLA|AL|ALLA|ANGOLO|IN|E|PER|DI|DA|CON|SU|DEL|DELLA|PRESSO|O|A|SI|CHE|NEL|NELLA|TRA|FRA|COMPRESA|COMPRESE|INCROCIO)$")
# espressioni che sembrano vie ma non lo sono
ESCLUSE = re.compile(r"^(CORSO (DI LAUREA|D'OPERA|DI STUDI|DI FORMAZIONE|DEI LAVORI|DELLA|DEL|DI)|VIA (D'URGENZA|TELEMATICA|DI FATTO|AMMINISTRATIVA|DI SOMMA|DIPLOMATICA|GIUDIZIALE|BONARIA|PRINCIPALE|ORDINARIA|URGENTE|INFORMATICA|RICONOSCIMENTO)|STRADA (COMPRESE|COMPRESA|DELL'IMPIANTO|STRADA)|VIA QUERRO)", re.I)
ALIAS = {
    "C.SO": "CORSO", "P.ZZA": "PIAZZA",
    "VIA LUIGI GATTI": "VIA GATTI", "VIA SALVADOR ALLENDE": "VIA ALLENDE",
    "PIAZZA REPUBBLICA": "PIAZZA DELLA REPUBBLICA", "PIAZZA MARTIRI": "PIAZZA MARTIRI DELLA LIBERTÀ", "VIA S.G. BOSCO": "VIA S.G. BOSCO",
}
MINUSC = {"DEI", "DEGLI", "DELLE", "DELLA", "DEL", "DI", "DA", "DE", "AL", "ALLE", "ALLA"}

def bella(s):
    out = []
    for i, w in enumerate(s.split()):
        if i and w in MINUSC:
            out.append(w.lower())
        elif w.startswith("D'") or w.startswith("ALL'"):
            a, b = w.split("'", 1)
            out.append(a.lower() + "'" + b.capitalize())
        elif re.fullmatch(r"(?:[A-Z]\.)+[A-Z]?", w):
            out.append(w)
        else:
            out.append(w.capitalize())
    return " ".join(out)

def vie_citate(oggetto):
    trovate = []
    for m in STRADA.finditer(oggetto.upper()):
        tipo = {"C.SO": "CORSO", "P.ZZA": "PIAZZA"}.get(m.group(1), m.group(1))
        nome = m.group(2).strip().rstrip(".")
        while True:
            n2 = CODA.sub("", nome)
            if n2 == nome:
                break
            nome = n2
        v = (tipo + " " + nome).strip()
        if ESCLUSE.match(v):
            continue
        v = ALIAS.get(v, v)
        if len(nome) < 3:
            continue
        b = bella(v)
        if b not in trovate:
            trovate.append(b)
    return trovate

NATURA = [
    ("Mozioni e ordini del giorno", re.compile(r"^\s*(MOZIONE|ORDINE DEL GIORNO|INTERROGAZIONE|INTERPELLANZA)", re.I)),
    ("Patrocini ed eventi", re.compile(r"PATROCINIO|BENEFICI DIVERSI|FESTA|MANIFESTAZIONE|MOSTRA[- ]MERCATO|RASSEGNA|CONCERTO|FIERA|KAPPA FUTURFESTIVAL|NOTTE AL CASTELLO|CACCIA ALLE UOVA|MERCATINO|CONVEGNO|PROIEZIONE|INIZIATIVA", re.I)),
    ("Pratiche amministrative", re.compile(r"ACCERTAMENT|RISCOSSIONE|INGIUNZIONE|RIMBORS|IMPOSTA DI (REGISTRO|BOLLO)|SPESE CONDOMINIALI|CONDOMINIO|RETTIFICA|INTEGRAZIONE DETERMINA|REVOCA|TRASFORMAZIONE IN PROPRIET|DIRITTO DI SUPERFICIE|ANNULLAMENTO|VINCOLO|OMESSO PAGAMENTO|RATEIZZ|SINISTRO|INDENNIT|BOLLETT|UTENZE|COMODATO|QUOTA DI ADESIONE|ACQUISTO COPIE|ACQUISTO DI N", re.I)),
]
TIPOLOGIE_PRATICHE = {"Rateizzazioni, rimborsi e restituzioni ai cittadini", "Variazioni e regolarizzazioni contabili", "Accertamenti di entrata (soldi in arrivo)", "Correzioni e revoche di atti precedenti"}

def natura(x):
    """Separa gli atti che decidono interventi, servizi o spese da patrocini, mozioni e pratiche."""
    o = x.get("oggetto") or ""
    if (x.get("tema") or "").startswith("Mozioni"):
        return "Mozioni e ordini del giorno"
    for nome, rx in NATURA:
        if rx.search(o):
            return nome
    if (x.get("tipologia_determina") or "") in TIPOLOGIE_PRATICHE:
        return "Pratiche amministrative"
    return "Interventi, servizi e spese"

def carica_regole(path):
    regole = []
    for r in csv.DictReader(open(path, encoding="utf-8-sig")):
        regole.append({**r, "rx": re.compile(r["regex"], re.I)})
    return regole

def attribuisci(oggetto, regole):
    """Restituisce (quartiere, riferimento, luogo) oppure ('', '', '')."""
    trovate = [r for r in regole if r["rx"].search(oggetto)]
    # un luogo collegato vale solo se l'oggetto non contiene già un nome di quartiere diverso
    nomi = [r for r in trovate if r["tipo"].startswith("Nome")]
    scelte = nomi or trovate
    if not scelte:
        return "", "", ""
    # «Cascine Vica» generico cede il passo a qualunque indicazione più precisa
    precise = [r for r in scelte if not r["quartiere"].startswith("Cascine Vica")]
    if precise:
        scelte = precise
    r = scelte[0]
    return r["quartiere"], r["tipo"], r["luogo"]

def main(atti, regole_csv, uscita):
    regole = carica_regole(regole_csv)
    righe = list(csv.DictReader(open(atti, encoding="utf-8-sig")))
    campi = ["tipo", "numero", "anno", "pubblicazione", "mese", "settore", "tema", "tipologia_determina",
             "importo_citato_eur", "oggetto", "link", "quartiere", "riferimento", "luogo", "vie", "natura"]
    n_att = n_vie = 0
    with open(uscita, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=campi)
        w.writeheader()
        for x in righe:
            o = x.get("oggetto") or ""
            q, rif, luogo = attribuisci(o, regole)
            vie = vie_citate(o)
            if not (q or vie):
                continue
            n_vie += 1
            n_att += 1 if q else 0
            w.writerow({**{k: x.get(k, "") for k in campi[:11]}, "quartiere": q, "riferimento": rif, "luogo": luogo, "vie": " | ".join(vie), "natura": natura(x)})
    print(f"atti letti {len(righe)}; con via/zona {n_vie}; attribuiti a un quartiere {n_att}")

if __name__ == "__main__":
    main(*sys.argv[1:4])
