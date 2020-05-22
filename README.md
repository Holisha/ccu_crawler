# ccu_crawler

## 目前功能

- 每日 00:00 自動執行
- 爬作業時間，並將結果導到 gmail 跟 google calendar
  - 可爬 pdf 內容 跟 一般連結
- 爬今日課表
  - 限平日
- 爬取公告與討論區內容
- 新增新的投影片到指定路徑

### Demo

- 顯示課表與公告

![](https://i.imgur.com/qOCGV45.png)

- 將作業期限新增到行事曆

![](https://i.imgur.com/C7EGao5.png)

- 自動執行

![](https://i.imgur.com/KWCdiH8.png)

- GUI

![](https://i.imgur.com/UGhDEkZ.png)

## 使用說明

- 先啟用兩個 api 並將 OAUTH 憑證改為 "credentials.json"，並放到對應的資料夾內
  - 權限調整請參考 google developers 內的說明頁面
  - [calendar api](https://developers.google.com/calendar/quickstart/python)
  - [gmail api](https://developers.google.com/gmail/api/quickstart/python)

- 需要的 package:
```python
# locally
beautifulsoup4==4.8.2
decorator==4.4.2
google-api-python-client==1.6.7
google-auth==1.11.2
google-auth-httplib2==0.0.3
google-auth-oauthlib==0.4.1
httplib2==0.17.0
lxml==4.5.0
oauth2client==4.1.2
oauthlib==3.1.0
pandas==1.0.1
pdfminer3k==1.3.1
pickleshare==0.7.5
selenium==3.141.0
virtualenv==20.0.4

# gui
PyQt5==5.12.3
PyQt5-sip==4.19.18
PyQtWebEngine==5.12.1
qtconsole==4.7.1
QtPy==1.9.0
PySide2==5.14.2.1

# heroku
APScheduler==3.6.3
dj-database-url==0.5.0
dj-static==0.0.6
gunicorn==20.0.4
```

- 執行時加入 `-h` 或 `-help` 可以預覽現有功能
- 第一次啟動時會詢問要以哪個帳號使用 api
  - 接著會將呼叫 api 所需的資訊存到 pickle 裡面
  - 如要更改帳號，刪除掉資料夾內的 `.pickle`

### 部署到 heroku

- 創建帳號與 app 過程不贅述
  - 詳情參考[實作細節](#實作細節)

- 需要將 `.pickle` 一併上傳到 heroku
- 啟動前需設置環境變數 `USERNAME` 和 `PASSWORD`
  - `heroku config:set USERNAME=your_username`
  - `heroku config:set PASSWORD=your_password`

- 使用 `heroku ps:scale=1 crawler` 啟動

- [詳細教學](https://djangogirlstaipei.herokuapp.com/tutorials/deploy-to-heroku/?os=windows)

## 實作細節

- [crawler](https://hackmd.io/ISiaMVvvR7uwmNgQODKQrQ)

### TODO

- 單一入口改用新版登入介面進入
  - 現在是用舊版
  - 要處理 `g-recaptcha` 驗證問題
- 增加 selenium 相關的爬蟲效能
- 寄信功能可以附圖片等
  - 現在只能純文字
- 下載 pdf 檔案
- 修正下載檔名有時會錯誤
- 將爬蟲資料存進本地，以方便建構 gui 
- gui 讓課程列表、attendees 全部變成參數
  - 根據使用者課表，客制化自己的課表

## 2.0

### gui.py

- 新增 gui 介面
- 與 google calendar api 連結
- 目前都是能夠使用的內容為寫死的，故仍需再改

## 1.3

### cralwer.py

- 修正 `get_ctopics` 格式錯誤
  - 移除 `homework` 參數
  - 移除 homework information 的部分，並將其移至其他函式
- 新增 `get_homework` 爬取今日作業項目

## 1.2

### goapi.py

- 修正時間為 `23:59` 導致 `start_time` 也為 `23:59` 的錯誤

## 1.1

### goapi.py

- 修正時間格式錯誤
- `date_adjust` 新增 `end` 參數，來控制回傳的時間
  - 方便日後新增參數

## 1.0

### 重點改動

- **可以放在 heroku 上面自動執行**
- 把今日課表效能加強，並可以在 heroku 上面執行
  - 原本用 selenium，現在改成 requests
- 把 detail.md 刪掉，改成用 hackmd
	- 不需要兩邊改來改去

### crawler.py

- 新增 `one_url` 跟 `old_login_url` 來登入單一入口
  - `__payload` 新增 `acc`, `pass` 當成帳號與密碼參數
- `daily_curriculum` 改成用 requests 實作

## 0.9

### 重點改動

- 讓 pdf 檔案日期能正常加到行事曆上

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
