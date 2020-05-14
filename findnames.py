# -*- coding: utf-8 -*-
import os
import json
import requests
import time
import pandas as pd
from myapp import get_names


class User:
    '''用户类，包括名字，mid，以及主页地址'''

    def __init__(self, mid, name):
        self.mid = mid
        self.name = name


# 本函数接受b站up主的mid号，请求api，根据其关注者的总数多次请求不同的pn，将结果暂存于文件
def request_follow(mid, dir):
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

# 本函数接受b站up主的mid号，请求api，将结果暂存于文件
# 获取up主的热门视频，如果视频日期晚于2018年，则再请求30条（一页）直到请求到无返回。
def find_videos(mid):
    cur_pn = 1
    default_url = "https://api.bilibili.com/x/space/arc/search?"
    para = {'mid': mid,
            'order': 'pubdate',
            'tid': 0,
            'ps': 30,
            'pn': cur_pn}
    response = request_get(default_url, para)
    response.encoding = 'utf-8'
    # 解析收到的json
    all_videos = json.loads(response.text)

    tlist = all_videos['data']['list']['tlist']
    vlist = all_videos['data']['list']['vlist']
    aid_list = []

    for videos in vlist:
        aid_list.append(videos['aid'])

    while vlist[-1]['created'] > 1514736000:
        # 本页最后的视频晚于18年发布，追溯更多页
        cur_pn += 1
        time.sleep(1)

        response = request_get(default_url, para)
        response.encoding = 'utf-8'
        new_vlist = json.loads(response.text)['data']['list']['vlist']

        if len(new_vlist) < 1:
            break

        for videos in new_vlist:
            vlist.append(videos)
            aid_list.append(videos['aid'])

        if len(vlist) > 100 or cur_pn > 5:
            break

    with open(os.getcwd() + '\\response\\videos\\' + str(mid), 'a', encoding='utf-8') as f:
        f.write(str(vlist))

    print(aid_list)
    return tlist, aid_list


# 本函数接受av号作为输入，返回up主的前40条热评中所有的用户id，名字
def get_replies(aid, mid):
    replies_list = []
    reply_member_set = set()
    default_url = "https://api.bilibili.com/x/v2/reply?"

    for i in range(2):
        para = {'oid': aid,
                'type': 1,
                'pn': i+1,
                'sort': 2}
        response = request_get(default_url, para)
        response.encoding = 'utf-8'
        # 解析收到的json
        replies_list += json.loads(response.text)['data']['replies']

    for reply in replies_list:
        reply_member_set.add((reply['member']['mid'], reply['member']['uname']))
        if reply['replies'] is not None:
            for subreply in reply['replies']:
                reply_member_set.add((subreply['member']['mid'], subreply['member']['uname']))

    print(reply_member_set)
    return reply_member_set


def request_get(url, para):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             + "Chrome/54.0.2840.99 Safari/537.36"}
    return requests.get(url, params=para, headers = headers)


def find_my_followers(filename):
    with open(os.getcwd() + '\\response\\' + filename, 'r', encoding='utf-8') as f:
        json_file = f.read()
        follow_result = json.loads(json_file)
        total_follow_nums = follow_result['data']['total']

        mid_list = []
        for users in follow_result['data']['list']:
            mid_list.append((users['mid'], users['uname']))
        print(mid_list)


if __name__ == "__main__":
    '''
        bpu2018 = get_names.readfile2018("\\myapp\\BPU2018.html")
        bpu2019 = get_names.readfile2019("\\myapp\\BPU2019_2.html")
    
        rawSet18 = set()
        rawSet19 = set()
        for i in range(100):
            rawSet18.add(bpu2018[i])
            rawSet19.add(bpu2019[i])
    
        setAll = rawSet19 | rawSet18
        setOnly19 = rawSet19 - rawSet18
        setOnly18 = rawSet18 - rawSet19
        setBoth = rawSet18 & rawSet19
    
        print(setBoth)
    
        pdAll = pd.DataFrame(setAll, columns=['mid', 'name'])
        pdOnly19 = pd.DataFrame(setOnly19, columns=['mid', 'name'])
        pdBoth = pd.DataFrame(setBoth, columns=['mid', 'name'])
        pdOnly18 = pd.DataFrame(setOnly18, columns=['mid', 'name'])
        pdGen = pd.concat([pdOnly19, pdBoth, pdOnly18], axis=0, ignore_index=True)
    
        pdGen.to_csv("nameset.csv", index=False, encoding='utf-8')
    
    
        # 获取关注信息的http response
        print(request_follow('32786875', 'bpu19\\'))
    
        #find_my_followers('followtest.json')
    
        #cur_mid = 10100539
        #find_followers(cur_mid)
    '''

    '''
    with open(os.getcwd() + "\\myapp\\judge.json", 'r', encoding='utf-8') as f:
        json_file = f.read()
        judge_result = json.loads(json_file)
        print(( judge_result['data']['replies'][19]['member']['uname']))
    '''

    #MID = '395936853'
    #tlist, aid_list = find_videos(MID)

    get_replies(191273)
    # 获取up主的热门视频，如果视频日期晚于2018年，则再请求30条（一页）直到请求到无返回。

    # 获取up主每个视频的前40条热评。检查其中所有评论人的id，记录于set
