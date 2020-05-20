import pandas as pd
import os
import os.path
import json
from myapp import support
import collections

bpu2018 = support.readfile2018("/myapp/BPU2018.html")
bpu2019 = support.readfile2019("/myapp/BPU2019_2.html")
bpu_all = {}
bpu_all.update(bpu2018)
bpu_all.update(bpu2019)

id18 = bpu2018.keys()
id19 = bpu2019.keys()

id_all = id18 | id19
id_only19 = id19 - id18
id_only18 = id18 - id19
id_both = id18 & id19

default_list = []

for item in id_only19:
    default_list.append(str(item))
for item in id_both:
    default_list.append(str(item))
for item in id_only18:
    default_list.append(str(item))

# 按序存储的用户id
default_dict = {}
for ids in default_list:
    default_dict[str(ids)] = 0

print("default list start with ", default_list[:3])
print("default list end with ", default_list[-3:])

rootdir = os.getcwd()
file_list = os.listdir(rootdir + '\\develop2\\')

# 存储整个的关注数据
all_follower_dict = {}
# 存储19年回复
all_reply19_dict = {}
# 存储18年回复
all_reply18_dict = {}
# 存储19年合作者
all_coworker19_dict = {}
# 存储18年合作者
all_coworker18_dict = {}

# 存储所有属性
attribute_dict = {}

for file_name in file_list:
    with open(rootdir + '\\develop2\\' + file_name, 'r', encoding='utf-8') as f:
        user = json.loads(f.read())
        mid = str(user['mid'])
        name = user['name']
        area = user['area']
        my_follower = {}
        for fol in user['followers']:
            my_follower[fol] = 1
        all_follower_dict.update({mid: my_follower})
        all_reply19_dict.update({mid: user['responders19']})
        all_reply18_dict.update({mid: user['responders18']})
        all_coworker19_dict.update({mid: user['coworkers19']})
        all_coworker18_dict.update({mid: user['coworkers18']})
        attribute_dict[mid] = {
            'name': name,
            'area': area,
            'honor': ''
        }

users = []
for u in default_list:
    users.append(int(u))

sum18 = sum19 = 0
for i in users[:100]:
    sum19 += i
for i in users[-100:]:
    sum18 += i

print(sum19)
print(sum18)





# 146 * 146
pd_follower = pd.DataFrame(all_follower_dict, columns=default_list, index=default_list).fillna(value=0).astype(int)
pd_double_follower = pd_follower.values.T & pd_follower
print(pd_double_follower)

pd_reply19 = pd.DataFrame(all_reply19_dict, columns=default_list, index=default_list)
# front 100 * 100
pd_19reply19 = pd_reply19.iloc[:100, :100]
print(pd_19reply19)

pd_reply18 = pd.DataFrame(all_reply18_dict, columns=default_list, index=default_list)
# end 100 * 100
pd_18reply18 = pd_reply18.iloc[-100:, -100:]
print(pd_18reply18)

pd_cowork19 = pd.DataFrame(all_coworker19_dict, columns=default_list, index=default_list)
# front 100 * 100
pd_19cowork19 = pd_cowork19.iloc[:100, :100]
print(pd_19cowork19)

pd_cowork18 = pd.DataFrame(all_coworker18_dict, columns=default_list, index=default_list)
# end 100 * 100
pd_18cowork18 = pd_cowork18.iloc[-100:, -100:]
print(pd_18cowork18)


pd_attribute = pd.DataFrame(pd.DataFrame(attribute_dict).T, index=default_list)
for i in range(0, 46):
    pd_attribute.iloc[i]['honor'] = '19'
for i in range(46, 100):
    pd_attribute.iloc[i]['honor'] = 'both'
for i in range(100, 146):
    pd_attribute.iloc[i]['honor'] = '18'
print(pd_attribute)


pd_follower  .to_excel(rootdir + "\\result\\" + "follower.xlsx"  , index=True, header=True)
pd_reply19   .to_excel(rootdir + "\\result\\" + "reply19.xlsx"   , index=True, header=True)
pd_19reply19 .to_excel(rootdir + "\\result\\" + "reply19_19.xlsx" , index=True, header=True)
pd_reply18   .to_excel(rootdir + "\\result\\" + "reply18.xlsx"   , index=True, header=True)
pd_18reply18 .to_excel(rootdir + "\\result\\" + "reply18_18.xlsx" , index=True, header=True)
pd_cowork19  .to_excel(rootdir + "\\result\\" + "cowork19.xlsx"  , index=True, header=True)
pd_19cowork19.to_excel(rootdir + "\\result\\" + "cowork19_19.xlsx", index=True, header=True)
pd_cowork18  .to_excel(rootdir + "\\result\\" + "cowork18.xlsx"  , index=True, header=True)
pd_18cowork18.to_excel(rootdir + "\\result\\" + "cowork18_18.xlsx", index=True, header=True)
pd_attribute .to_excel(rootdir + "\\result\\" + "attribute.xlsx", index=True, header=True)


pd_double_follower.to_excel(rootdir + "\\result\\" + "double_follower.xlsx"  , index=True, header=True)

