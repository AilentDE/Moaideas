import os
import requests
import time
import sqlite3
from datetime import datetime, date

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
def create_db():
    db = sqlite3.connect('data/HLKdata.db')
    cur = db.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS subscriber (id integer PRIMARY KEY AUTOINCREMENT, date date, name text, subscriberCount integer, videoCount integer, viewCount integer)''')
    db.commit()
    db.close()

def save_data(data):
    db = sqlite3.connect('data/HLKdata.db')
    cur = db.cursor()
    cur.executemany("INSERT INTO subscriber(date, name, subscriberCount, videoCount, viewCount) VALUES (?, ?, ?, ?, ?)", data)
    db.commit()
    db.close()


if __name__=='__main__':
    print('執行時間：\n', datetime.now())
    API_KEY = os.getenv('API_KEY')
    HARUKA = os.getenv('HARUKA')
    LYRA = os.getenv('LYRA')
    KUYOU = os.getenv('KUYOU')
    WEBHOOK = os.getenv('WEBHOOK')
    create_db()

    yesterday = {}
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
        
        save_data(collect)
        if yesterday != {}:
            for i,name in enumerate(['haruka', 'lyra', 'kuyou']):
                const += '{}: {:,} (+ {:,})\n'.format(name, int(collect[i][2]), int(collect[i][2])-int(yesterday[name]))
                yesterday[name] = collect[i][2]
        else:
            for i,name in enumerate(['haruka', 'lyra', 'kuyou']):
                const += '{}: {:,}\n'.format(name, int(collect[i][2]))
        response = requests.post(WEBHOOK, json={"content": const}, timeout=5)