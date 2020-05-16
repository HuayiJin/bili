import os
import re
import requests
import json
import time
SLEEP_TIME = 0.2

def readfile2018(filepath):
    cwdpath = os.getcwd()
    # Read a file
    with open(cwdpath + "/myapp/BPU2018.html", "rt", encoding='utf-8') as in_file:
        text = in_file.read()
        urls = re.findall('https://space.bilibili.com/\\d+', text)
        # print(urls)
        names = re.findall('<strong>.+?</strong>', text)

        userdict = {}
        for i in range(100):
            # print(urls[i + 1] + '  ' + names[i])
            name = names[i][8:-9]
            # print(name)
            mid = int(urls[i + 1][27:])
            # print(mid)
            userdict[mid] = name
    return userdict


def readfile2019(file_path):
    cwd_path = os.getcwd()
    # Read a file
    with open(cwd_path + "/myapp/BPU2019_2.html", "rt", encoding='utf-8') as in_file:
        text = in_file.read()
        urls = re.findall('//space.bilibili.com/\\d+', text)
        # print(len(urls))
        names = re.findall('span class="vip-name-check.+?</span>', text)
        # print(len(names))
        userdict = {}
        for i in range(100):
            mid = int(urls[2 * i][21:])
            url = 'https:' + urls[2 * i]
            name = re.search('>.+?<', names[i]).group()[1:-1]
            userdict[mid] = name
    return userdict


def request_get(url, para):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             + "Chrome/54.0.2840.99 Safari/537.36"}
    return requests.get(url, params=para, headers=headers)

'''
以下所有函数的userSet为百大up主的集合，仅考虑百大之间的互动
'''

# 本函数接受b站up主的mid号，根据其关注者的总数多次请求不同的pn
# 本函数返回up主关注人员的mid字典
# 字典定义：键为mid，值为用户名
def request_follow(mid, userSet):
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

    if total_follow_nums > 50:
        # 关注者多于50个，有多页需要请求
        time.sleep(SLEEP_TIME)
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

    follower_dict = {}
    for users in follow_data_list:
        mid = int(users['mid'])
        if mid in userSet:
            follower_dict[mid] = users['uname']

    return follower_dict


# 本函数接受b站up主的mid号，返回up主的热门视频
# 返回值1为作者最多投稿的分区
# 返回值2为作者所有视频的字典列表，按照20年，19年，18年分为三个字典
# 返回值3为作者所有合作视频的字典，按照20年，19年，18年分为三个字典
# 如果视频日期晚于2018年，则再请求30条（一页）直到请求到无返回。
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

    t_dict = {}
    for item in tlist.values():
        t_dict[item['count']] = item['name']
    t_dict2 = sorted(t_dict.keys(), reverse=True)
    area = t_dict[t_dict2[0]]

    while vlist[-1]['created'] > 1514736000:
        # 本页最后的视频晚于18年发布，追溯更多页
        # 直到新页中无视频或者最后的视频早于18年
        cur_pn += 1   
        time.sleep(SLEEP_TIME)
        print("searching page ", cur_pn)
        para = {'mid': mid,
                'order': 'pubdate',
                'tid': 0,
                'ps': 30,
                'pn': cur_pn}
        response = request_get(default_url, para)
        response.encoding = 'utf-8'
        new_vlist = json.loads(response.text)['data']['list']['vlist']

        if len(new_vlist) < 1:
            break
        else:
            vlist += new_vlist

    # [{2020}, {2019}, {2018}]
    aid_list = [{},{},{}]
    union_vid_list = [{},{},{}]
    for videos in vlist:
        if videos['created'] > 1577808000:
            year = 0
        elif videos['created'] > 1546272000:
            year = 1
        elif videos['created'] > 1514736000:
            year = 2
        else:
            break

        # 向字典添加视频
        aid_list[year][videos['aid']] = videos['title']
        # 提取所有合作视频
        if videos['is_union_video'] == 1:
            union_vid_list[year][videos['aid']] = videos['title']

    return area, aid_list, union_vid_list


# 本函数接受av号作为输入，返回up主的前20条热评中百大up的id
# 本函数使用myid以排除自评
# 本函数接受userSet作为输入，排除非百大的评论。
def get_replies(aid, myid, userSet):
    default_url = "https://api.bilibili.com/x/v2/reply?"

    para = {'oid': aid,
            'type': 1,
            'pn': 1,
            'sort': 2}
    response = request_get(default_url, para)
    response.encoding = 'utf-8'
    # 解析收到的json
    
    raw_replies = json.loads(response.text)
    reply_set = set()

    try:
        replies_list = raw_replies['data']['replies']
        for reply in replies_list:
            mid = int(reply['member']['mid'])
            if mid != myid and mid in userSet:
                reply_set.add(mid)
            if reply['replies'] is not None:
                for subreply in reply['replies']:
                    submid = int(subreply['member']['mid'])
                    if submid != myid and submid in userSet:
                        reply_set.add(submid)
    except Exception as e:
        print(e)

    return reply_set


# 本函数接受合作视频的av号作为输入，返回所有合作成员mid(int型)
# 本函数通过myid和userSet排除本人及非百大up
def get_staff(aid, myid, userSet):
    response = request_get("https://www.bilibili.com/video/av" + str(aid), {})
    response.encoding = 'utf-8'

    search_staff = re.search('"staffData":\[.+?\]', response.text)
    staff_set = set()
    if search_staff:
        try:
            staffData = json.loads(search_staff.group()[12:])

            if len(staffData) > 1:
                for staff in staffData:
                    mid = int(staff['mid'])
                    if mid != myid and mid in userSet:
                        staff_set.add(mid)
        except Exception as e:
            print(e)

    return staff_set

