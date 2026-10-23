import json, urllib.request, urllib.parse, time
BB = "45.590,8.855,45.640,8.935"
Q = f"""
[out:json][timeout:120];
(
  way({BB})["highway"~"^(motorway|motorway_link|trunk|trunk_link|primary|primary_link|secondary|secondary_link|tertiary|tertiary_link|unclassified|residential|living_street)$"];
);
out body geom;
relation({BB})["type"="restriction"];
out body;
"""
data = urllib.parse.urlencode({"data": Q}).encode()
res = None
for url in ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter", "https://overpass.private.coffee/api/interpreter"]:
    for _ in range(2):
        try:
            r = urllib.request.Request(url, data=data, headers={"User-Agent": "castellanza-cantieri/1.0"})
            res = json.load(urllib.request.urlopen(r, timeout=180)); break
        except Exception as e:
            print("errore", url, e); time.sleep(15)
    if res: break
ways, rels = [], []
for el in res["elements"]:
    if el["type"] == "way":
        t = el["tags"]
        ways.append({"id": el["id"], "nodes": el["nodes"], "geom": [[round(p["lat"], 6), round(p["lon"], 6)] for p in el["geometry"]],
                     "tags": {k: t[k] for k in ("name", "ref", "highway", "oneway", "junction", "access", "motor_vehicle", "maxspeed", "maxweight", "hgv", "bridge") if k in t}})
    elif el["type"] == "relation":
        rels.append({"id": el["id"], "tags": el["tags"], "members": el["members"]})
json.dump({"ways": ways, "restrictions": rels}, open("tools/rete.json", "w"), ensure_ascii=False, separators=(",", ":"))
# v4
print(len(ways), "ways", len(rels), "restrictions")

# v5: cimiteri, ingressi e parcheggi vicini (stampati nel log)
try:
    Q2 = f"""
[out:json][timeout:90];
(way({BB})["landuse"="cemetery"];way({BB})["amenity"="grave_yard"];relation({BB})["landuse"="cemetery"];)->.c;
.c out tags geom;
node(w.c)["entrance"];out;
node(w.c)["barrier"];out;
nwr(around.c:350)["amenity"="parking"];out tags center;
"""
    d2 = urllib.parse.urlencode({"data": Q2}).encode()
    r2 = None
    for url in ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter", "https://overpass.private.coffee/api/interpreter"]:
        try:
            r2 = json.load(urllib.request.urlopen(urllib.request.Request(url, data=d2, headers={"User-Agent": "castellanza-cantieri/1.0"}), timeout=120)); break
        except Exception as e:
            print("errore poi", url, e)
    for el in (r2 or {}).get("elements", []):
        g = el.get("geometry") or []
        c = el.get("center") or ({"lat": el["lat"], "lon": el["lon"]} if "lat" in el else None)
        if g:
            la = [p["lat"] for p in g]; lo = [p["lon"] for p in g]
            print("POI", el["type"], el["id"], json.dumps(el.get("tags", {}), ensure_ascii=False), "bbox", round(min(la),6), round(min(lo),6), round(max(la),6), round(max(lo),6), "geom", json.dumps([[round(p["lat"],6), round(p["lon"],6)] for p in g]))
        else:
            print("POI", el["type"], el["id"], json.dumps(el.get("tags", {}), ensure_ascii=False), "at", c and round(c["lat"],6), c and round(c["lon"],6))
except Exception as e:
    print("errore poi", e)
