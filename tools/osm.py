import json, urllib.request, urllib.parse
Q = """
[out:json][timeout:60];
area["name"="Castellanza"]["boundary"="administrative"]->.a;
(
  way(area.a)["highway"]["name"~"^(Corso Sempione|Via Nizzolina|Via Lombardia|Via Guglielmo Marconi|Via Marconi|Via Gabrio Piola|Via Piave|Corso Matteotti|Corso Giacomo Matteotti|Via Luigi Pomini|Via Pomini|Via Sanguinola)$"];
);
out geom tags;
"""
data = urllib.parse.urlencode({"data": Q}).encode()
req = urllib.request.Request("https://overpass-api.de/api/interpreter", data=data, headers={"User-Agent": "castellanza-cantieri/1.0"})
res = json.load(urllib.request.urlopen(req, timeout=120))
out = []
for el in res.get("elements", []):
    if el.get("type") == "way":
        out.append({"id": el["id"], "name": el["tags"].get("name"), "oneway": el["tags"].get("oneway"),
                    "highway": el["tags"].get("highway"), "nodes": el.get("nodes"),
                    "geom": [[round(p["lat"], 6), round(p["lon"], 6)] for p in el.get("geometry", [])]})
json.dump(out, open("tools/osm_strade.json", "w"), ensure_ascii=False)
print(len(out), "ways")
