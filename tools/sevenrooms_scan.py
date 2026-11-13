"""扫SevenRooms空位：python3 tools/sevenrooms_scan.py venue_slug [天数] [人数]
输出每天能直接订（type=book）的时段数，以及晚市有没有位。"""
import sys, json, urllib.request, datetime as dt
v = sys.argv[1]; days = int(sys.argv[2]) if len(sys.argv) > 2 else 56; ps = sys.argv[3] if len(sys.argv) > 3 else "2"
d0 = dt.date.today(); out = {}
for k in range(0, days, 3):
    s = (d0 + dt.timedelta(k)).strftime("%m-%d-%Y")
    u = f"https://www.sevenrooms.com/api-yoa/availability/widget/range?venue={v}&time_slot=19:00&party_size={ps}&halo_size_interval=16&start_date={s}&num_days=3&channel=SEVENROOMS_WIDGET"
    try: j = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=30))
    except Exception as e: print("ERR", e); break
    if j.get("status") != 200: print(j.get("msg")); break
    for day, shifts in j["data"]["availability"].items():
        rec = {}
        for sh in shifts:
            cat = sh.get("shift_category"); bk = [t["time"] for t in sh.get("times", []) if t.get("type") == "book"]
            if sh.get("is_closed"): continue
            rec.setdefault(cat, []).extend(bk)
        out[day] = rec
for day in sorted(out):
    wd = dt.date.fromisoformat(day).strftime("%a")
    r = out[day]; print(day, wd, " ".join(f"{c}:{len(t)}" + (f"({t[0]}..{t[-1]})" if t else "") for c, t in r.items()) or "closed")
