"""Classifica i titoli raccolti da Google News e dal sito del Comune.

Uso: python3 strumenti/classifica_stampa.py ANNO grezzi.txt [precedente.csv] > data/stampa.csv
- grezzi.txt: una riga per articolo, «MMGG|testata|titolo». La testata è un codice (CR = sito del Comune,
  AG, TC, TO, TT, LN, LS, RE, CT, QV, GV, IT, QP, RN, LV, AN, 24, CQ, PT: vedi TESTATE) o il nome per esteso.
  Una notizia del Comune che ripubblica un articolo finisce con « ⟨Testata⟩».
- precedente.csv: righe già classificate da tenere (senza duplicati di data+titolo).
Regole fisse e indicative: tema, tono, chi parla, storia e formato sono ricavati solo dal titolo."""
import re, csv, collections, sys
ANNO = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 2026
GREZZI = sys.argv[2] if len(sys.argv) > 2 else "raw.txt"
PREC = sys.argv[3] if len(sys.argv) > 3 else None
TESTATE = {"CR": "Città di Rivoli (sito del Comune)", "AG": "L'Agenda News", "TC": "Torino Cronaca", "TO": "Torino Oggi", "TT": "TorinoToday",
           "LN": "Luna Nuova", "LS": "La Stampa", "RE": "la Repubblica Torino", "CT": "Corriere Torino", "QV": "QV Quotidiano Venariese",
           "GV": "Giornale La Voce", "IT": "Il Torinese", "QP": "Quotidiano Piemontese", "RN": "RaiNews (TGR Piemonte)", "LV": "La Valsusa",
           "AN": "ANSA", "24": "24ovest.it", "CQ": "CronacaQui", "PT": "Prima Torino"}
