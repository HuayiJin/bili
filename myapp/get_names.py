import os
import re


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
