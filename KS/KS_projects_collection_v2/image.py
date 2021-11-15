import requests
from bs4 import BeautifulSoup
import os
import json
import pymongo
import math
import time
from datetime import datetime

'''
時間阻斷器
'''
def time_start(hour):
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
Slack 通知
'''
def Bot_Message(channel, text):
    payload={
        "token":os.getenv('API_KEY'),
        "channel":channel,
        "text":'{}'.format(text)} 
    r = requests.post("https://slack.com/api/chat.postMessage", params=payload) 

if __name__=="__main__":
    MONGODB = os.getenv('MONGODB')
    time_start(datetime.now().hour+1)
    print('執行時間：\n', datetime.now())

    try:
        while True:
            runtime = datetime.now().strftime('%Y-%m-%dT%H:00:00Z')
            pyclient = pymongo.MongoClient(MONGODB)
            db = pyclient.ks_upcoming
            rs = requests.Session()

            total = ''
            url = 'https://www.kickstarter.com/discover/advanced?state=upcoming&category_id=34&sort=magic&seed=2727675&page=1'
            r = rs.get(url, timeout=10)
            for i in BeautifulSoup(r.text, 'html5lib').select_one('.count.ksr-green-500').text:
                if i.isdigit():
                    total+=i
            total = math.ceil(int(total)/12)

            for i in range(1, total+1):
                url = 'https://www.kickstarter.com/discover/advanced?state=upcoming&category_id=34&sort=magic&seed=2727675&page={}'.format(i)
                r = rs.get(url, timeout=10)
                token = BeautifulSoup(r.text, 'html5lib').find('meta', attrs={'name': 'csrf-token'})['content']
                for data in BeautifulSoup(r.text, 'html5lib').select('.js-react-proj-card.grid-col-12.grid-col-6-sm.grid-col-4-lg'):
                    urlid = data['data-pid']
                    urlf = json.loads(data['data-project'])['urls']['web']['project']
                    url = 'https://www.kickstarter.com/graph'
                    rs.headers.update(
                        {'content-type':'application/json',
                        'x-csrf-token':'{}'.format(token)}
                    )
                    payloads = {
                        "operationName": "PrelaunchPage",
                        "variables": {
                        "slug": "{}/{}".format(urlf.split('/')[-2], urlf.split('/')[-1])
                        },
                        "query": "query PrelaunchPage($slug: String!) {\n  me {\n    id\n    isKsrAdmin\n    __typename\n  }\n  project(slug: $slug) {\n    id\n    name\n    location {\n      discoverUrl\n      displayableName\n      countryName\n      __typename\n    }\n    state\n    description\n    url\n    imageUrl(width: 1000)\n    prelaunchActivated\n    isWatched\n    watchesCount\n    category {\n      url\n      name\n      parentCategory {\n        name\n        __typename\n      }\n      __typename\n    }\n    verifiedIdentity\n    creator {\n      id\n      name\n      slug\n      hasImage\n      imageUrl(width: 48)\n      url\n      biography\n      backingsCount\n      isFacebookConnected\n      lastLogin\n      websites {\n        url\n        domain\n        __typename\n      }\n      launchedProjects {\n        totalCount\n        __typename\n      }\n      location {\n        displayableName\n        __typename\n      }\n      __typename\n    }\n    collaborators {\n      edges {\n        node {\n          name\n          url\n          imageUrl(width: 48)\n          __typename\n        }\n        title\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
                    }
                    r = rs.post(url, data=json.dumps(payloads), timeout=5)
                    db[urlid].insert_one(
                        {
                            'date': runtime,
                            'watchesCount': r.json()['data']['project']['watchesCount']
                        }
                    )
                    time.sleep(1)
            pyclient.close()
            rs.close()
            time_start(datetime.now().hour+1)
    except Exception as e:
        print(e)
        Bot_Message('spider_status', '【KS_upcoming】{}'.format(e))