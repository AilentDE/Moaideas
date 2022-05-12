import os
import requests
import json
import time
from datetime import datetime
from datetime import timedelta

# from dotenv import load_dotenv
# load_dotenv()

twitter_token = os.getenv("TWITTER_TOKEN")
sub_token = os.getenv('SUB_TOKEN')
webhook = os.getenv("WEBHOOK")
query_str = os.getenv("QUERY_STR")
print(query_str)
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

def find_author_name(author_id, twitter_token=sub_token):
    url = 'https://api.twitter.com/2/users/'+author_id

    headers = {
        "Authorization": "Bearer {}".format(twitter_token)
    }
    return requests.get(url, headers=headers, timeout=5).json()['data']['username']

if __name__=='__main__':
    while True:
        try:
            result = twitter_request(check_time)
            if 'data' in result:
                for i in range(len(result['data'])-1, -1, -1):
                    temp_time = result['data'][i]['created_at']
                    author_name = find_author_name(result['data'][i]['author_id'])
                    discord_webhook('https://twitter.com/'+author_name+'/status/'+result['data'][i]['id']) # 新增本名查詢
                    print('【NEWS】 datetime： '+temp_time)
                    check_time = datetimePLUS1(temp_time)
            else:
                pass
            time.sleep(10) #limited by 450 requests per 15-minute window (app auth)
        except ValueError as e:
            print('[{}] WRONG JSONDECODE: {}'.format(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'), e))
            time.sleep(5)
        except Exception as e:
            print('[{}] Other WRONG: {}'.format(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'), e))
            time.sleep(5)