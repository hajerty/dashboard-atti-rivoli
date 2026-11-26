# A che punto siamo · Comune di Rivoli

Dashboard sul mandato 2024–2029 del Comune di Rivoli letto negli atti pubblici: determine, delibere di Giunta e di Consiglio, ordinanze di viabilità, avvisi del sito del Comune e voti del Consiglio, dal 1° luglio 2024 al 10 novembre 2026.

**Sito:** https://hajerty.github.io/dashboard-atti-rivoli/

## Sezioni

**Il mandato**
- **Il mandato in sei storie**: la pagina iniziale. Programma, tempi dalla delibera al cantiere, teleriscaldamento, vie con più cantieri, mozioni e temi in crescita.
- **Programma «Rivoli, è ora»**: i 40 impegni ricavati dal programma di mandato, divisi nelle 12 aree «Rivoli, è ora di…». Ogni impegno ha uno stato indicativo con il motivo e gli atti collegati. La vista «Presentazione» riassume ogni area in una diapositiva: fatto, in corso, da fare.
- **Consiglio comunale**: mozioni e ordini del giorno approvati e respinti, con gli eventuali atti successivi.
- **La città nei giornali** (dal luglio 2024, con filtro per periodo): confronto tra i temi degli atti e quelli degli articoli di stampa, tono per tema, storie del periodo con il primo intervento del Comune e gli atti collegati, testate e elenco degli articoli.

**In città**
- **Interventi e tempi**: dalla delibera all'affidamento e alla fine lavori, in sotto-schede:
  - In sintesi
  - Intervento per intervento
  - Per ufficio
  - Quanto siamo rapidi: confronto con i lavori simili e con i termini del Codice dei contratti
  - Per tema
  - Nel tempo
  - Dalle mozioni agli atti
- **Reti e cantieri**: mappa dei cantieri di gas, acqua, luce, teleriscaldamento e fibra, più asfalti e strade del Comune. Si filtra per anno, rete e stato del cantiere, e c'è il confronto tra strade asfaltate e scavi successivi.
- **In arrivo in città**: decisioni già prese che si vedranno nei prossimi mesi.
- **Calendario eventi**: i principali eventi mese per mese.

**Gli atti**
- **Attività degli uffici**
- **Approfondisci un tema**
- **Cerca tra gli atti**

## Dati (`data/`)

| File | Contenuto |
|---|---|
| `atti.csv` | tutti gli atti (tipo, numero, anno, data, ufficio, tema, oggetto, link) |
| `programma.csv` | impegni del programma «Rivoli, è ora» con area, parole chiave, stato, fatti e cosa manca |
| `prossimamente.csv` | decisioni in arrivo con certezza, fase e prossimo passo |
| `catene.csv`, `catene_atti.csv` | interventi deliberati e atti collegati (CUP o rimandi espliciti), con area del programma |
| `procedure.csv`, `affidamenti.csv` | procedure e affidamenti ricavati dalle determine |
| `tempi_gare.csv` | coppie avvio → aggiudicazione delle gare e confronto con i termini |
| `mozioni.csv`, `mozioni_seguiti.csv` | mozioni e odg con esito del voto e seguito |
| `lavori.csv`, `lavori_in_arrivo.csv` | atti del Comune sulle reti, geolocalizzati |
| `avvisi_lavori.csv` | avvisi di viabilità del sito del Comune, una riga per via |
| `ordinanze_viabilita.csv` | ordinanze di viabilità dell'Albo, una riga per via, con categoria e committente |
| `calendario.csv` | eventi in città da ordinanze e delibere di Giunta |
| `stampa.csv` | articoli su Rivoli (titolo, testata, data) da Google News e notizie del sito del Comune, con tema, tono, chi parla e storia assegnati dal titolo |
| `mappa_osm.csv`, `mappa_confine.csv` | base cartografica da OpenStreetMap (© contributori di OpenStreetMap) |

**Fonti:** Google News (titoli degli articoli: il testo resta sui siti delle testate); Albo pretorio online del Comune di Rivoli (pagine pubbliche); sito istituzionale del Comune (avvisi e notizie); rivoli.consiglicloud.it (voti del Consiglio, pagine pubbliche); stradario ANNCSU; OpenStreetMap.

Temi, stati degli impegni, collegamenti tra atti e categorie sono ricavati dal testo degli oggetti degli atti. Sono una lettura indicativa: non sono un giudizio politico né una verifica sul posto.

## Come si aggiorna

1. Aggiornare i file in `data/` e la data in `data/aggiornato_al.txt` (forma «12 novembre 2026»): `build.py` la scrive anche in testata come «Ultimo aggiornamento». Se cambiano i testi o il codice della pagina, aggiornare `src/pagina.html`.
2. Eseguire `python3 build.py`, che genera `index.html` con i dati incorporati. La pagina funziona anche offline.
3. Fare commit e push: GitHub Pages pubblica `index.html`.
4. Stampa: i titoli raccolti da Google News vanno in `dati_grezzi/` (una riga «MMGG|testata|titolo»); `python3 strumenti/classifica_stampa.py ANNO dati_grezzi/<file>.txt data/stampa.csv > nuovo.csv` li classifica e li unisce a quelli già presenti.
5. Versione di prova (artifact, limite 262.144 byte per documento): `npm install` e poi `node strumenti/minifica.mjs src/pagina.html <cartella>` produce `<cartella>/index.html` e `<cartella>/rv-app.js`, da caricare nei documenti `files/index.html` e `files/rv-app.js`. `src/pagina.html` resta la fonte leggibile.
6. Date dei cantieri: per ogni nuova ordinanza di viabilità ancora in pubblicazione leggere nel testo le date di inizio e fine (`inizio`, `fine` in `ordinanze_viabilita.csv`); per gli avvisi del sito leggere le date anche nella descrizione, non solo nel titolo e nel sottotitolo (l'avviso Edison sul teleriscaldamento indica «dal 16 dicembre 2024 al 31 dicembre 2026» solo nel testo); per quelli che rimandano alle ordinanze («consulta le ordinanze») cercare le date nelle ordinanze allegate. Per l'avviso Edison sul teleriscaldamento le date di ogni tappa sono in `dati_grezzi/tlr_edison_ordinanze_AAAA-MM-GG.csv`, lette dai PDF allegati all'avviso e riportate in `inizio`/`fine` di `ordinanze_viabilita.csv`: va ripetuto a ogni aggiornamento, perché il Comune aggiunge le nuove tappe all'avviso. Quando la data di fine manca, la pagina stima lo stato dalla pubblicazione (in corso per 30 giorni, 7 per guasti e urgenze: `window.RVstima` in `src/pagina.html`), quindi un cantiere senza date non sparisce, ma la data letta è sempre migliore della stima.
