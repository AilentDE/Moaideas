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
query_str = os.getenv("QUERY_STR")
print(query_str)
proxima_tag = os.getenv("PROXIMA_TAG")
check_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

def twitter_request(time=check_time, query_str=query_str, twitter_token=twitter_token):
    url = 'https://api.twitter.com/2/tweets/search/recent?query='+query_str+\
    '&start_time='+time+\
    '&tweet.fields=created_at&expansions=author_id&user.fields=name'
    
    headers = {
        "Authorization": "Bearer {}".format(twitter_token)
    }
    return requests.get(url, headers=headers, timeout=5).json()

def discord_webhook(text_message, webhook_url=webhook):
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
            result = twitter_request(check_time)
            if 'data' in result:
                for i in range(len(result['data'])-1, -1, -1):
                    temp_time = result['data'][i]['created_at']
                    discord_webhook('https://twitter.com/'+proxima_tag+'/status/'+result['data'][i]['id'])
                    print('【NEWS】 datetime： '+temp_time)
                    check_time = datetimePLUS1(temp_time)
            else:
                pass
            time.sleep(10) #limited by 450 requests per 15-minute window (app auth)
        except ValueError:
            print('[{}] WRONG JSONDECODE'.format(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')))
            time.sleep(10)
        except:
            print('[{}] Other WRONG'.format(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')))
            time.sleep(10)