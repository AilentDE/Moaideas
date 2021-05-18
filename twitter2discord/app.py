import os
import requests
import json
import time
from datetime import datetime
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
twitter_token = os.getenv("TWITTER_TOKEN")
proxima_webhook = os.getenv("PROXIMA_WEBHOOK")

de_time = '2021-05-07T10:30:00Z'
query_str = '(%23遙的繪本 OR %23萊菈art) -is:retweet'

def twitter_request(time=de_time, query_str=query_str, twitter_token=twitter_token):
    url = 'https://api.twitter.com/2/tweets/search/recent?query='+query_str+\
    '&start_time='+time+\
    '&tweet.fields=created_at&expansions=author_id&user.fields=name'
    
    headers = {
        "Authorization": "Bearer {}".format(twitter_token)
    }
    return requests.get(url, headers=headers).json()

def discord_webhook(text_message, webhook_url=proxima_webhook):
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        "content": text_message
    }
    return requests.post(webhook_url, data=json.dumps(payload), headers=headers)

def datetimePLUS1(time_str):
    return (datetime.strptime(time_str[:-5], '%Y-%m-%dT%H:%M:%S') + timedelta(seconds=1)).strftime('%Y-%m-%dT%H:%M:%SZ')

if __name__=='__main__':
    while True:
        try:
            result = twitter_request(de_time)
            if 'data' in result:
                for i in range(len(result['data'])-1, -1, -1):
                    temp_time = result['data'][i]['created_at']
                    discord_webhook('https://twitter.com/proxima_gallery/status/'+result['data'][i]['id'])
                    print('【新創作】 datetime： '+temp_time)
                    de_time = datetimePLUS1(temp_time)
            else:
                pass
            time.sleep(10) #limited by 450 requests per 15-minute window (app auth)
        except:
            print("Something Warning")