NAZ = {"La Stampa", "la Repubblica Torino", "Corriere Torino", "RaiNews (TGR Piemonte)", "ANSA"}
STORIE = [
    ("Metro 1 e corso Francia", r"metro|metropolitan|corso francia|c\.so francia|cascine vica, servono|infra\.to|cantieri infiniti"),
    ("Case ATC di via Pasubio", r"pasubio|case atc|disagi case atc|case popolari di rivoli|alloggi atc"),
    ("Occupazioni nei licei", r"occupat|occupazione|romero|darwin e romero|scuola di rivoli, petardi"),
    ("Accensione del riscaldamento", r"riscaldamento|termosifoni"),
    ("Regole sulla pubblicità", r"pubblicit"),
    ("Ex scuola Primo Levi: studentato e Croce Verde", r"primo levi|studentato|cascine vica rinasce"),
    ("Gemello digitale e barriere", r"gemello digitale|copia digitale|senza barriere"),
    ("Piano regolatore", r"piano regolatore|consumo di suolo"),
    ("Ex Dana: produzione trasferita a Rivoli", r"ex dana|allison"),
    ("Cascina Scola e beni confiscati", r"cascina scola|bene confiscato|immobile confiscato|confiscato alla mafia"),
    ("Bonus trasporti GTT", r"bonus gtt|biglietti gtt|agevolazioni per la mobilit|sostegno mobilit|bonus per studenti|accessibili a rivoli, scattano"),
    ("Cittadinanza onoraria a Wes Studi", r"wes studi|mohicani|premio oscar studi"),
    ("Nuovo Centro per l'impiego", r"centro per l.impiego"),
]
REGOLE = [  # (tema, regex) in ordine di priorità: prima l'argomento, la voce politica è un campo a parte
    ("Castello (museo, non Comune)", r"castello di rivoli|rudi fuchs|marisa merz|c2c|art week|inserzioni, tre artiste|giornata del contemporaneo"),
    ("Cronaca", r"incident|investit|investe |arrest|droga|vipera|scompars|ritrovat|allontanato|aggression|assalt|rubat|pirata|tamponament|scontro|multat|pass disabili|pass del marito|ribalt|allarmi bomba|minacce|scritta|lutto|furti|raid notturno|gasolio|olio di frittura|podisti|emmy|regist[ai] del thriller|kilimangiaro|scrittrice"),
    ("Ospedale e ASL (non Comune)", r"ospedale|\basl\b|psichiatria|neurolog|neuroscienze|evviva|abio|lilt|ictus|cuore 2026"),
    ("Opere, urbanistica e patrimonio", r"piano regolatore|rigenerazione|consumo di suolo|studentato|primo levi|cascina scola|gemello digitale|copia digitale|senza barriere|cascine vica rinasce|maxi piano|maxi-progetto|confiscat|complesso sportivo|pubblicit|stazione radio|comitato quartiere|piazza mafalda|lavori pubblici|biodiversit|don milani|palestra"),
    ("Viabilità e mobilità", r"metro|corso francia|c\.so francia|gtt|\bbus\b|mebus|viabilit|circolazione|tangenziale|sp 7|mobilit[aà] (sostenibile|alternativa)|settimana europea della mobilit|agevolazioni per la mobilit|sostegno mobilit|trasporti|traffico|cantieri|monopattini|rallentare le auto|teleriscald|strade pericolose"),
    ("Ambiente e verde", r"albero|alberi|rifiuti|raee|odori|zanzar|larvicid|cassonetti|puliamo|riscaldament|termosifon"),
    ("Cultura, eventi e sport", r"pallacanestro|basket|strarivoli|festa dello sport|tennis|sportiv|fiera|mercatin|sagra|presenta \"|la promessa|\bmostra\b|teatro|heart of gaza"),
    ("Servizi comunali", r"censimento a rivoli|censimento permanente"),
    ("Scuola e giovani", r"scuol|liceo|darwin|romero|natta|student|giovan|ragazz|orienta|bussole|primo voto|servizio civile|0-6|ascoltami|nido|refezione|centri estivi|promemoria|berlino|intercultura|matteotti|neo-elettori"),
    ("Sociale e casa", r"\batc\b|pasubio|alloggi|case popolari|edilizia sociale|anzian|over 6|ultra 65|famigli|disabil|fibromialgia|congedo|colletta|villa mater|nascita|svezzamento|genitori|carta .dedicata|spazi ancore|alzheimer|donne|ottobre rosa|inclusione|dedicata a te|comunit[aà] educante|croce verde"),
    ("Lavoro e commercio", r"lavoro|impiego|commerci|imprese|ex dana|corso gratuito|corso di aggiornamento|\bcna\b|confesercenti|p\.p\.u|gdo|grande distribuzione|maxistore|job day|muletto|artigian|conad|tecnologia dimenticata|caat|peperone"),
    ("Sicurezza e legalità", r"carabinier|polizia locale|legalit|mafia|riina|capo dei capi|divisa|taurinense|forze armate|alpini|telecamera|varco"),
    ("Servizi comunali", r"uffici comunali|servizi comunali|censimento|fuori sede|tributo|p\.i\.a\.o|esumazioni|votiva|cimitero|mobilit[aà] esterna|soluzioni gestionali|dialogare con l.amministrazione|rivoli in comune|turismovest|ravensburg|gemellaggio|generazione|contributi economici alle associazioni|zoom per il territorio"),
    ("Consiglio comunale", r"consiglio comunale|\bmozion|convocazione|commissione|capigruppo|consulta di rivoli|trasparenza sugli atti|vita di coppia"),
    ("Cultura, eventi e sport", r"."),
]
VOCI = [("Forze politiche e Consiglio", r"\blega\b|forza italia|fratelli d|\(pd\)|\bpd\b|\bavs\b|campo largo|consiglio comunale|\bmozion|ordine del giorno|adduce|conticelli|grimaldi"),
        ("Sindaco e Comune", r"sindac|errigo|il comune|chiarimenti del comune|proposta del comune"),
        ("Cittadini, comitati e lavoratori", r"residenti|cittadini|commercianti|protesta|presidio dei|marcia|corteo|mobilitazione|sciopero|in 5mila|in 3mila|oltre 3")]
