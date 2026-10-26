#!/usr/bin/env python3
"""Aggiorna gli orari dei cinema (Roma e Bologna) nelle pagine in docs/.

Per Roma legge Nottola Sera (fonte principale) e usa MyMovies solo per i film che
Nottola non riporta; per Bologna legge MyMovies. Poi riscrive il blocco dati di ogni pagina
(tra /*DATA_START*/ e /*DATA_END*/) e aggiorna la data scritta nella pagina.
Se qualcosa va storto (sito cambiato, pochi dati) il programma si ferma
con un errore e NON tocca le pagine: restano quelle di prima.

Uso:  python update.py            (aggiorna davvero)
      python update.py --offline dati.json   (prova senza internet)
"""
import re, sys, json, time, difflib, datetime, pathlib, unicodedata
from zoneinfo import ZoneInfo

DOCS = pathlib.Path(__file__).parent / "docs"
CITIES = {"roma": "Roma", "bologna": "Bologna"}   # prefisso del file -> città
MIN_FILMS_WITH_TIMES = 8                          # sotto questa soglia ci si ferma
UA = {"User-Agent": "orari-cinema/1.0 (uso personale, 1 richiesta al secondo)"}
GIORNI = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
        "agosto", "settembre", "ottobre", "novembre", "dicembre"]
STOP = {"cinema", "cinemas", "multisala", "multiscreen", "the", "teatro", "sala", "d", "essai", "studio"}
NOISE = {"4k", "restaurata", "restaurato", "versione", "director", "cut"}
MIN_NOTTOLA_CINEMAS = 15
NOTTOLA = "https://www.nottolasera.it"


def norm(s):
    s = s.replace("’", " ").replace("'", " ")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[^a-z0-9 ]+", " ", s.lower()).split())


def key(s):
    return " ".join(t for t in norm(s).split() if t not in STOP)


def match_cinema(name, codes):
    """Trova il codice del cinema (es. ADR) dal nome scritto sul sito."""
    k = key(name)
    best, score = None, 0.0
    for code, mine in codes.items():
        km = key(mine)
        if km == k:
            return code
        r = difflib.SequenceMatcher(None, k, km).ratio()
        if k and km and (k in km or km in k) and min(len(k), len(km)) / max(len(k), len(km)) > 0.5:
            r = max(r, 0.9)
        if r > score:
            best, score = code, r
    return best if score >= 0.8 else None


# ---------------------------------------------------------------- lettura sito
def fetch(url):
    import requests
    r = requests.get(url, headers=UA, timeout=30)
    r.raise_for_status()
    return r.text


TIME = re.compile(r"^\s*(\d{1,2}):(\d{2})\s*$")


def parse_film_page(html, city_name):
    from bs4 import BeautifulSoup, NavigableString
    soup = BeautifulSoup(html, "html.parser")
    title = ""
    if soup.title:
        m = re.match(r"^(.*?)\s+a\s+" + re.escape(city_name) + r"\b", soup.title.get_text(strip=True))
        title = m.group(1).strip() if m else ""
    cinemas, cur, vo = {}, None, False
    for el in (soup.body or soup).descendants:
        if getattr(el, "name", None) == "a":
            m = re.search(r"/cinema/[a-z\-]+/(\d+)/", el.get("href", ""))
            txt = el.get_text(" ", strip=True)
            if m and txt and not txt.upper().startswith("VAI AL"):
                cur = re.sub(r"^CINEMA\s+", "", txt, flags=re.I).strip()
                cur = re.sub(r"[\s\*]+$", "", cur)          # toglie le icone (**) a fine nome
                cur = re.sub(r"\s+\d+$", "", cur)         # toglie il numero finale dell'elenco
                vo = False
                cinemas.setdefault(cur, [])
        elif isinstance(el, NavigableString):
            s = str(el).strip()
            if not s:
                continue
            if "Versione originale" in s:
                vo = True
                continue
            m = TIME.match(s)
            if m and cur is not None:
                t = "%02d:%s" % (int(m.group(1)), m.group(2)) + ("v" if vo else "")
                if t not in cinemas[cur]:
                    cinemas[cur].append(t)
    return title, {c: t for c, t in cinemas.items() if t}


def scrape(city, city_name):
    from bs4 import BeautifulSoup
    base = f"https://www.mymovies.it/cinema/{city}/"
    soup = BeautifulSoup(fetch(base), "html.parser")
    ids = []
    for a in soup.find_all("a", href=True):
        m = re.search(r"\?f=(\d+)", a["href"])
        if m and m.group(1) not in ids:
            ids.append(m.group(1))
    films = {}
    for i in ids:
        time.sleep(1)
        try:
            title, cin = parse_film_page(fetch(f"{base}provincia/?f={i}"), city_name)
        except Exception as e:
            print("  salto film", i, e)
            continue
        if title and cin:
            films[title] = {"id": int(i), "cin": cin}
    print(f"{city_name}: {len(films)} film letti dal sito")
    return films


