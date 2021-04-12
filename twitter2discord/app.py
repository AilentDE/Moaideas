import os
import requests
import json
import time
from datetime import datetime
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
twitter_token = os.getenv("TWITTER_TOKEN")
haruka_webhook = os.getenv("HARUKA_WEBHOOK")
lyra_webhook = os.getenv("LYRA_WEBHOOK")
haruka_id = os.getenv("HARUKA_ID")
lyra_id = os.getenv("LYRA_ID")


haruka_time = '2021-04-12T07:30:00Z'
lyra_time = '2021-04-12T07:30:00Z'

def twitter_request(time, tid, twitter_token=twitter_token):
    url = 'https://api.twitter.com/2/users/'+tid+\
    '/tweets?start_time='+time+\
    '&tweet.fields=created_at&exclude=replies'
    
    headers = {
        "Authorization": "Bearer {}".format(twitter_token)
    }
    return requests.get(url, headers=headers).json()

def discord_webhook(text_message, webhook_url):
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
        # Haruka check
        result = twitter_request(haruka_time, haruka_id)
        if 'data' in result:
            for i in range(len(result['data'])-1, -1, -1):
                temp_time = result['data'][i]['created_at']
                discord_webhook('@haruka_owl https://twitter.com/haruka_owl/status/'+result['data'][i]['id'], haruka_webhook)
                print('【小遙發送了推文】 datetime： '+temp_time)
                haruka_time = datetimePLUS1(temp_time)
        else:
            pass
        
        # lyra check
        result = twitter_request(lyra_time, lyra_id)
        if 'data' in result:
            for i in range(len(result['data'])-1, -1, -1):
                temp_time = result['data'][i]['created_at']
                discord_webhook('@cygnus_lyra https://twitter.com/cygnus_lyra/status/'+result['data'][i]['id'], lyra_webhook)
                print('【萊菈發送了推文】 datetime： '+temp_time)
                lyra_time = datetimePLUS1(temp_time)
        else:
            pass
        
        time.sleep(1) #limited by 900 request / 15 min