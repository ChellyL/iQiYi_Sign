# -*- coding: utf8 -*-

from json import dumps

import hashlib
import random
import requests
import string
import telegram
import time
import os

# 爱奇艺cookie
P00001 = "8**********从Cookie中找***********f"
P00003 = "1**********从Cookie中找***********6"
dfp = "a**********从Cookie中找***********6"

# tg token
token = '你的频道token'
userid = '你的tgid'

# pushplus微信推送
pushplustoken = ""
############################################

tasks = ["8a2186bb5f7bedd4", "b6e688905d4e7184", "acf8adbb5870eb29", "843376c6b3e2bf00", "8ba31f70013989a8",
         "CHANGE_SKIN"]  # 浏览任务号


# 日志推送至微信
def SendWX(senddata):
    url = "http://www.pushplus.plus/send/"
    data = {
        "token": pushplustoken,
        "title": "爱奇艺签到抽奖",
        "content": senddata
    }
    headers = {'Content-Type': 'application/json'}
    res = requests.post(url, data=dumps(data).encode(encoding='utf-8'), headers=headers)
    print(res.text)


# 日志推送到tg
def SendTG(senddata):
    # os.environ['http_proxy'] = 'http://127.0.0.1:7890' 如果是国内机器自己加代理
    # os.environ['https_proxy'] = 'https://127.0.0.1:7890'
    bot = telegram.Bot(token)
    bot.sendMessage(chat_id=userid, text=senddata)


# 随机字符串 a-z A-Z 0-9
def strRandom(num):
    return ''.join(random.sample(string.ascii_letters + string.digits, num))


# md5加密
def md5(data):
    return hashlib.md5(bytes(data, encoding='utf-8')).hexdigest()


# 13位时间戳
def time_13():
    return round(time.time() * 1000)


# 拼接 连接符 数据 特殊符号（可不填）
def k(c, t, e=None):
    buf = []
    for key, value in t.items():
        buf.append('='.join([key, str(value)]))
    if e != None:
        buf.append(e)
        return (md5(c.join(buf)))
    return (c.join(buf))


# 登录
def login():
    url = "https://serv.vip.iqiyi.com/vipgrowth/query.action?P00001=" + P00001
    res = requests.get(url).json()
    if res['code'] == 'A00000':
        level = res['data']['level']  # VIP等级
        growthvalue = res['data']['growthvalue']  # 当前VIP成长值
        distance = res['data']['distance']  # 升级需要成长值
        deadline = res['data']['deadline']  # VIP到期时间
        today_growth_value = res['data']['todayGrowthValue']  # 今日获得的成长值

        logbuf = (
            f"VIP 等级: {level}\n当前成长值: {growthvalue}\n升级需成长值: {distance}\n今日成长值: {today_growth_value}\nVIP 到期时间: {deadline}")
    else:
        logbuf = (res['msg'])
    print(logbuf)
    return logbuf


# 签到
def Checkin():
    sign_date = {
        "agentType": "1",
        "agentversion": "1.0",
        "appKey": "basic_pcw",
        "authCookie": P00001,
        "qyid": md5(strRandom(16)),
        "task_code": "natural_month_sign",
        "timestamp": time_13(),
        "typeCode": "point",
        "userId": P00003
    }
    post_date = {
        "natural_month_sign": {
            "agentType": "1",
            "agentversion": "1",
            "authCookie": P00001,
            "qyid": md5(strRandom(16)),
            "taskCode": "iQIYI_mofhr",
            "verticalCode": "iQIYI"
        }
    }
    sign = k('|', sign_date, "UKobMjDMsDoScuWOfp6F")
    url = f"https://community.iqiyi.com/openApi/task/execute?{k('&', sign_date)}&sign={sign}"
    header = {
        'Content-Type': 'application/json'
    }
    res = requests.post(url, headers=header, data=dumps(post_date)).json()
    if res['code'] == 'A00000':
        if res['data']['code'] == 'A0000':
            quantity = res['data']['data']['rewards'][0]['rewardCount']  # 积分
            addgrowthvalue = res['data']['data']['rewards'][0]['rewardCount']  # 新增成长值
            continued = res['data']['data']['signDays']  # 签到天数
            logbuf = (f"签到成功: 获得积分{quantity}, 成长值{addgrowthvalue}，累计签到{continued}天")
        else:
            logbuf = (f"签到失败：{res['data']['msg']}")
    else:
        logbuf = (f"签到失败：{res['message']}")
    print(logbuf)

    return logbuf


