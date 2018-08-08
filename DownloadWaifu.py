#!/usr/bin/env python

from hashlib import sha1
from sys import argv
from concurrent import futures
from os import path, mkdir

import requests

HEADERS = {
    'Access-Control-Request-Method': 'GET',
    'Origin': 'https://crypko.ai',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
    'Accept': '*/*',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Access-Control-Request-Headers': 'address,authorization',
}

def generate_url(crypko):
    salt = 'asdasd3edwasd'
    mes = crypko['noise'] + salt + crypko['attrs']
    return sha1(mes.encode()).hexdigest()

def get_page(owner_addr, page):
    api = 'https://api.crypko.ai/crypkos/search'
    res = requests.get(api, headers=HEADERS, params={
        'category': 'all',
        'page': page,
        'sort': '-id',
        'ownerAddr': owner_addr
    })
    return res.json()

def download(crypko):
    base = 'https://img.crypko.ai/daisy/{}_lg.jpg'

    url = base.format(generate_url(crypko))
    name = '{}.jpg'.format(crypko.get('name', '# ' + str(crypko['id'])))
    return [name, requests.get(url).content]

def main(owner_addr):
    page, cnt, crypkos = 1, 1, []
    print('获取Crypko列表中...')

    # TODO: 这个地方也可以多线程, 然而懒
    while True:
        print('\r第{}页'.format(page), end='')
        tmp = get_page(owner_addr, page)
        total = tmp['totalMatched']
        crypkos.extend(tmp['crypkos'])
        if not tmp['crypkos']:
            print('')
            break
        page += 1

    print('开始下载...')
    with futures.ThreadPoolExecutor(max_workers=25) as executor:
        tasks = executor.map(download, crypkos)
        for name, content in tasks:
            print('\r[{: 02.2f}%] 下载中: {}'.format(cnt / total, name), end='')
            with open('./{}/{}'.format(owner_addr, name), 'wb') as f:
                f.write(content)
            cnt += 1

if __name__ == '__main__':
    if len(argv) != 2:
        print('{} your_wallet_address')
    else:
        if not path.exists(argv[1]):
            mkdir(argv[1])
        main(argv[1])
