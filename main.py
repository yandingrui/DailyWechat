from wechatpy import WeChatClient
import os
import json
from datetime import datetime, timedelta
import requests
import math
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import random

nowtime = datetime.utcnow() + timedelta(hours=8)
today = datetime.strptime(str(nowtime.date()), "%Y-%m-%d")


def get_time():
    dictDate = {'Monday': '星期一', 'Tuesday': '星期二', 'Wednesday': '星期三', 'Thursday': '星期四',
                'Friday': '星期五', 'Saturday': '星期六', 'Sunday': '星期天'}
    a = dictDate[nowtime.strftime('%A')]
    return nowtime.strftime("%Y年%m月%d日") + a

def add_spaces(text, interval=20):
    return ' '.join(text[i:i+interval] for i in range(0, len(text), interval))

def get_words():
    words = requests.get("https://api.shadiao.pro/chp")
    words.encoding = 'utf-8'
    if words.status_code != 200:
        return get_words()
    return add_spaces(words.json()['data']['text'])

def get_weather(city, key):
    url = f"https://api.seniverse.com/v3/weather/daily.json?key={key}&location={city}&language=zh-Hans&unit=c&start=-1&days=5"
    res = requests.get(url).json()
    print(res)
    weather = (res['results'][0])["daily"][0]
    city = (res['results'][0])["location"]["name"]
    return city, weather

def get_count(born_date):
    delta = today - datetime.strptime(born_date, "%Y-%m-%d")
    return delta.days


def get_birthday(birthday):
    nextdate = datetime.strptime(str(today.year) + "-" + birthday, "%Y-%m-%d")
    if nextdate < today:
        nextdate = nextdate.replace(year=nextdate.year + 1)
    return (nextdate - today).days
    
def split_and_assign_text():
    try:
        # 获取文本
        text = get_words()
        if not text:
            return '', '', '', ''
            
        # 计算需要分割的次数
        total_length = len(text)
        chunk_size = 22
        
        # 分割前三个部分
        words = text[:chunk_size] if total_length > 0 else ''
        words1 = text[chunk_size:chunk_size*2] if total_length > chunk_size else ''
        words2 = text[chunk_size*2:chunk_size*3] if total_length > chunk_size*2 else ''
        
        # 将剩余部分合并到words3
        words3 = text[chunk_size*3:] if total_length > chunk_size*3 else ''
        
        return word, word1, word2, word3
        
    except Exception as e:
        print(f"Error occurred: {e}")
        return '', '', '', ''

if __name__ == '__main__':
    app_id = os.getenv("APP_ID")
    app_secret = os.getenv("APP_SECRET")
    template_id = os.getenv("TEMPLATE_ID")
    weather_key = os.getenv("WEATHER_API_KEY")

    client = WeChatClient(app_id, app_secret)
    wm = WeChatMessage(client)

    f = open("./users_info.json", encoding="utf-8")
    js_text = json.load(f)
    f.close()
    data = js_text['data']
    num = 0
    words=get_words()
    #words, words1, words2, words3 = split_and_assign_text()
    out_time=get_time()

    print(words, out_time)

    for user_info in data:
        born_date = user_info['born_date']
        birthday = born_date[5:]
        city = user_info['city']
        user_id = user_info['user_id']
        name = user_info['user_name'].upper()


        wea_city,weather = get_weather(city,weather_key)
        data = dict()
        data['time'] = {'value': out_time}
        data['words'] = {'value': words}
        data['words1'] = {'value': words1}
        data['words2'] = {'value': words2}
        data['words3'] = {'value': words3}
        data['weather'] = {'value': weather['text_day']}
        data['city'] = {'value': wea_city}
        data['tem_high'] = {'value': weather['high']}
        data['tem_low'] = {'value': weather['low']}
        data['born_days'] = {'value': get_count(born_date)}
        data['birthday_left'] = {'value': get_birthday(birthday)}
        data['wind'] = {'value': weather['wind_direction']}
        data['name'] = {'value': name}
        print(data)
        res = wm.send_template(user_id, template_id, data)
        print(res)
        num += 1
    print(f"成功发送{num}条信息")
