# -*- coding: utf-8 -*-
import os
import json
import time
import re
from myapp import support

SLEEP_TIME = 0.5

class User:
    def __init__(self, mid, name, userSet, default_list):
        self.mid = mid
        self.name = name
        self.userSet = userSet

        # 字典定义：键为mid，值为用户名
        self.followers = {}

        # area是作者投稿的主要分区
        self.area = ""

        # 视频av号字典列表，键为aid，值为视频标题
        # 第0，1，2项分别为20年、19年、18年的视频
        self.myVideos = []

        # 热评者id字典列表，键为mid，值为评论次数
        self.myResponders19 = default_list
        self.myResponders18 = default_list

        # 合作伙伴字典列表，键为mid，值为合作次数
        self.myCoworkers19 = default_list
        self.myCoworkers18 = default_list

    def get_my_follower(self):
        try:
            self.followers = support.request_follow(self.mid, userSet)
        except Exception as e:
            print(e)

    def get_my_video(self):
        self.area, self.myVideos, union_vid_list = support.find_videos(self.mid)

        # 查找我的合作伙伴
        for aid in union_vid_list[1].keys():
            coworker = support.get_staff(aid, self.mid, self.userSet)
            if len(coworker) > 0:
                for workers in coworker:
                    self.myCoworkers19[workers] += 1
            time.sleep(SLEEP_TIME)

        for aid in union_vid_list[2].keys():
            coworker = support.get_staff(aid, self.mid, self.userSet)
            if len(coworker) > 0:
                for workers in coworker:
                    self.myCoworkers18[workers] += 1
            time.sleep(SLEEP_TIME)

        # 查找我的评论者
        for aid in self.myVideos[1].keys():
            responder = support.get_replies(aid, self.mid, self.userSet)
            if len(responder) > 0:
                for resp in responder:
                    self.myResponders19[resp] += 1
            time.sleep(SLEEP_TIME)

        for aid in self.myVideos[2].keys():
            responder = support.get_replies(aid, self.mid, self.userSet)
            if len(responder) > 0:
                for resp in responder:
                    self.myResponders18[resp] += 1
            time.sleep(SLEEP_TIME)

    # 以json输出当前状况
    def print_status(self):
        status = {
            'mid': self.mid,
            'name': self.name,
            'area': self.area,
            'followers': self.followers,
            'responders19': self.myResponders19,
            'responders18': self.myResponders18,
            'coworkers19': self.myCoworkers19,
            'coworkers18': self.myCoworkers18
        }            
        return json.dumps(status, ensure_ascii=False)


if __name__ == "__main__":
    bpu2018 = support.readfile2018("/myapp/BPU2018.html")
    bpu2019 = support.readfile2019("/myapp/BPU2019_2.html")

    rawSet18 = set()
    rawSet19 = set()
    for i in range(100):
        rawSet18.add(bpu2018[i])
        rawSet19.add(bpu2019[i])

    setAll = rawSet19 | rawSet18
    setOnly19 = rawSet19 - rawSet18
    setOnly18 = rawSet18 - rawSet19
    setBoth = rawSet18 & rawSet19
    default_list = []

    for item in setOnly19:
        default_list.append({item[0]: 0})
    for item in setBoth:
        default_list.append({item[0]: 0})
    for item in setOnly18:
        default_list.append({item[0]: 0})

    print(default_list)
    list_all = list(setAll)
    list_all.sort()

    id_set_all = set()
    for item in list_all:
        id_set_all.add(item[0])

    print(id_set_all)
    
    # for i in range(len(list_all)):
    for i in range(3):
        cur_mid = list_all[i][0]
        cur_name = list_all[i][1]
        print("No.", i, " Start with: ", cur_mid, " user name: ", cur_name)
        cur_user = User(cur_mid, cur_name, id_set_all, default_list)
        cur_user.get_my_follower()
        print("Success getting followers!")
        cur_user.get_my_video()
        print("Success getting video info!")
        with open(os.getcwd() + "/develop/" + str(cur_mid) + ".json", 'a', encoding='utf-8') as f:
            f.write(cur_user.print_status())
        print("Success writing into files: ", str(cur_mid))
        time.sleep(SLEEP_TIME)

    '''
    pdAll = pd.DataFrame(setAll, columns=['mid', 'name'])
    pdOnly19 = pd.DataFrame(setOnly19, columns=['mid', 'name'])
    pdBoth = pd.DataFrame(setBoth, columns=['mid', 'name'])
    pdOnly18 = pd.DataFrame(setOnly18, columns=['mid', 'name'])
    pdGen = pd.concat([pdOnly19, pdBoth, pdOnly18], axis=0, ignore_index=True)

    pdGen.to_csv("nameset.csv", index=False, encoding='utf-8')

    with open(os.getcwd() + "/myapp/judge.json", 'r', encoding='utf-8') as f:
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
        with open(os.getcwd() + "/test/" + str(cur_mid) + ".json", 'a', encoding='utf-8') as f:
            f.write(cur_user.print_status())
        print("Success writing into files: ", str(cur_mid))
    '''