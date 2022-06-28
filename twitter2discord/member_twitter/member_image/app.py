import os
import requests
import json
import time
from datetime import datetime
from datetime import timedelta
# from dotenv import load_dotenv
# load_dotenv()

twitter_token = os.getenv("TWITTER_TOKEN")
webhook = os.getenv("WEBHOOK")
member_name = os.getenv("MEMBER_NAME")
member_id = os.getenv("MEMBER_ID")
check_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

def twitter_request(time, tid, twitter_token=twitter_token):
    url = 'https://api.twitter.com/2/users/'+tid+\
    '/tweets?start_time='+time+\
    '&tweet.fields=created_at&exclude=retweets,replies'
    
    headers = {
        "Authorization": "Bearer {}".format(twitter_token)
    }
    return requests.get(url, headers=headers, timeout=5).json()

def discord_webhook(text_message, webhook_url):
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        "content": text_message
    }
    return requests.post(webhook_url, data=json.dumps(payload), headers=headers, timeout=5)

def datetimePLUS1(time_str):
    return (datetime.strptime(time_str[:-5], '%Y-%m-%dT%H:%M:%S') + timedelta(seconds=1)).strftime('%Y-%m-%dT%H:%M:%SZ')

if __name__=='__main__':
    while True:
        try:
            result = twitter_request(check_time, member_id)
            if 'data' in result:
                for i in range(len(result['data'])-1, -1, -1):
                    temp_time = result['data'][i]['created_at']
                    discord_webhook('https://twitter.com/'+member_name+'/status/'+result['data'][i]['id'], webhook)
                    print('【新通知！】 datetime： '+temp_time)
                    check_time = datetimePLUS1(temp_time)
            else:
                pass

            time.sleep(15) #limited by 300 request / 15 min by APP
        except ValueError as e:
            print('[{}] WRONG JSONDECODE: {}'.format(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'), e))
            time.sleep(5)
        except Exception as e:
            print('[{}] Other WRONG: {}'.format(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'), e))
            time.sleep(5)