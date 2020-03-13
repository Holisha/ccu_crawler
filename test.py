import re


string = """今天(星期五)課表
[ 一 | 二 | 三 | 四 | 五 | 六 | 日 ]
時間 課程 地點
13:15~14:30 深度學習概論 創新大樓341
14:45~16:00 深度學習概論 創新大樓341
18:10~19:00 專題實驗（一） 工學院A館101
19:10~20:00 專題實驗（一） 工學院A館101
20:10~21:00 專題實驗（一） 工學院A館101
21:10~22:00 專題實驗（一） 工學院A館101"""

string = string.split('\n')
string.pop(1)

previous = string[2]
idx = 3
for tmp in string[3:]:

    if tmp[12:] == previous[12:]:
        print(tmp[7:11])
        string[idx] = tmp.replace(tmp[7:11] ,previous[7:11])
        string.pop(idx-1)
    else:
        idx += 1
        
    previous = tmp

print("\n".join(string))