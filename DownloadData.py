#!/usr/bin/env python
# -*- coding: utf-8 -*-

from concurrent import futures
from time import sleep
import os
import json
import requests

api = 'https://api.crypko.ai/crypkos/{}/detail'

proxy_list = []

# def get_proxy():
#     global proxy_list

#     if len(proxy_list) == 0:
#         res = requests.get('http://xxxx/get_all').json()
#         proxy_list = res

#     return proxy_list.pop()


headers = {
    'Access-Control-Request-Method': 'GET',
    'Origin': 'https://crypko.ai',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko',
    'Accept': '*/*',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Access-Control-Request-Headers': 'address,authorization',
}


def get_detail(cid):
    global cnt, MAX_CNT, n
    while True:
        try:
            # proxy = res = 'get proxy error'
            # proxy = get_proxy()
            res = requests.get(api.format(cid), headers=headers, timeout=5)
            # res = requests.get(api.format(cid), proxies={'HTTPS': 'http://' + proxy}, headers=headers, timeout=5)
            cnt += 1

            if 'MAX_CNT' in globals():
                print('[{:.2f}%][{} / {}] Download #{}'.format(cnt / MAX_CNT * 100, n, MAX_CNT, cid))

            return res.json()
        except Exception as e:
            print(e, res)
            print('failed to download #{}, asking for new proxy'.format(cid))
            # requests.get('http://xxxx/delete?proxy=' + proxy)

if not os.path.exists('./new_data'):
    os.mkdir('./new_data')

try:
    MIN_CNT = 500 * (max(int(i) for i in os.listdir('./new_data') if i.isdigit()) + 1)
except ValueError:
    MIN_CNT = 0
cnt = n = MIN_CNT
INTERVAL = 500

while True:

    res = get_detail(MIN_CNT + INTERVAL)

    if res.get('error'):
        print('no new cards, sleeping for 600s...')
        sleep(600)
        continue
    else:
        MAX_CNT = MIN_CNT + INTERVAL

    data = []

    with futures.ThreadPoolExecutor(max_workers=25) as executor:

        tasks = executor.map(get_detail, range(MIN_CNT, MAX_CNT))

        for cid, ret in zip(range(MIN_CNT, MAX_CNT), tasks):
            data.append(ret)
            n += 1

    print("write new_data/{}".format(MIN_CNT // INTERVAL))
    with open('new_data/{}'.format(MIN_CNT // INTERVAL), 'w') as f:
        json.dump(data, f, indent=1)

    MIN_CNT = MAX_CNT
    cnt = n = MIN_CNT

    print('finish, sleeping for 60s...')
    sleep(60)
