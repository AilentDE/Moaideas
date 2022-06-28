import requests
from bs4 import BeautifulSoup
import os
import json
import sqlite3
import time
from datetime import datetime, date, timedelta

# 時間阻斷
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

# 請求預設
def request(tag='', org=''):
    url = 'https://web.pcc.gov.tw/prkms/tender/common/basic/readTenderBasic'
    payload = {
        'pageSize': 50,
        'firstSearch': 'true',
        'searchType': 'basic',
        'level_1': 'on',
        'orgName': org,
        'orgId': '',
        'tenderName': tag,
        'tenderId': '',
        'tenderType': 'TENDER_DECLARATION',
        'tenderWay': 'TENDER_WAY_ALL_DECLARATION',
        'dateType': 'isSpdt',
        'tenderStartDate': '',
        'tenderEndDate': '',
        'radProctrgCate': ''
    }
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }
    return requests.get(url, params=payload, headers=header, timeout=5)

# 發送至TEAMS WEBHOOK
TOKEN = os.getenv('TOKEN')
def Bot_Message(message=[{"type": "TextBlock",'text': '**No new tender now.**'}]):
    url = TOKEN
    headers = {
        'Content-type': 'application/json'
    }
    data = {
    "type":"message",
        "attachments":[
            {
                "contentType":"application/vnd.microsoft.card.adaptive",
                "contentUrl": '',
                "content":{
                    "$schema":"http://adaptivecards.io/schemas/adaptive-card.json",
                    "type":"AdaptiveCard",
                    "version":"1.2",
                    "body": message
                }
            }
        ]
    }
    requests.post(url, headers=headers, data=json.dumps(data), timeout=5)

# 資料庫設置
class db_method:

    def __init__(self):
        self.db = sqlite3.connect('data/tender.db')
        self.cur = self.db.cursor()

    def create_db(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS tender (id integer PRIMARY KEY AUTOINCREMENT, tender_id text, tender_name text, url text, start_date text, end_date text, budget integer, save_date date)")
        self.db.commit()

    def save_datas(self, data):
        self.cur.executemany("INSERT INTO tender(tender_id, tender_name, url, start_date, end_date, budget, save_date) VALUES (?, ?, ?, ?, ?, ?, ?)", data)
        self.db.commit()

    def old_datas(self, date):
        self.cur.row_factory = lambda cursor, row: row[0]
        temp = self.cur.execute("SELECT tender_id FROM tender WHERE save_date >= (?) ", (date,)).fetchall()
        self.cur.row_factory = None
        return temp
    
    def close_db(self):
        self.db.close()

# data轉格式
def get_list(item):
    number = item.select('td')[2].text.replace('\n', '').replace('\t', '')\
        .split('  var hw = Geps3.CNS.pageCode2Img("')[0].strip()
    if '(更正公告)' in number:
        number = number.replace(' (更正公告)', '')
    name = item.select('td')[2].text.replace('\n', '').replace('\t', '')\
        .split('  var hw = Geps3.CNS.pageCode2Img("')[1].split('");$')[0].strip()
    url = item.select('td')[2].select_one('a')['href'].split('tpam?pk=')[1]
    url = 'https://web.pcc.gov.tw/tps/QueryTender/query/searchTenderDetail?pkPmsMain='+url
    start_date = item.select('td')[6].text.replace('\n', '').replace('\t', '')
    end_date = item.select('td')[7].text.replace('\n', '').replace('\t', '')
    try:
        budget = int(item.select('td')[8].text.replace('\n', '').replace('\t', '').replace(',', '').strip())
    except:
        budget = None
    save_date = date.today()
    return (number, name, url, start_date, end_date, budget, save_date)

# tag設定
tags = ['桌遊','教材', '教具', '桌上遊戲', '桌上型遊戲', '遊戲', '兒童', '益智', '贈品', '禮品', '探索', '紙牌', '沉浸式體驗', '玩具', '解謎', '實境解謎', '文化轉譯']
org_tags=['基隆市文化局']

# 2022月份工作日設定

# 周一到週五放假的日期
HOLIDAY = ["2022-09-09", "2022-10-10", "2023-01-12"]
# 週六週日還要上班的日期
WORKDAY = []

if __name__ == '__main__':
    check_point = 0

    db = db_method()
    db.create_db()
    db.close_db()

    if datetime.now().hour<9 or datetime.now().hour>=15:
        time_start(9)
    else:
        time_start(15)
    print('執行時間：\n', datetime.now())
    
    while check_point <5:
        try:
            # 工作判定器
            today = datetime.now()
            if (today.weekday()<=4) and (today.strftime("%Y-%m-%d") not in HOLIDAY):
                pass
            elif today.strftime("%Y-%m-%d")in WORKDAY:
                pass
            else:
                time_start(9)
                continue

            item_list = []
            '''
            Normal tag
            '''
            for tag in tags:
                    r = request(tag)
                    soup = BeautifulSoup(r.text, 'html5lib')

                    items = soup.select_one('#tpam').select_one('tbody').select('tr')
                    if items[0].text == '無符合條件資料':
                        continue

                    for item in items:
                        item_list.append(get_list(item))
            '''
            Organ tag
            '''
            for org in org_tags:
                    r = request(tag)
                    soup = BeautifulSoup(r.text, 'html5lib')

                    items = soup.select_one('#tpam').select_one('tbody').select('tr')
                    if items[0].text == '無符合條件資料':
                        continue

                    for item in items:
                        item_list.append(get_list(item))
            
            # 去重複當日data
            re_item_list = []
            for data in item_list:
                if data not in re_item_list:
                    re_item_list.append(data)
            item_list = []

            # 去除已經紀錄data
            db = db_method()
            old_tender = db.old_datas(date.today()-timedelta(days=60))
            for item in re_item_list:
                if item[0] not in old_tender:
                    item_list.append(item)
            
            # 發布內容
            if len(item_list) == 0:
                Bot_Message()
            else:
                message = []
                message_count = 0
                for item in item_list:
                    if item[5]:
                        message.append(
                            {
                                'type': 'TextBlock',
                                'text': '[{}]({})\r- 預算: {:,}\r- 截止日期: {}'.format(item[1], item[2], item[5], item[4])
                            }
                        )
                    else:
                        message.append(
                            {
                                'type': 'TextBlock',
                                'text': '[{}]({})\r- 預算: {}\r- 截止日期: {}'.format(item[1], item[2], item[5], item[4])
                            }
                        )
                    message_count +=1
                    if message_count ==10:
                        Bot_Message(message)
                        message = []
                        message_count = 0
                    else:
                        continue
                if message_count == 0:
                    pass
                else:
                    Bot_Message(message)

            # 儲存data
            db.save_datas(item_list)
            db.close_db()

            check_point = 0
            del item_list, re_item_list

            if datetime.now().hour<9 or datetime.now().hour>=15:
                time_start(9)
            else:
                time_start(15)
        except:
            check_point += 1
            Bot_Message([{"type": "TextBlock",'text': '__Here is some **ERROR** appeared__'}])
            time.sleep(5)