def parse_nottola_cinema(html):
    """Pagina di un cinema su Nottola Sera -> {titolo film: [orari]} (v = versione originale)."""
    from bs4 import BeautifulSoup, NavigableString
    soup = BeautifulSoup(html, "html.parser")
    res, cur, ino = {}, None, False
    for el in (soup.body or soup).descendants:
        if getattr(el, "name", None) == "a":
            txt = el.get_text(" ", strip=True)
            if re.search(r"/film/\d+/", el.get("href", "")) and txt:
                cur, ino = txt, False
                res.setdefault(cur, [])
        elif isinstance(el, NavigableString) and cur is not None:
            s = str(el).strip()
            if not s:
                continue
            if s.lower().startswith("orari"):
                ino = True
                s = s[5:]
            if ino:
                for m in re.finditer(r"(\d{1,2})[.:](\d{2})\s*(V\.?\s?O\.?\s?S?\.?)?", s):
                    h, mi = int(m.group(1)), int(m.group(2))
                    if h < 24 and mi < 60:
                        t = "%02d:%02d" % (h, mi) + ("v" if m.group(3) else "")
                        if t not in res[cur]:
                            res[cur].append(t)
    return {k: v for k, v in res.items() if v}


def scrape_nottola():
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(fetch(NOTTOLA + "/"), "html.parser")
    cin = {}
    for a in soup.find_all("a", href=True):
        m = re.search(r"/cinema/(\d+)/?$", a["href"])
        if m and a.get_text(strip=True):
            cin[m.group(1)] = a.get_text(" ", strip=True)
    out = {}
    for cid, name in cin.items():
        time.sleep(1)
        try:
            out[name] = parse_nottola_cinema(fetch(f"{NOTTOLA}/cinema/{cid}"))
        except Exception as e:
            print("  salto cinema", name, e)
    print(f"Nottola Sera: {len(out)} cinema letti")
    return out


def fkey(t):
    return " ".join(x for x in norm(t).split() if x not in NOISE and len(x) > 1 and not re.fullmatch(r"\d{4}", x))


# ---------------------------------------------------------------- scrittura pagine
def tkey(t):
    h, m = int(t[:2]), int(t[3:5])
    return (h + 24 if h < 6 else h) * 60 + m


JS_STR = r'"(?:[^"\\]|\\.)*"'


