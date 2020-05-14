# -*- coding: utf-8 -*-
import re
import os
import pandas as pd
import numpy
import json
import urllib
import requests
import time


class User:
    '''用户类，包括名字，mid，以及主页地址'''

    def __init__(self, mid, name):
        self.mid = mid
        self.name = name


def readfile2018(filepath):
    cwdpath = os.getcwd()
    # Read a file
    with open(cwdpath + filepath, "rt", encoding='utf-8') as in_file:
        text = in_file.read()
        urls = re.findall('https://space.bilibili.com/\\d+', text)
        # print(urls)
        names = re.findall('<strong>.+?</strong>', text)

        userlist = []
        for i in range(100):
            # print(urls[i + 1] + '  ' + names[i])
            name = names[i][8:-9]
            # print(name)
            mid = urls[i + 1][27:]
            # print(mid)
            userlist.append((mid, name))
    return userlist


def readfile2019(file_path):
    cwd_path = os.getcwd()
    # Read a file
    with open(cwd_path + file_path, "rt", encoding='utf-8') as in_file:
        text = in_file.read()
        urls = re.findall('//space.bilibili.com/\\d+', text)
        # print(len(urls))
        names = re.findall('span class="vip-name-check.+?</span>', text)
        # print(len(names))
        userlist = []
        for i in range(100):
            mid = urls[2 * i][21:]
            url = 'https:' + urls[2 * i]
            name = re.search('>.+?<', names[i]).group()[1:-1]
            userlist.append((mid, name))
    return userlist


def request_get(url, para):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/54.0.2840.99 Safari/537.36"}

    return requests.get(url, params=para, headers = headers)


def request_follow(mid, dir):
    # 本函数接受b站up主的mid号，请求api，根据其关注者的总数多次请求不同的pn，将结果暂存于文件
    cur_pn = 1
    default_url = "https://api.bilibili.com/x/relation/followings?"
    para = {'vmid': mid,
            'order': 'desc',
            'pn': cur_pn}

    response = request_get(default_url, para)
    response.encoding = 'utf-8'
    # 解析收到的json
    follow_result = json.loads(response.text)

    total_follow_nums = follow_result['data']['total']
    follow_data_list = follow_result['data']['list']

    if total_follow_nums > 50 :
        # 关注者多于50个，有多页需要请求
        time.sleep(1)
        total_pn = total_follow_nums // 50
        for i in range(total_pn):
            cur_pn += 1
            para = {'vmid': mid,
                    'order': 'desc',
                    'pn': cur_pn}

            response = request_get(default_url, para)
            response.encoding = 'utf-8'
            follow_result = json.loads(response.text)
            follow_data_list += follow_result['data']['list']

    mid_list = []
    for users in follow_data_list:
        mid_list.append((users['mid'], users['uname']))

    with open(os.getcwd() + '\\response\\follow\\' + dir + str(mid), 'a', encoding='utf-8') as f:
        f.write(str(mid_list))

    return mid_list


def find_my_followers(filename):
    with open(os.getcwd() + '\\response\\' + filename, 'r', encoding='utf-8') as f:
        json_file = f.read()
        follow_result = json.loads(json_file)
        total_follow_nums = follow_result['data']['total']

        mid_list = []
        for users in follow_result['data']['list']:
            mid_list.append((users['mid'], users['uname']))
        print(mid_list)


def find_followers(mid):
    # 本函数接受b站up主的mid号，返回其所有关注者的list
    request_follow()


if __name__ == "__main__":
    '''
    bpu2018 = readfile2018("\\myapp\\BPU2018.html")
    bpu2019 = readfile2019("\\myapp\\BPU2019_2.html")

    idSet18 = set()
    idSet19 = set()
    for i in range(100):
        idSet18.add(bpu2018[i][1])
        idSet19.add(bpu2019[i][1])

    pd18 = pd.DataFrame(bpu2018)
    pd19 = pd.DataFrame(bpu2019)
    print(pd18)
    print(idSet18 & idSet19)
    '''
    # 获取关注信息的http response
    print(request_follow('32786875', 'bpu19\\'))

    #find_my_followers('followtest.json')

    #cur_mid = 10100539
    #find_followers(cur_mid)