# 网页签到
def WebCheckin():
    web_sign_date = {
        "agenttype": "1",
        "agentversion": "0",
        "appKey": "basic_pca",
        "appver": "0",
        "authCookie": P00001,
        "channelCode": "sign_pcw",
        "dfp": dfp,
        "scoreType": "1",
        "srcplatform": "1",
        "typeCode": "point",
        "userId": P00003,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
        "verticalCode": "iQIYI"
    }
    sign = k('|', web_sign_date, "DO58SzN6ip9nbJ4QkM8H")
    url = f"https://community.iqiyi.com/openApi/score/add?{k('&', web_sign_date)}&sign={sign}"
    res = requests.get(url).json()
    if res['code'] == 'A00000':
        if res['data'][0]['code'] == 'A0000':
            quantity = res['data'][0]['score']  # 积分
            continued = res['data'][0]['continuousValue']  # 累计签到天数
            logbuf = (f"网页端签到成功: 获得积分{quantity}, 累计签到{continued}天")
        else:
            logbuf = (f"网页端签到失败：{res['data'][0]['message']}")
    else:
        logbuf = (f"网页端签到失败：{res['message']}")
    print(logbuf)
    return logbuf


# 抽奖
def Lottery():
    url = f"https://iface2.iqiyi.com/aggregate/3.0/lottery_activity?app_k=0&app_v=0&platform_id=0&dev_os=0&dev_ua=0&net_sts=0&qyid=0&psp_uid=0&psp_cki={P00001}&psp_status=0&secure_p=0&secure_v=0&req_sn=0"
    res = requests.get(url).json()
    if res['code'] == 0:
        try:
            logbuf = (f"抽奖失败：{res['kv']['msg']}")
        except:
            logbuf = (f"抽奖成功：{res['title']}-{res['awardName']},剩余抽奖次数{res['daysurpluschance']}次")
            print(logbuf)
            return [int(res['daysurpluschance']), logbuf]
    elif res['code'] == 3:
        logbuf = ("抽奖失败：Cookie失效")
    else:
        logbuf = ("抽奖失败：未知错误")
    print(logbuf)
    return [0, logbuf]


# 任务
def joinTask(task):
    url = f"https://tc.vip.iqiyi.com/taskCenter/task/joinTask?taskCode={task}&lang=zh_CN&platform=0000000000000000&P00001={P00001}"
    requests.get(url)


def notifyTask(task):
    url = f"https://tc.vip.iqiyi.com/taskCenter/task/notify?taskCode={task}&lang=zh_CN&platform=0000000000000000&P00001={P00001}"
    requests.get(url)


def getTaskRewards(task):
    url = f"https://tc.vip.iqiyi.com/taskCenter/task/getTaskRewards?taskCode={task}&lang=zh_CN&platform=0000000000000000&P00001={P00001}"
    res = requests.get(url).json()
    if res['msg'] == "成功":
        if res['code'] == 'A00000':
            if res['dataNew'] != []:
                logbuf = (f"浏览奖励成功：{res['dataNew'][0]['name']} {res['dataNew'][0]['value']}")
            else:
                logbuf = False
        else:
            logbuf = (f"浏览奖励失败：{res['msg']}")
    else:
        logbuf = ("浏览奖励失败：cookie无效/接口失效")
    if logbuf:
        print(logbuf)
    return logbuf


def task():
    luckbuf = []
    for i in tasks:
        joinTask(i)
        notifyTask(i)
        time.sleep(5)
        logbuf = getTaskRewards(i)
        if logbuf:
            luckbuf.append(logbuf)
        time.sleep(1)
    return ("\n".join(luckbuf))


# 主程序
def main():
    # 推送消息内容
    push_msg = ""
    rtn_msg = ""

    log = []
    startime = time_13()

    rtn_msg = Checkin()
    push_msg = push_msg + "\n" + rtn_msg
    log.append(rtn_msg)  # 签到
    time.sleep(1)
    rtn_msg = WebCheckin()
    push_msg = push_msg + "\n" + rtn_msg
    log.append(rtn_msg)  # 网页端签到
    time.sleep(1)
    while True:
        lucknum = Lottery()  # 抽奖
        if lucknum[0] != 0:
            rtn_msg = lucknum[1]
            push_msg = push_msg + "\n" + rtn_msg
            log.append(rtn_msg)
            time.sleep(2)
        else:
            rtn_msg = lucknum[1]
            push_msg = push_msg + "\n" + rtn_msg
            log.append(rtn_msg)
            break
    rtn_msg = task()
    push_msg = push_msg + "\n" + rtn_msg
    log.append(rtn_msg)  # 做任务

    rtn_msg = login()
    push_msg = push_msg + "\n" + rtn_msg
    log.insert(0, rtn_msg)  # 登录信息
    endtime = time_13()
    duration = (endtime - startime) / 1000
    rtn_msg = f"共耗时{duration}秒"
    print(rtn_msg)
    push_msg = push_msg + "\n" + rtn_msg
    print("***END***")
    SendTG("\n".join(log))  # 推送到tg
    # SendWX("\n".join(log))  # 推送到微信
 
    return "\n".join(log)


def main_handler(event, context):
    return main()


if __name__ == '__main__':
    main()
