import os
import re
import requests
import json
import time


def readfile2018(filepath):
    cwdpath = os.getcwd()
    # Read a file
    with open(cwdpath + "\\myapp\\BPU2018.html", "rt", encoding='utf-8') as in_file:
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
    with open(cwd_path + "\\myapp\\BPU2019_2.html", "rt", encoding='utf-8') as in_file:
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
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             + "Chrome/54.0.2840.99 Safari/537.36"}
    return requests.get(url, params=para, headers=headers)


# 本函数接受b站up主的mid号，根据其关注者的总数多次请求不同的pn，将结果暂存于文件
# 本函数返回up主关注人员的mid字典
# 字典定义：键为mid，值为用户名
def request_follow(mid):
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

    follower_dict = {}
    for users in follow_data_list:
        follower_dict[users['mid']] = users['uname']
    # with open(os.getcwd() + '\\response\\follow\\' + str(mid), 'a', encoding='utf-8') as f:
    #     f.write(str(follower_dict))

    return follower_dict


# 本函数接受b站up主的mid号，返回up主的热门视频
# 返回值1为作者投稿分区的字典
# 返回值2为作者所有视频的字典
# 返回值3为作者所有合作视频的字典
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
        t_dict[item['name']] = item['count']

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

        if len(vlist) > 150 or cur_pn > 5:
            break

    # with open(os.getcwd() + '\\response\\videos\\' + str(mid), 'a', encoding='utf-8') as f:
    #     f.write(str(vlist))

    aid_dict = {}
    union_vid_dict = {}
    for videos in vlist:
        # 向字典添加视频
        aid_dict[videos['aid']] = videos['title']
        # 提取所有合作视频
        if videos['is_union_video'] == 1:
            union_vid_dict[videos['aid']] = videos['title']

    return t_dict, aid_dict, union_vid_dict


# 本函数接受av号作为输入，返回up主的前40条热评中所有的用户id，名字
def get_replies(aid):
    replies_list = []
    default_url = "https://api.bilibili.com/x/v2/reply?"

    for i in range(2):
        para = {'oid': aid,
                'type': 1,
                'pn': i + 1,
                'sort': 2}
        response = request_get(default_url, para)
        response.encoding = 'utf-8'
        # 解析收到的json
        replies_list += json.loads(response.text)['data']['replies']

    reply_dict = {}
    for reply in replies_list:
        reply_dict[reply['member']['mid']] = reply['member']['uname']
        if reply['replies'] is not None:
            for subreply in reply['replies']:
                reply_dict[subreply['member']['mid']] = subreply['member']['uname']

    return reply_dict


# 本函数接受合作视频的av号作为输入，返回所有合作成员mid字典
def get_staff(aid):
    response = request_get("https://www.bilibili.com/video/av" + str(aid), {})
    response.encoding = 'utf-8'

    search_staff = re.search('"staffData":\[.+?\]', response.text)
    staff_dict = {}
    if search_staff:
        try:
            staffData = json.loads(search_staff.group()[12:])

            if len(staffData) > 1:
                for staff in staffData:
                    staff_dict[staff['mid']] = staff['name']
        except Exception as e:
            print(e)

    return staff_dict

