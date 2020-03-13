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
flag = False
idx = 3
for tmp in string[3:]:

    if tmp[12:] == previous[12:]:
        if not flag:
            time = previous[:5]
            flag = True
            
        string.pop(idx-1)
    else:
        if flag:
            string[idx-1] = previous.replace(previous[:5], time)
            flag = False

        idx += 1
        
    previous = tmp

if flag:
    string[-1] = tmp.replace(tmp[:5], time)


print("\n".join(string))