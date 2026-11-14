import json,urllib.request,time,sys
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'
H={'Park Hyatt':41730116,'Four Seasons':11875,'Shangri-La':3135685,'Pullman Quay Grand':2853,'Crown Towers':32586621,'W Sydney':45622452,
   'Sofitel Darling Harbour':1620140,'Capella':45894224,'Fullerton':9586127,'Langham':11890,'Kimpton Margot':1094057,'QT Sydney':304897,
   'InterContinental Coogee':11703,'QT Bondi':1161419}
date=sys.argv[1]; res={}
for n,i in H.items():
    u=f"https://www.agoda.com/api/cronos/property/BelowFoldParams/GetSecondaryData?hotel_id={i}&checkin={date}&los=1&adults=2&rooms=1"
    for k in range(4):
        try:
            d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':UA}),timeout=40))
            if 'masterRooms' in d.get('roomGridData',{}): break
            print(n,'no rooms yet',flush=True); time.sleep(8)
        except Exception as e: print(n,'retry',e,flush=True); time.sleep(5)
    else: continue
    rooms=[]
    for m in d['roomGridData']['masterRooms']:
        ps=[r['pricing']['displayPrice'] for r in m.get('rooms',[]) if r.get('pricing',{}).get('displayPrice')]
        if ps: rooms.append((m['name'],min(ps)))
    res[n]={'cur':d['currencyInfo']['code'],'name':d['hotelInfo']['name'],'rooms':sorted(rooms,key=lambda x:x[1])}
    print(n,d['hotelInfo']['name'],len(rooms),rooms[:1],rooms[-1:] if rooms else '',flush=True)
    time.sleep(2)
json.dump(res,open(f'prices_{date}.json','w'),indent=1)
