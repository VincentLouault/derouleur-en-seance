# Relaie les fils RSS de Public Sénat et de LCP en un fichier JSON lisible par le dérouleur.
import json, re, urllib.request, xml.etree.ElementTree as ET, email.utils, sys
from datetime import datetime
from zoneinfo import ZoneInfo
FLUX = [("Public Sénat", "https://www.publicsenat.fr/feed"), ("LCP", "https://lcp.fr/rss-actualites.xml")]
out = {"maj": None, "sources": {}}
for nom, url in FLUX:
    items = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (derouleur-en-seance)"})
        root = ET.fromstring(urllib.request.urlopen(req, timeout=30).read())
        for it in root.iter("item"):
            t = (it.findtext("title") or "").strip(); l = (it.findtext("link") or "").strip(); d = it.findtext("pubDate")
            ts = None
            if d:
                try: ts = int(email.utils.parsedate_to_datetime(d).timestamp() * 1000)
                except Exception: ts = None
            if ts is None:
                # LCP : pas de date de publication, mais « le Vendredi 20 novembre 2026 à 10:43 » dans le résumé (heure de Paris).
                m = re.search(r"(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})\s+à\s+(\d{1,2}):(\d{2})", it.findtext("description") or "", re.I)
                if m:
                    mois = ["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"].index(m.group(2).lower()) + 1
                    ts = int(datetime(int(m.group(3)), mois, int(m.group(1)), int(m.group(4)), int(m.group(5)), tzinfo=ZoneInfo("Europe/Paris")).timestamp() * 1000)
            if t and l.startswith("http"): items.append({"titre": t, "lien": l, "date": ts, "source": nom})
            if len(items) >= 12: break
    except Exception as e:
        print(nom, "erreur :", e, file=sys.stderr)
    out["sources"][nom] = items
import time; out["maj"] = int(time.time() * 1000)
json.dump(out, open("actus.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print({k: len(v) for k, v in out["sources"].items()})
