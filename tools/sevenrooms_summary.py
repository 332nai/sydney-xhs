"""对一批SevenRooms餐厅做空位体检：两人、晚市（17:30到20:30之间开始），
往后扫N天，统计周五周六晚上最早哪天能直接订、未来4周有几个周末晚上能订、平日最早哪天。
用法：python3 tools/sevenrooms_summary.py 天数 slug1 slug2 ..."""
import sys, json, urllib.request, datetime as dt, time
N = int(sys.argv[1]); venues = sys.argv[2:]; d0 = dt.date.today()
def fetch(v, s):
    u = f"https://www.sevenrooms.com/api-yoa/availability/widget/range?venue={v}&time_slot=19:00&party_size=2&halo_size_interval=16&start_date={s}&num_days=3&channel=SEVENROOMS_WIDGET"
    for _ in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=30))["data"]["availability"]
        except Exception: time.sleep(2)
    return {}
res = {}
for v in venues:
    days = {}
    for k in range(0, N, 3):
        for day, shs in fetch(v, (d0 + dt.timedelta(k)).strftime("%m-%d-%Y")).items():
            ok = [t["time"] for sh in shs if not sh.get("is_closed") for t in sh.get("times", [])
                  if t.get("type") == "book" and "17:30" <= t["time"] <= "20:30"]
            anyslot = any(t.get("type") == "book" for sh in shs for t in sh.get("times", []))
            open_ = any(sh.get("times") for sh in shs)
            days[day] = (ok, anyslot, open_)
        time.sleep(.3)
    ds = sorted(days); D = lambda s: dt.date.fromisoformat(s)
    wk = [d for d in ds if D(d).weekday() in (4, 5) and days[d][2]]
    wk_ok = [d for d in wk if days[d][0]]
    wd_ok = [d for d in ds if D(d).weekday() < 4 and days[d][0]]
    near = [d for d in wk if (D(d) - d0).days < 28]
    nb = sum(1 for d in near if days[d][0])
    res[v] = dict(first_weekend=wk_ok[0] if wk_ok else None, first_weekday=wd_ok[0] if wd_ok else None,
                  weekend_next4w=f"{nb}/{len(near)}", any_book=any(x[1] for x in days.values()),
                  last_open=max((d for d in ds if days[d][2]), default=None))
    print(v, res[v], flush=True)
json.dump(res, open(f"/home/claude/hard/sr_{d0}.json", "w"), indent=1)