def apply(html, films, city_name, today, nott=None):
    block = re.search(r"/\*DATA_START\*/(.*?)/\*DATA_END\*/", html, re.S)
    if not block:
        raise RuntimeError("marcatori DATA_START/DATA_END non trovati")
    cin_block = re.search(r"var CIN=\{.*?\};", html, re.S).group(0)
    codes = {c: json.loads(n) for c, n in re.findall(r"([A-Z]{2,3}):\[(" + JS_STR + ")", cin_block)}
    old = re.findall(r"\[(" + JS_STR + "),(" + JS_STR + "),(" + JS_STR + r")\]", block.group(1).split("var MID")[0])
    old_mid = json.loads(re.search(r"var MID=(\{.*?\});", block.group(1), re.S).group(1))
    by_key = {fkey(json.loads(t)): json.loads(t) for t, g, d in old}

    def canon(title):
        k = fkey(title)
        if k in by_key:
            return by_key[k]
        close = difflib.get_close_matches(k, list(by_key), n=1, cutoff=0.9)
        return by_key[close[0]] if close else title

    # 1) MyMovies: film -> {codice: orari}
    mm, ids = {}, {}
    for title, f in films.items():
        ck = canon(title)
        ids[ck] = f["id"]
        for cname, times in f["cin"].items():
            code = match_cinema(cname, codes)
            if code:
                mm.setdefault(ck, {}).setdefault(code, set()).update(times)
    # 2) Nottola Sera (solo Roma): film -> {codice: orari}
    nt, ncodes = {}, set()
    for cname, fl in (nott or {}).items():
        code = match_cinema(cname, codes)
        if not code:
            continue
        ncodes.add(code)
        for ftitle, times in fl.items():
            nt.setdefault(canon(ftitle), {}).setdefault(code, set()).update(times)
    # 3) unione: per i cinema letti da Nottola vale Nottola; MyMovies solo per gli altri cinema
    #    e per i film che Nottola non riporta
    per_film = {}
    for ck in set(mm) | set(nt):
        if ck in nt:
            per = dict(nt[ck])
            for code, tt in mm.get(ck, {}).items():
                if code not in ncodes:
                    per[code] = tt
        else:
            per = mm[ck]
        per_film[ck] = per

    def data_of(per):
        return ";".join(c + " " + " ".join(sorted(t, key=tkey)) for c, t in per.items() if t)

    old_titles = {json.loads(t) for t, g, d in old}
    with_times = sum(1 for ck, per in per_film.items() if data_of(per))
    prima = sum(1 for t, g, d in old if json.loads(d))
    minimo = max(MIN_FILMS_WITH_TIMES, int(0.6 * prima))
    if with_times < minimo:
        raise RuntimeError(f"{city_name}: solo {with_times} film con orari (ne servono almeno {minimo}), lascio la pagina com'era")

    rows, mid = [], {}
    for t, g, d in old:
        T = json.loads(t)
        data = data_of(per_film.get(T, {}))
        if T in per_film and ids.get(T):
            mid[T] = ids[T]
        elif T in old_mid:
            mid[T] = old_mid[T]
        rows.append("[" + t + "," + g + "," + json.dumps(data, ensure_ascii=False) + "]")
    for ck, per in per_film.items():
        if ck not in old_titles and data_of(per):
            rows.append("[" + json.dumps(ck, ensure_ascii=False) + ',"In programmazione",' + json.dumps(data_of(per), ensure_ascii=False) + "]")
            if ids.get(ck):
                mid[ck] = ids[ck]
    new_block = ("var D=[\n" + ",\n".join(rows) + "\n];\nvar MID=" + json.dumps(mid, ensure_ascii=False) + ";\n")
    html = html[:block.start(1)] + new_block + html[block.end(1):]

    data_it = f"{GIORNI[today.weekday()]} {today.day} {MESI[today.month - 1]} {today.year}"
    html = re.sub(r"Programmazione di [a-zì]+ \d{1,2} [a-z]+ \d{4}\.", f"Programmazione di {data_it}.", html, count=1)
    fonte = ("Nottola Sera e, per i film che Nottola non riporta, da MyMovies" if ncodes else "MyMovies")
    note = (f"Orari di {data_it}, presi da {fonte}, aggiornati in automatico ogni giorno. "
            f"Sono aggiornati {with_times} film: gli altri hanno la scritta «orari sul sito» e, nella scheda, "
            "il link agli orari di oggi su MyMovies. Gli incassi sono totali in Italia e non si aggiornano da soli. "
            "Il prezzo è indicato solo dove il sito lo riporta. La prenotazione è dimostrativa, non fa nessun pagamento. "
            "“VO” indica la versione originale con sottotitoli.")
    html = re.sub(r'<p class="note">.*?</p>', lambda m: '<p class="note">' + note + "</p>", html, count=1, flags=re.S)
    return html, with_times


RETRIES = 3          # tentativi per città
WAIT = 300           # secondi di attesa tra un tentativo e l'altro


def main():
    sys.stdout.reconfigure(line_buffering=True)
    today = datetime.datetime.now(ZoneInfo("Europe/Rome")).date()
    offline = None
    if "--offline" in sys.argv:
        offline = json.load(open(sys.argv[sys.argv.index("--offline") + 1], encoding="utf-8"))
    done, failed = [], []
    for city, name in CITIES.items():
        files = sorted(DOCS.glob(city + "*.html"))
        if not files:
            continue
        ok = False
        for attempt in range(1, RETRIES + 1):
            try:
                films = offline[city] if offline else scrape(city, name)
                nott = None
                if city == "roma":
                    try:
                        nott = offline.get("nottola") if offline else scrape_nottola()
                        if nott is not None and len(nott) < MIN_NOTTOLA_CINEMAS:
                            print(f"::warning::Nottola Sera: solo {len(nott)} cinema letti, uso solo MyMovies")
                            nott = None
                    except Exception as e:
                        print(f"::warning::Nottola Sera non letto ({e}), uso solo MyMovies")
                        nott = None
                out = [(p, apply(p.read_text(encoding="utf-8"), films, name, today, nott)) for p in files]
                for p, (html, n) in out:
                    p.write_text(html, encoding="utf-8")
                    print(f"{p.name}: aggiornato ({n} film con orari)")
                ok = True
                break
            except Exception as e:
                print(f"::warning::{name}, tentativo {attempt}/{RETRIES}: {e}")
                if attempt < RETRIES and not offline:
                    time.sleep(WAIT)
        (done if ok else failed).append(name)
    if failed:
        print("::warning::Non aggiornate (restano come prima): " + ", ".join(failed))
    if not done:
        raise SystemExit("Nessuna città aggiornata")


if __name__ == "__main__":
    main()
