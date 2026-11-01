# Baut dist/: eine einzige index.html (Inhalte + Aufnahmen eingebettet), dazu
# manifest.webmanifest und sw.js, damit die Seite als Homescreen-App offline läuft.
# Vorher: ton.py (Aufnahmen) und icon.py (Icons).
import base64, hashlib, json, os

HIER = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HIER, "dist")

def schluessel(text):
    return hashlib.sha1(text.encode()).hexdigest()[:10]

inhalt = json.load(open(os.path.join(HIER, "inhalt.json")))
schl, ses = {}, {}
for thema in inhalt:
    for e in thema["items"]:
        k = schluessel(e[0])
        schl[e[0]] = k
        if k not in ses:
            daten = open(os.path.join(HIER, "ton", k + ".m4a"), "rb").read()
            ses[k] = "data:audio/mp4;base64," + base64.b64encode(daten).decode()

j = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
html = open(os.path.join(HIER, "vorlage.html")).read()
html = html.replace("__INHALT__", j(inhalt)).replace("__SES__", j(ses)).replace("__SCHLUESSEL__", j(schl))
os.makedirs(DIST, exist_ok=True)
open(os.path.join(DIST, "index.html"), "w").write(html)

manifest = {
    "name": "Merhaba Deutsch", "short_name": "Merhaba", "lang": "tr",
    "start_url": "./", "scope": "./", "display": "standalone",
    "background_color": "#f5f2ea", "theme_color": "#1f5c4a",
    "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
              {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}],
}
open(os.path.join(DIST, "manifest.webmanifest"), "w").write(j(manifest))

version = hashlib.sha1(html.encode()).hexdigest()[:8]
sw = f"""const CACHE='merhaba-{version}';
const DATEIEN=['./','index.html','manifest.webmanifest','icon-180.png','icon-192.png','icon-512.png','rechtliches.html'];
self.addEventListener('install',e=>{{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(DATEIEN.map(u=>new Request(u,{{cache:'reload'}})))));self.skipWaiting()}});
self.addEventListener('activate',e=>{{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))));self.clients.claim()}});
self.addEventListener('fetch',e=>{{if(e.request.method!=='GET')return;
  e.respondWith(caches.match(e.request,{{ignoreSearch:true}}).then(r=>r||fetch(e.request)))}});
"""
open(os.path.join(DIST, "sw.js"), "w").write(sw)
print(f"dist/index.html {len(html) / 1e6:.1f} MB, {len(ses)} Aufnahmen, Version {version}")
