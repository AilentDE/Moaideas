import os
import requests
import time
import sqlite3
from datetime import datetime, date, timedelta

'''
時間阻斷器
'''
def time_start(hour):
    # 時
    while True:
        if datetime.now().hour == (hour-1):
            break
        else:
            time.sleep(3600)
            continue

    # 分
    while True:
        if datetime.now().minute == 59:
            break
        else:
            time.sleep(60)
            continue

    # 秒
    while True:
        if datetime.now().second >= 50:
            break
        else:
            time.sleep(5)
            continue

    while True:
        if datetime.now().hour == hour:
            break
        else:
            continue

'''
預設資料庫路徑/app/data/.db
'''
class db_method:

    def __init__(self):
        self.db = sqlite3.connect('data/HLKdata.db')
        self.cur = self.db.cursor()

    def create_db(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS subscriber (id integer PRIMARY KEY AUTOINCREMENT, date date, name text, subscriberCount integer, videoCount integer, viewCount integer)''')
        self.db.commit()

    def save_datas(self, data):
        self.cur.executemany("INSERT INTO subscriber(date, name, subscriberCount, videoCount, viewCount) VALUES (?, ?, ?, ?, ?)", data)
        self.db.commit()

    def search_by_date(self, key):
        return self.cur.execute("SELECT name, subscriberCount FROM subscriber WHERE date = (?)", (key,))
    
    def close_db(self):
        self.db.close()

if __name__=='__main__':
    print('執行時間：\n', datetime.now())
    API_KEY = os.getenv('API_KEY')
    HARUKA = os.getenv('HARUKA')
    LYRA = os.getenv('LYRA')
    KUYOU = os.getenv('KUYOU')
    WEBHOOK = os.getenv('WEBHOOK')
    
    db = db_method()
    db.create_db()
    db.close_db()
    requests.post(WEBHOOK, json={"content": "HLKsee run。"}, timeout=5)

    while True:
        time_start(9)
        collect = []
        ttime = date.today()
        const = ''

        for name,target in zip(['haruka', 'lyra', 'kuyou'], [HARUKA, LYRA, KUYOU]):
            url = 'https://www.googleapis.com/youtube/v3/channels' +\
            '?id='+target +\
            '&key='+API_KEY  +\
            '&part=statistics'

            r = requests.get(url, timeout=3)
            data = r.json()['items'][0]['statistics']
            collect.append((ttime, name, data['subscriberCount'], data['videoCount'], data['viewCount']))
        
        db = db_method()
        db.save_datas(collect)

        yesterday = db.search_by_date((date.today()-timedelta(days=1))).fetchall()
        today = db.search_by_date(date.today()).fetchall()
        db.close_db()

        if yesterday:
            for x, y in zip(yesterday, today):
                const += '{}: {:,} {:+d}\n'.format(y[0], y[1], y[1]-x[1])
        else:
            for y in today:
                const += '{}: {:,}\n'.format(y[0], y[1])
        requests.post(WEBHOOK, json={"content": const}, timeout=5)