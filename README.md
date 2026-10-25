# Cinema a Roma e a Bologna: aggiornamento automatico

Questo pacchetto aggiorna ogni notte gli orari delle quattro pagine (Roma telefono, Roma iPhone,
Roma computer, Bologna) e le pubblica su un sito tuo gratuito (GitHub Pages).

## Cosa contiene
- `docs/`: le pagine pronte (`roma.html`, `roma-iphone.html`, `roma-desktop.html`, `bologna.html`) e un indice.
- `update.py`: legge gli orari da MyMovies e riscrive i dati nelle pagine.
- `.github/workflows/aggiorna.yml`: lo fa partire da solo ogni notte (e anche a mano).

## Come metterlo online (una volta sola, circa 10 minuti)
1. Crea un account gratuito su https://github.com e poi un nuovo repository **pubblico** (per esempio `orari-cinema`).
   Con un repository privato le pagine gratuite non funzionano.
2. Carica dentro tutto il contenuto di questa cartella (anche la cartella nascosta `.github`).
   Dal sito: «Add file» > «Upload files», trascina tutto.
3. Vai in **Settings > Pages**, scegli *Deploy from a branch*, ramo `main`, cartella `/docs`, poi Save.
4. Vai in **Settings > Actions > General** e in «Workflow permissions» scegli *Read and write permissions*. Save.
5. Vai nella scheda **Actions**, scegli «Aggiorna orari cinema» e premi **Run workflow**.
6. Quando il pallino diventa verde, le pagine sono qui:
   `https://TUO-NOME.github.io/orari-cinema/` (con l'indice dei quattro link).

Da quel momento si aggiorna da solo ogni notte, verso le 4:30-5:30 ora italiana.

## Cosa si aggiorna da solo e cosa no
- **Da solo:** orari, film in sala, data scritta in alto, link agli orari.
- **Non da solo:** trame, cast, premi, stelle della critica, incassi, prezzi e indirizzi. Restano quelli di oggi.
  I film nuovi compaiono con «Trama non disponibile». Per completarli basta chiedermelo.
- Un film che non c'è più nel listino resta nell'elenco con la scritta «orari sul sito».

## Se qualcosa non va
- Se MyMovies cambia il suo sito, o legge troppo pochi film, il programma si ferma con un errore
  (pallino rosso in Actions) e **non tocca le pagine**: restano come erano. In quel caso mandami il
  messaggio dell'errore e lo sistemo.
- Ho provato la parte che scrive le pagine e quella che riconosce i nomi dei cinema, ma **non ho potuto provare la
  lettura dal vero del sito** da dove lavoro. Il primo avvio (passo 5) serve proprio a verificarla:
  controlla nel registro (clicca sull'esecuzione) che compaia «Roma: N film letti dal sito».

## Attenzione
Leggere un sito in modo automatico può essere regolato dalle sue condizioni d'uso. Il programma fa una richiesta
al secondo, una volta al giorno, per uso personale. Controlla le condizioni di MyMovies se pensi di
diffondere le pagine. Gli incassi e le trame restano di proprietà delle rispettive fonti.
