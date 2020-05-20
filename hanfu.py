# -*- coding: utf-8 -*-
import os
import json
import time
import re
import pandas as pd

from myapp import support

SLEEP_TIME = 1 


if __name__ == "__main__":
    rootdir = os.getcwd()
    hot_video_list, user_list = support.readfile_hanfu()

    print(hot_video_list)
    print(user_list)
    hot_video_info_list = []
    user_info_list = []
    for video in hot_video_list:
        temp = support.get_video_info(video)
        print(temp)
        hot_video_info_list.append(temp)
        time.sleep(SLEEP_TIME)

    pd_hot = pd.DataFrame(hot_video_info_list)
    pd_hot.to_excel(rootdir + "\\hanfu\\" + "hot.xlsx", index=True, header=True)

    for user in user_list:
        temp = support.find_videos_simple(user)
        print(temp)
        user_info_list.append(temp)
        time.sleep(SLEEP_TIME)

    pd_user = pd.DataFrame(user_info_list)
    pd_user.to_excel(rootdir + "\\hanfu\\" + "user.xlsx", index=True, header=True)
