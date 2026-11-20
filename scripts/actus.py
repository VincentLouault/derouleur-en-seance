# Relaie les fils RSS de Public Sénat et de LCP en un fichier JSON lisible par le dérouleur.
import json, urllib.request, xml.etree.ElementTree as ET, email.utils, sys
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
            if t and l.startswith("http"): items.append({"titre": t, "lien": l, "date": ts, "source": nom})
            if len(items) >= 12: break
    except Exception as e:
        print(nom, "erreur :", e, file=sys.stderr)
    out["sources"][nom] = items
import time; out["maj"] = int(time.time() * 1000)
json.dump(out, open("actus.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print({k: len(v) for k, v in out["sources"].items()})