NEG = r"presidio(?! di legalit)|protest|disagi|crollat|pericolant|degrado|attacca|accusa|denunc|a rischio|penalizza|chiuderemo|cattivi odori|restano fermi|attesa|smantellat|mobilitazione|urgent|aspettare|nulla|senza i fondi|occupat|vandalism|scaricabarile|strumentalizz|non ci sta|dice basta|basta cantieri|in pericolo|doccia gelata|pericolose|sciopero|diserta|salta il corteo|sbloccare|ripresa dei cantieri|completare|chiede il conto|chi ha sbagliato|risponda|petardi|servono 70|rallentare le auto|trappola"
POS = r"inaugur|rinasce|rinascita|successo|arriva|raddoppia|al via|si rinnova|benvenuto|riqualific|nuov[aoe]|premio|grazie a|amplia|tornano|bonus|contribut|unanimit|si accende|protagonista|rafforzata|nasce|valorizz|celebra|accoglie|ricostruiamo|offre un terreno|smentisce|al fianco|presidio di legalit|ridisegna|futuro|eccellenza|più accessibili|trasporti gratis"
NEUTRO_FORZATO = r"nessun divieto|chiarimenti|mozione arriva|approda in consiglio|la mozione propost|mozione per l"
righe = []
for l in open(GREZZI, encoding="utf-8"):
    l = l.rstrip("\n")
    if not l: continue
    d, s, t = l.split("|", 2)
    m = re.search(r" ⟨([^⟩]+)⟩$", t); ril = m.group(1) if m else ""
    t = re.sub(r" ⟨[^⟩]+⟩$", "", t).strip()
    test = TESTATE.get(s, s)
    fonte = "Comune" if s == "CR" else "Stampa"
    if fonte == "Comune" and ril: fonte = "Comune (rilancia la stampa)"
    tl = t.lower()
    tema = next(n for n, r in REGOLE if re.search(r, tl))
    storia = next((n for n, r in STORIE if re.search(r, tl)), "")
    voce = next((n for n, r in VOCI if re.search(r, tl)), "Redazione") if fonte == "Stampa" else ""
    if fonte == "Stampa" and tema not in ("Cronaca", "Castello (museo, non Comune)", "Ospedale e ASL (non Comune)"):
        tono = "neutro" if re.search(NEUTRO_FORZATO, tl) else "critico" if re.search(NEG, tl) else "positivo" if re.search(POS, tl) else "neutro"
    else: tono = ""
    righe.append({"data": f"{ANNO}-{d[:2]}-{d[2:]}", "testata": test, "tipo_testata": "Comune" if s == "CR" else ("Nazionale, pagine Torino" if test in NAZ else "Locale"),
                  "fonte": fonte, "tema": tema, "tono": tono, "voce": voce, "storia": storia, "rilancia_da": ril, "formato": "Agenda di eventi" if re.search(r"cosa fa(re|i)|tutti gli (appuntamenti|eventi)|eventi (imperdibili|da non perdere)|gli appuntamenti a rivoli|weekend a rivoli|il weekend a rivoli|week-end|fine settimana", tl) else "Articolo", "titolo": t})
if PREC:
    viste = {(r["data"], r["titolo"]) for r in righe}
    righe += [r for r in csv.DictReader(open(PREC, encoding="utf-8-sig")) if (r["data"], r["titolo"]) not in viste]
righe.sort(key=lambda r: (r["data"], r["testata"]))
w = csv.DictWriter(sys.stdout, fieldnames=list(righe[0])); w.writeheader(); w.writerows(righe)
print(len(righe), "righe", collections.Counter(r["fonte"] for r in righe), file=sys.stderr)
