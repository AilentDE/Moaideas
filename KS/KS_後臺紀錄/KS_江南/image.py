import os
import time
import math
import pymongo
import requests
from datetime import datetime
from bs4 import BeautifulSoup

def Bot_Message(channel, text):
    payload={
        "token":os.getenv('API_KEY'),
        "channel":channel,
        "text":'{}'.format(text)} 
    r = requests.post("https://slack.com/api/chat.postMessage", params=payload) 

if __name__=='__main__':
    MONGODB = os.getenv('MONGODB')
    EMAIL = os.getenv('EMAIL')
    PASS = os.getenv('PASSWORD')

    try:
        while True:
            start = time.time()
            rs = requests.Session()
            url = 'https://www.kickstarter.com/login?then=%2Fprojects%2Fmoaideas%2Fjiangnan-life-of-gentry-re%2Fdashboard%3Fref%3Dcreator_nav'
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
                'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"'
            }
            r = rs.get(url, headers=headers, timeout=10)

            myclient = pymongo.MongoClient(MONGODB)
            db = myclient.jiangnan_re
            ttime = datetime.now()

            '''
            statu data
            '''
            submit = {}
            # login (reffer dashboard)
            url = 'https://www.kickstarter.com/user_sessions'
            rs.headers.update({
                'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
                'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"'
                })
            data = {
                'utf8': '✓',
                'authenticity_token': BeautifulSoup(r.text, 'html5lib').find('input', attrs={'name': 'authenticity_token'})['value'],
                'source': 'login',
                'then': '/projects/moaideas/jiangnan-life-of-gentry-re/dashboard?ref=creator_nav',
                'user_session[email]': EMAIL,
                'user_session[password]': PASS,
                'commit': '登入',
                'user_session[remember_me]': '0',
                'user_session[remember_me]': '1'
            }
            r = rs.post(url, data=data, timeout=10)
            for x,y in zip(BeautifulSoup(r.text, 'html5lib').select_one('.stats-numbers').select('.gray-colored'), BeautifulSoup(r.text, 'html5lib').select_one('.stats-numbers').select('h1')):
                submit[x.text.strip()] = y.text.strip()
            for x,y in zip(BeautifulSoup(r.text, 'html5lib').select_one('.flex.mr2').select('.type-14'), BeautifulSoup(r.text, 'html5lib').select_one('.flex.mr2').select('.type-38')):
                submit[x.text.strip()] = y.text.strip()
            submit['date'] = ttime
            collection = db.statu
            collection.insert_one(submit)
            print('Save STATU data at {}'.format(datetime.now()))

            '''
            reffer data
            '''
            submit = []
            r = rs.get('https://www.kickstarter.com/project_referrers/refs/stats?project_id=142191257', timeout=10)
            for i in range(1, math.ceil(r.json()['total']/20)+1):
                r = rs.get('https://www.kickstarter.com/project_referrers/refs/stats?page={}&project_id=142191257'.format(i), timeout=10)
                for x in r.json()['data']:
                    x['date'] = ttime
                    submit.append(x)
            collection = db.reffer
            collection.insert_many(submit)
            print('Save REFFER data at {}'.format(datetime.now()))

            myclient.close()
            rs.close()
            
            time.sleep(3600-(time.time()-start))
    except Exception as e:
        print(e)
        Bot_Message('spider_status', '{}'.format(e))