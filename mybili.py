# -*- coding: utf-8 -*-
import os
import json
import time
import re
import pandas as pd
from myapp import support


class User:
    def __init__(self, mid, name):
        self.mid = mid
        self.name = name

        # 字典定义：键为mid，值为用户名
        self.followers = {}

        # tlist是作者投稿的主要分区的list，键为分区，值为数量
        self.tlist = {}

        # 视频av号字典，键为aid，值为视频标题
        self.myVideos = {}

        # 热评者id字典，键为mid，值为用户名
        self.myResponders = {}

        # 合作伙伴字典，键为mid，值为用户名
        self.myCoworkers = {}

    def get_my_follower(self):
        try:
            self.followers = support.request_follow(self.mid)
        except Exception as e:
            print(e)

    def get_my_video(self):
        self.tlist, self.myVideos, union_vid_dict = support.find_videos(self.mid)

        # 查找我的合作伙伴
        for aid in union_vid_dict.keys():
            self.myCoworkers.update(support.get_staff(aid))
            time.sleep(0.5)

        # 查找我的评论者
        for aid in self.myVideos.keys():
            self.myResponders.update(support.get_replies(aid))
            time.sleep(0.5)

    # 以json输出当前状况
    def print_status(self):
        status = {
            'mid': self.mid,
            'name': self.name,
            'tlist': self.tlist,
            'followers': self.followers,
            'responders': self.myResponders,
            'coworkers': self.myCoworkers
        }
        return json.dumps(status, ensure_ascii=False)


if __name__ == "__main__":
    bpu2018 = support.readfile2018("\\myapp\\BPU2018.html")
    bpu2019 = support.readfile2019("\\myapp\\BPU2019_2.html")

    rawSet18 = set()
    rawSet19 = set()
    for i in range(100):
        rawSet18.add(bpu2018[i])
        rawSet19.add(bpu2019[i])

    setAll = rawSet19 | rawSet18
    setOnly19 = rawSet19 - rawSet18
    setOnly18 = rawSet18 - rawSet19
    setBoth = rawSet18 & rawSet19
    list_all = list(setAll)
    list_all.sort()

    for i in range(len(list_all)):
        cur_mid = list_all[i][0]
        cur_name = list_all[i][1]
        print("No.", i, " Start with: ", cur_mid, " user name: ", cur_name)
        cur_user = User(cur_mid, cur_name)
        cur_user.get_my_follower()
        print("Success getting followers!")
        cur_user.get_my_video()
        print("Success getting video info!")
        with open(os.getcwd() + "\\develop\\" + str(cur_mid) + ".json", 'a', encoding='utf-8') as f:
            f.write(cur_user.print_status())
        print("Success writing into files: ", str(cur_mid))
        time.sleep(10)


    '''
    pdAll = pd.DataFrame(setAll, columns=['mid', 'name'])
    pdOnly19 = pd.DataFrame(setOnly19, columns=['mid', 'name'])
    pdBoth = pd.DataFrame(setBoth, columns=['mid', 'name'])
    pdOnly18 = pd.DataFrame(setOnly18, columns=['mid', 'name'])
    pdGen = pd.concat([pdOnly19, pdBoth, pdOnly18], axis=0, ignore_index=True)

    pdGen.to_csv("nameset.csv", index=False, encoding='utf-8')

    with open(os.getcwd() + "\\myapp\\judge.json", 'r', encoding='utf-8') as f:
        json_file = f.read()
        judge_result = json.loads(json_file)
        print(( judge_result['data']['replies'][19]['member']['uname']))
    '''

    # MID = '395936853'
    # tlist, aid_list = find_videos(MID)

    # get_replies(191273)
    # 获取up主的热门视频，如果视频日期晚于2018年，则再请求30条（一页）直到请求到无返回。

    # 获取up主每个视频的前40条热评。检查其中所有评论人的id，记录于set
    # print(request_get("https://www.bilibili.com/video/BV1LK411W735", {}).text)

    # get_staff(498082939)
    '''
        cur_mid = 62540916
        cur_name = "周六野Zoey"
        print("Start with: ", cur_mid, " user name: ", cur_name)
        cur_user = User(cur_mid, cur_name)
        cur_user.get_my_follower()
        print("Success getting followers!")
        cur_user.get_my_video()
        print("Success getting video info!")
        with open(os.getcwd() + "\\test\\" + str(cur_mid) + ".json", 'a', encoding='utf-8') as f:
            f.write(cur_user.print_status())
        print("Success writing into files: ", str(cur_mid))
    '''