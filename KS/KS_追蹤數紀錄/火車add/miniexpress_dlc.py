import os
import requests
from bs4 import BeautifulSoup
import json
import sqlite3
import time
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
        self.db = sqlite3.connect('data/Watches.db')
        self.cur = self.db.cursor()

    def create_db(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS jiangnan(id integer PRIMARY KEY AUTOINCREMENT, date date, watches integer)''')
        self.db.commit()

    def save_data(self, data):
        self.cur.execute("INSERT INTO jiangnan(date, watches) VALUES (?, ?)", data)
        self.db.commit()

    def search_by_date(self, key):
        return self.cur.execute("SELECT date, watches FROM jiangnan WHERE date = (?)", (key,))
    
    def close_db(self):
        self.db.close()

def Bot_Message(channel, text):
    payload={
        "token":os.getenv('API_KEY'),
        "channel":channel,
        "text":'{}'.format(text)} 
    r = requests.post("https://slack.com/api/chat.postMessage", params=payload) 

if __name__ == '__main__':
    project_url = 'https://www.kickstarter.com/projects/moaideas/mini-express-map-pack-expansion-1-and-2'
    db = db_method()
    db.create_db()
    db.close_db()

    try:
        while True:
            db = db_method()
            today = db.search_by_date(date.today()).fetchone()
            if not today:
                # get csrf
                headers = {
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
                    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"'
                }
                r1 = requests.get(project_url, headers=headers)
                token = BeautifulSoup(r1.text, 'html5lib').find('meta', attrs={'name':'csrf-token'})['content']
                cookies = r1.cookies['_ksr_session']

                # get data
                url = 'https://www.kickstarter.com/graph'
                headers = {'content-type':'application/json',
                            'cookie':'_ksr_session={}'.format(cookies),
                            'x-csrf-token':'{}'.format(token),
                            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
                            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"'}
                key_word_list = project_url.split('/')
                payloads = {
                    "operationName": "PrelaunchPage",
                    "variables": {
                        "slug": "moaideas/mini-express-map-pack-expansion-1-and-2"
                    },
                    "query": "query PrelaunchPage($slug: String!) {\n  me {\n    id\n    isKsrAdmin\n    __typename\n  }\n  project(slug: $slug) {\n    id\n    name\n    location {\n      discoverUrl\n      displayableName\n      countryName\n      __typename\n    }\n    state\n    description\n    url\n    imageUrl(width: 1000)\n    prelaunchActivated\n    isWatched\n    watchesCount\n    category {\n      url\n      name\n      parentCategory {\n        name\n        __typename\n      }\n      __typename\n    }\n    verifiedIdentity\n    creator {\n      id\n      name\n      slug\n      hasImage\n      imageUrl(width: 48)\n      url\n      biography\n      backingsCount\n      isFacebookConnected\n      lastLogin\n      websites {\n        url\n        domain\n        __typename\n      }\n      launchedProjects {\n        totalCount\n        __typename\n      }\n      location {\n        displayableName\n        __typename\n      }\n      __typename\n    }\n    collaborators {\n      edges {\n        node {\n          name\n          url\n          imageUrl(width: 48)\n          __typename\n        }\n        title\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
                }
                r = requests.post(url, data=json.dumps(payloads), headers=headers)
                jsdata = json.loads(r.text)
                db.save_data((date.today(), jsdata['data']['project']['watchesCount']))

                yesterday = db.search_by_date((date.today()-timedelta(days=1))).fetchone()
                today = db.search_by_date(date.today()).fetchone()
                db.close_db()
                if yesterday:
                    msg = '● Mini Express: Map Pack Expansion 1 & 2：{:,} 名 跟隨者  ({:+d})'.format(today[1], today[1]-yesterday[1])
                else:
                    msg = '● Mini Express: Map Pack Expansion 1 & 2：{:,} 名 跟隨者'.format(today[1])
                Bot_Message('kickstarter_news', msg)
                time_start(9)

            else:
                db.close_db()
                print('Already data today.')
                time_start(9)
    except Exception as e:
        print(e)
        Bot_Message('spider_status', '{}'.format(e))