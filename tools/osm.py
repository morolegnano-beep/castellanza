import json, urllib.request, urllib.parse
Q = """
[out:json][timeout:60];
area["name"="Castellanza"]["boundary"="administrative"]->.a;
(
  way(area.a)["highway"]["name"~"^(Corso Sempione|Via Nizzolina|Via Lombardia|Viale Lombardia|Via Guglielmo Marconi|Via Marconi|Via Gabrio Piola|Via Piave|Corso Matteotti|Corso Giacomo Matteotti|Via Luigi Pomini|Via Pomini|Via Sanguinola)$"];
  way(45.6125,8.8860,45.6160,8.8980)["highway"]["highway"!~"footway|path|service|steps|cycleway"];
  way(45.6000,8.8800,45.6300,8.9200)["name"~"Lombardia"];
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
                    "highway": el["tags"].get("highway"), "nodes": el.get("nodes"), "ref": el["tags"].get("ref"), "bridge": el["tags"].get("bridge"),
                    "geom": [[round(p["lat"], 6), round(p["lon"], 6)] for p in el.get("geometry", [])]})
json.dump(out, open("tools/osm_strade.json", "w"), ensure_ascii=False)
print(len(out), "ways")
