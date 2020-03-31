# ccu_crawler

## 目前功能

- 爬作業時間，並將結果導到 gmail 跟 google calendar
  - 可爬 pdf 內容 跟 一般連結
- 爬今日課表
- 爬取公告與討論區內容
- 新增新的投影片到指定路徑

## 使用說明

- 先啟用兩個 api 並將 OAUTH 憑證改為 "credentials.json"，並放到資料夾內
  - 權限調整請參考 google developers 內的說明頁面
  - [calendar api](https://developers.google.com/calendar/quickstart/python)
  - [gmail api](https://developers.google.com/gmail/api/quickstart/python)

- 需要的 package:
```python
requests
bs4
lxml
selenium
pandas
pdfminer3k
google-api-client
pickle
argparse
```
- 執行時加入 `-h` 或 `-help` 可以預覽現有功能
- 第一次啟動時會詢問要以哪個帳號使用 api
  - 接著會將呼叫 api 所需的資訊存到 pickle 裡面
  - 如要更改帳號，刪除掉資料夾內的 `.pickle`

## 0.9

### 重點改動

- 讓 pdf 檔案日期能正常加到行事曆上

### TODO

- 增加 selenium 相關的效能
- 下載 pdf 檔案

### main.py

- `--daily` 參數邏輯上修正
- 把帳密登入的地方移至 parser 底下，讓 `-h` 功能可以正常使用
  - 原先會先輸入帳密，再跳出 -h 並結束

### crawler.py

- key_word list 針對 ML 新增 "Homework Assignment"
- 加強 check_pdf 的嚴謹性 
- get_course 的 pdf 功能修正

### getPDF.py

- 新增 key_word, format list 來處理不同的日期格式與 deadline 的位置

## 0.8

### TODO

- 增加 selenium 相關的效能
- 下載 pdf 檔案
- 測試 pdf 檔案日期是否能正常加到行事曆上

### main.py

- 新增 `--daily` 參數
  - 是否要爬取今日課表與其公告
  
### crawler.py

- 將作業日期改用 dict 資料結構
  - title: date

### goapi.py

- add_event(): 新增 `from_today` 參數
  -  檢查作業日期是否已經過期
    -  以避免把過期的作業加到行事曆上

- 新增 check_repetitive() 函式
  - **避免 403 error**
  - 檢查是否有重複的內容在行事曆上
  - 以保持行事曆的乾淨

## 0.7

### TODO

- 增加 selenium 相關的效能
- 下載 pdf 檔案

### main.py

- 改成 input + getpass 來獲得使用者資訊
- 改用 argparse 來控制參數

### crawler.py

- 新增檔案名稱更改功能
- 修正 download 下載時的太快關閉的bug
- 爬取上課教材到指定路徑
  - 在同個目錄下

## 0.6

### TODO

- 爬取上課教材到指定路徑
  - 在同個目錄下?
  - 或是一門課一個路徑?

### crawler.py

- 修正找到隱藏的 icon 導致的錯誤
  - 作業連結沒有 title 這個屬性
  - pdf 尚未確認

- 新增 get_ctopics
  - 爬取公告

- daily_curriculum: 時間合併，並檢查是否有作業 

### goapi.py

- `add_event`:新增防呆、提醒、邀請用戶功能
