"""严格版：未来N天里，任何一天、任何时段，只要有晚市（16:30以后）能直接订就算有位。
用法：python3 tools/sevenrooms_strict.py 天数 slug ..."""
import sys, json, urllib.request, datetime as dt, time
N = int(sys.argv[1]); d0 = dt.date.today()
def fetch(v, s):
    u = f"https://www.sevenrooms.com/api-yoa/availability/widget/range?venue={v}&time_slot=19:00&party_size=2&halo_size_interval=16&start_date={s}&num_days=3&channel=SEVENROOMS_WIDGET"
    for _ in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=30))["data"]["availability"]
        except Exception: time.sleep(2)
    return {}
for v in sys.argv[2:]:
    open_days = 0; ok = []
    for k in range(0, N, 3):
        for day, shs in fetch(v, (d0 + dt.timedelta(k)).strftime("%m-%d-%Y")).items():
            if (dt.date.fromisoformat(day) - d0).days >= N: continue
            ts = [t for sh in shs if not sh.get("is_closed") for t in sh.get("times", []) if t["time"] >= "16:30" or t["time"].endswith("PM")]
            if not ts: continue
            open_days += 1
            bk = [t["time"] for t in ts if t.get("type") == "book"]
            if bk: ok.append((day, bk[0], bk[-1]))
    first = ok[0] if ok else None
    print(f"{v}: 开门{open_days}天，能订{len(ok)}天，最早{first}", flush=True)
