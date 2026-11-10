# Dashboard Atti Rivoli

Dashboard sugli atti pubblicati dal Comune di Rivoli: determine dei dirigenti, delibere di Giunta e delibere di Consiglio, dal 1° luglio 2024 al 10 novembre 2026.

**Sito:** https://hajerty.github.io/dashboard-atti-rivoli/

## Cosa mostra

- **Panoramica**: quanti atti escono ogni mese, di cosa si occupano, quali uffici li producono.
- **Approfondisci un tema**: andamento, uffici e atti più recenti per ogni tema.
- **Per quartiere**: gli atti che citano una via, una piazza o un quartiere, assegnati ai quartieri solo quando una regola documentata lo permette; vie senza quartiere e regole usate.
- **Programma di mandato**: i 35 impegni delle linee programmatiche 2024-2029 con uno stato indicativo (realizzato, in corso, avviato, non risulta), il motivo e gli atti collegati.
- **Prossimamente**: le decisioni già prese che si vedranno in città nei prossimi mesi.
- **Cerca un atto**: ricerca per parola, con il link alla scheda dell'atto sull'Albo.

## Dati

Fonte: Albo pretorio online del Comune di Rivoli (registri Delibere di Giunta, Delibere di Consiglio, Determine), pagine pubbliche.

Temi, tipi di determina e importi sono ricavati dal solo testo dell'oggetto degli atti. Gli stati degli impegni e le voci di "Prossimamente" sono una lettura indicativa fatta a mano sugli oggetti degli atti: non sono un giudizio politico né una verifica sul posto.

| File | Contenuto |
|---|---|
| `data/atti.csv` | tutti gli atti (tipo, numero, anno, data, ufficio, tema, oggetto, link) |
| `data/programma.csv` | impegni del programma con parole chiave, stato, fatti e cosa ancora non risulta |
| `data/prossimamente.csv` | decisioni in arrivo con certezza, fase e prossimo passo |
| `data/regole_quartieri.csv` | regole per assegnare gli atti ai quartieri, con la fonte di ognuna |
| `data/territorio.csv` | atti che citano una via o un quartiere, con il quartiere assegnato (generato da `quartieri.py`) |

## Come si aggiorna

1. Aggiornare `atti.csv`, `programma.csv` e `prossimamente.csv` in `data/` e la data in `data/aggiornato_al.txt`; se cambiano i testi della pagina, aggiornare `src/pagina.html`.
2. Eseguire `python3 build.py`: rigenera `data/territorio.csv` da `atti.csv` e `regole_quartieri.csv` (con `quartieri.py`) e poi `index.html` con i dati incorporati, funziona anche offline.
3. Fare commit e push: GitHub Pages pubblica `index.html`.

`src/pagina.html` è la pagina, `src/d3.min.js` la libreria dei grafici (d3 v7).

Le regole per i quartieri sono in `data/regole_quartieri.csv`: il Comune non pubblica i confini dei quartieri, quindi si aggiungono solo vie o luoghi collegati a un quartiere da una fonte documentata (sito del Comune o atto). Se si ottiene l'elenco ufficiale delle vie per quartiere, basta aggiungere una riga per via.

L'aggiornamento è pensato ogni due mesi.
