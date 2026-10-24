import math, os, time, urllib.request
from PIL import Image
UA={"User-Agent":"sydney-xhs-map/0.1 (ianhao9397@gmail.com)"}
def merc(lat, lon, z):
    n = 256 * 2 ** z
    x = (lon + 180) / 360 * n
    y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n
    return x, y
def fetch_tile(z, x, y):
    os.makedirs("tc", exist_ok=True)
    fp = f"tc/osm_{z}_{x}_{y}.png"
    if not os.path.exists(fp):
        u = f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        for a in range(3):
            try:
                open(fp, "wb").write(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read()); break
            except Exception:
                time.sleep(2)
        time.sleep(0.15)
    return Image.open(fp).convert("RGB")
def render(center_lat, center_lon, z, w, h, scale=1):
    """按缩放级别 z 拼 OSM 瓦片，scale>1 时放大底图（只用于小地图）。"""
    cx, cy = merc(center_lat, center_lon, z)
    ww, hh = int(w / scale) + 2, int(h / scale) + 2
    x0, y0 = cx - ww / 2, cy - hh / 2
    img = Image.new("RGB", (ww, hh), "white")
    for tx in range(int(x0 // 256), int((x0 + ww) // 256) + 1):
        for ty in range(int(y0 // 256), int((y0 + hh) // 256) + 1):
            img.paste(fetch_tile(z, tx, ty), (int(round(tx * 256 - x0)), int(round(ty * 256 - y0))))
    if scale != 1:
        img = img.resize((int(ww * scale), int(hh * scale)), Image.LANCZOS)
    img = img.crop((0, 0, w, h))
    def to_px(lat, lon):
        x, y = merc(lat, lon, z); return (x - x0) * scale, (y - y0) * scale
    return img, to_px
