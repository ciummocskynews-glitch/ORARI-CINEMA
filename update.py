#!/usr/bin/env python3
"""Aggiorna gli orari dei cinema (Roma e Bologna) nelle pagine in docs/.

Legge i listini di MyMovies, riscrive il blocco dati di ogni pagina
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
STOP = {"cinema", "cinemas", "multisala", "the", "teatro", "sala", "d", "essai", "studio"}


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


# ---------------------------------------------------------------- scrittura pagine
def tkey(t):
    h, m = int(t[:2]), int(t[3:5])
    return (h + 24 if h < 6 else h) * 60 + m


JS_STR = r'"(?:[^"\\]|\\.)*"'


def apply(html, films, city_name, today):
    block = re.search(r"/\*DATA_START\*/(.*?)/\*DATA_END\*/", html, re.S)
    if not block:
        raise SystemExit("marcatori DATA_START/DATA_END non trovati")
    cin_block = re.search(r"var CIN=\{.*?\};", html, re.S).group(0)
    codes = {c: json.loads(n) for c, n in re.findall(r"([A-Z]{2,3}):\[(" + JS_STR + ")", cin_block)}
    old = re.findall(r"\[(" + JS_STR + "),(" + JS_STR + "),(" + JS_STR + r")\]", block.group(1).split("var MID")[0])
    old_mid = json.loads(re.search(r"var MID=(\{.*?\});", block.group(1), re.S).group(1))
    by_key = {norm(json.loads(t)): json.loads(t) for t, g, d in old}

    new_data = {}      # titolo mio -> {data, id}
    extra = []         # film nuovi
    for title, f in films.items():
        per = {}
        for cname, times in f["cin"].items():
            code = match_cinema(cname, codes)
            if code:
                per.setdefault(code, set()).update(times)
        data = ";".join(c + " " + " ".join(sorted(t, key=tkey)) for c, t in per.items())
        mine = by_key.get(norm(title))
        if mine:
            new_data[mine] = {"data": data, "id": f["id"]}
        else:
            extra.append((title, data, f["id"]))
    with_times = sum(1 for v in new_data.values() if v["data"]) + sum(1 for e in extra if e[1])
    if with_times < MIN_FILMS_WITH_TIMES:
        raise SystemExit(f"{city_name}: solo {with_times} film con orari, mi fermo senza modificare nulla")

    rows, mid = [], {}
    for t, g, d in old:
        T = json.loads(t)
        v = new_data.get(T)
        data = v["data"] if v else ""
        if v:
            mid[T] = v["id"]
        elif T in old_mid:
            mid[T] = old_mid[T]
        rows.append("[" + t + "," + g + "," + json.dumps(data, ensure_ascii=False) + "]")
    for title, data, i in extra:
        rows.append("[" + json.dumps(title, ensure_ascii=False) + ',"In programmazione",' + json.dumps(data, ensure_ascii=False) + "]")
        mid[title] = i
    new_block = ("var D=[\n" + ",\n".join(rows) + "\n];\nvar MID=" + json.dumps(mid, ensure_ascii=False) + ";\n")
    html = html[:block.start(1)] + new_block + html[block.end(1):]

    data_it = f"{GIORNI[today.weekday()]} {today.day} {MESI[today.month - 1]} {today.year}"
    html = re.sub(r"Programmazione di [a-zì]+ \d{1,2} [a-z]+ \d{4}\.", f"Programmazione di {data_it}.", html, count=1)
    note = (f"Orari di {data_it}, presi da MyMovies e aggiornati ogni notte in automatico. "
            f"Sono aggiornati {with_times} film: gli altri hanno la scritta «orari sul sito» e, nella scheda, "
            "il link agli orari di oggi su MyMovies. Gli incassi sono totali in Italia e non si aggiornano da soli. "
            "Il prezzo è indicato solo dove il sito lo riporta. La prenotazione è dimostrativa, non fa nessun pagamento. "
            "“VO” indica la versione originale con sottotitoli.")
    html = re.sub(r'<p class="note">.*?</p>', lambda m: '<p class="note">' + note + "</p>", html, count=1, flags=re.S)
    return html, with_times


def main():
    today = datetime.datetime.now(ZoneInfo("Europe/Rome")).date()
    offline = None
    if "--offline" in sys.argv:
        offline = json.load(open(sys.argv[sys.argv.index("--offline") + 1], encoding="utf-8"))
    results = {}
    for city, name in CITIES.items():
        files = sorted(DOCS.glob(city + "*.html"))
        if not files:
            continue
        films = offline[city] if offline else scrape(city, name)
        results[city] = [(p, apply(p.read_text(encoding="utf-8"), films, name, today)) for p in files]
    for city, lst in results.items():          # scrive solo se tutte le città sono andate bene
        for p, (html, n) in lst:
            p.write_text(html, encoding="utf-8")
            print(f"{p.name}: aggiornato ({n} film con orari)")


if __name__ == "__main__":
    main()
