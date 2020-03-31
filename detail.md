# crawler
###### tags: `程式` `自學`

- 爬蟲練習
- 讀取關鍵字
    - 網頁、pdf、pptx
- 輸出到 google calendar
- 輸出到 gmail

## requirements

```python
conda install -c conda-forge <package>
requests
lxml
bs4
pdfminer3k
google-api-python-client
selenium
```

## TODO

- 抓課表效能改善
- 抓pdf 到指定資料夾
- 分開抓取公告、討論區內容
- 信件可以傳文字以外的內容

## 步驟

- [參考](https://ithelp.ithome.com.tw/articles/10193266)

1. 檢查網頁是否需要登入，且**登入頁面**和**需要的資訊**在哪
	- `F12 -> network`
	- from data、 request header
2. 決定登入的方式
	- post、cookie、selenium 等
3. 使用 requests 把網頁抓下來
4. beautiful soup 分析爬到的內容
5. 用 selenium 把今日課表抓下來
    - 效能尚未改善

- 如果遇到需要**重複登入或跳轉**的頁面，可以改用 selenium 爬

### 模擬登入

#### requests

- 有的網站會擋爬蟲，故 header 有些要自己寫
	- 騙網站是以使用者登入
	- 以 dictionary 儲存 header 跟 payload

- 有些網站把登入頁面寫在別的地方，會以 hidden 的方式把網站包起來
	- 有些還需要 token 來辨識使用找

- 查看**登入頁面**的網址
- 先把**登入頁面的網址**爬下來，並找辨識的 token
	- 注意只能發送一次 request，避免重新生成 token
- 選擇登入方式，並把需要的資訊一起送過去
	- post
- 爬需要的頁面
	- 要 Connection 要 keep-alive


```python
requests.session() 		# 只發送一次 request，避免認證用的 token 換掉
requests.get(str url) 	# 把內容爬下來
html.fromstring() 		# 以 string 解析 html 的內容，依照樣貌推測是從 document 或 fragment
requets.text			# 以文字方式顯示爬到的內容
requests.content		# 以二進位表示爬到的內容
```

- 找到 token 後用 `xpath` 把 token 抓出來

```python
# 以 list 儲存不重複的 token 
list(set(tree.xpath('//input[@name="'+ TOKEN +'"]/@value')))
# 以 post 發送給 server
requests.post(LOGIN_URL, data = payload, headers = headers)
```

#### selenium

```python
selenium.webdriver # 模擬瀏覽器的 object
```

- `ChromeOptions()` 來控制瀏覽器的參數
	- `add_argument()`: 新增參數
	- `add_experimental_argument()`: 新增給 **Chrome** 的參數
	- headless: 表示不顯示瀏覽器
		- win10 下有時會導致操作錯誤，或找不到元素
	- window-size: 視窗大小

- Chrome 下載控制:
	- **prefs** 中， 由 **download.default_directory** 來控制預設位置
	- profile.default_content_settings.popups: 0為禁止彈出視窗

- 定位:
```python
find_element()
find_element_by_id()
find_element_by_class_name()
find_element_by_name()
find_element_by_tag_name()
find_element_by_link_text()
find_element_by_partial_link_text()
find_element_by_css_selector()
find_element_by_xpath()
```
> 找複數 element 時，則 `find_elemnts()` ，以此類推
> 回傳值為 list of WebElement

- 操作:
	- `clear()`: 清空
	- `click()`: 模擬滑鼠點擊
	- `send_keys()`: 模擬鍵盤輸出
	- `submit()`: 提交表單

- WebElement:
```python
get_attribute()	# 取得屬性內容
parent	# 取得父節點
text	# 該節點內文字
```

### XPath

- A major element in the XSLT standard
- 可以用來偵測、尋找 XML document 中的 element 和 attributes

XPath 基本用法
| Expression | Description                     |
| ---------- | ------------------------------- |
| `nodename` | 選取所有叫 nodename 的節點      |
| `/`        | 從 root 節點選取                |
| `//`       | 從符合 selection 的節點開始選取 |
| `.`        | 選取當前節點                    |
| `..`       | 選取當前節點的 parent           |
| `@`        | 選取屬性                        |
| `|`        | or                             |

example:
| Path Expression | Result                               |
| --------------- | ------------------------------------ |
| bookstore       | 選取所有叫 bookstore 的節點          |
| //book          | 選取所有 book element                |
| /bookstore      | 選取 root 中的 bookstore             |
| bookstore/book  | 選取所有 bookstore 下的 book element |
| bookstore//book | 選取bookstore 下所有叫 book 的節點   |
| //@lang         | 選取所有叫 lang 的屬性               |
> node 跟 element 不一樣

- `[]`: 選取第 i 個符合的元素
	- last() 表最後一個
	- position() < 3: 選取前兩個元素
	- 不同語言的初值有所不同
	- IE: 從 0 開始
	- W3C: 從 1 開始

XPath Axes

- 用來表示與 current node 關係
- 常用於定位

| AxisName           | Result                                              |
| ------------------ | --------------------------------------------------- |
| ancestor           | 選取所有當前節點之前的 祖先節點                     |
| ancestor-or-self   | 同上，多包括當前節點                                |
| attribute          | 選取該節點所有屬性                                  |
| child              | 選取所有子節點                                      |
| descendant         | 選取當前節點之下的所有節點(含有 grandchildren node) |
| descendant-or-self | 同上，包含自己                                      |
| following          | 選取該文件中最接近當前節點的 tag                    |
| following-sibling  | 選取當前節點之後的同層節點                          |
| namespace          | 選取 namespace nodes                                |
| parent             | 選取父節點                                          |
| preceding          | 選取當前節點**之前**的所有節點                      |
| preceding-sibling  | 選取在當前節點之前的同層節點                        |
| self               | 選取當前節點                                        |
> 用 `::` 連接


### CSS selector

| Selector  | Description                  |
| --------- | ---------------------------- |
| .         | class                        |
| #         | id                           |
| *         | all elements                 |
| element   | 選取所有名稱符合的元素       |
| ,         | and                          |
| `space`   | 當前節點之下的 element       |
| >         | 指定 parent 與 children 關係 |
| ~         | 指定 ancestor 與 precedent   |
| `[]`      | 屬性                         |
| contain() | 包含指定文字的節點           |

`[]` 操作:
- `|=` : 指定 value 內**文字開頭**
- `^=`: 指定 value **開頭**
- `$=`: 指定 value 結尾
- `~=`: 指定 value 要包含的**字串**
- `*=`: 指定 value 內要有的**字元**



### 正規表示法

- 通常被稱為一個**模式(pattern)**，用來描述或符合一系列**有規則的字串**
- 執行效率未必快速，但方便 programmer 處理字串，且很多語言都有支援
	- ex: python, c#, Java, JavaScript, c++...
		- C++ 11 才開始支援

EX:
| RegExp                  | Example           | 備註         |
| ----------------------- | ----------------- | ------------ |
| `/^\d{4}-\d{2}-\d{2}$/` | 1999-05-11        | 西元生日格式 |
| `/^[A-Z]\d{9}$/`        | A123456789        | 身分證格式   |
| `/^.*@gmail\.com$/`     | example@gmail.com | gmail 格式   |


- 使用 re 模塊
	- `import re`

- `compile(pattern, flag=0)`
	- 把正規表示法是轉換為一般格式
- `escape(pattern)`
	- 把 pattern 以展開為正規表示法
- `findall(pattern, str, flag=0)`
	- 從 str 找到 pattern 內有的形式
	- 以 list 型態回傳符合的字串
- `match(pattern, str, flag=0)`
	- 與 findall 相似，**回傳值不同**
	- 匹配成功回傳 MatchObject，否則回傳 None
- `search(pattern, str, flag=0)`
	- 與 match 相似，但不是從開始處匹配
	- [match vs search](https://docs.python.org/2/library/re.html#search-vs-match)
- `split(pattern, str, maxsplit=0, flag=0)`
	- 功能同 strcat，不過可以用正規表達式
	- maxsplit 為最多可分割次數
- `sub(pat, repl ,str , count=0, flag=0)``
	- 把 str 內的 pattern 替換為 repl

```python=
pat = 'John'
repl = 'Tom'
text = 'my name is John.'
re.sub(pat, repl, text)
# result
'my name is Tom.'
```

#### 匹配對象

- 匹配的結果會儲存到 `group` 中
- 之後補

### 分析

- `xpath`, `bs4`

#### bs4

- 搭配正規表示法可以方便 programmer
	- 但可能會增加搜尋的時間複雜度，導致效能下降

- `find\_all(name, attrs, recursive, string, limit, \*\*kwargs)`
	- 可以直接搜尋標籤或屬性
	- 可以搭配 `re.compile`
	- **html5 的屬性要用 attrs 搜尋**
		- ex: data-*
	- 回傳一個 list of object
	- find 則回傳第一個找到的 object
- `find_parent` / `find_parents`
- `find_next_sibling` / `find_previous_sibling`

- `select`: CSS selector
	- `:nth-of-type(int num)`: 找第 num 個 
	- 以空格為間隔
	- `>`: 從左邊的標籤找符合右邊標籤的內容
		- `'head > title'`: 找 head 內有 title 標籤的 tags
	- `.`: by CSS class
	- `#`: by ID
	- 可以藉由 attribute 去找
		- [官網](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#css-selectors)
	- `select_one`: 回傳第一個找到的

- 其他
	- `insert`
		- `insert_before()` / `insert_after()`
	- `decompose`
	- `wrap`
	- `unwrap`
	- `replace_with`
	- `prettify()`

## PDF reader

- 以 requests.get.content 處理爬下來的內容
- 接者以 io.BytesIO 開啟 stream

- [PDF utf8](https://blog.csdn.net/qq_29750461/article/details/80011255)
- [PDFminer3k 圖解](https://blog.csdn.net/mingyuli/article/details/79737634)

## Google API Client

### Setup

1. 先申請 credentials，並將 credentials.json 存到同個目錄
	- 每個 api 都要各別申請
2. 使用 `build("api_name", "api_version")` 來選擇需要的服務
	- 後面參數接 api 名稱
3. 呼叫 build 好的服務內的 api
	- `featured()`: let the collections to be nested
4. 對該 api 發送需要的 request
	- 使用`.execute()` 來發送
	- 回傳值為 response
5. 對 response 進行操作，通常是回傳 JSON response
	- 官網的 Docs 都有寫 JSON 格式
	- - 可以把所有用到的都寫到同一行

ex:
- build service
- service 呼叫 calendar 內的 events()
- event 內的 insert，並用 execute()發送 request
```python
resp = self.service.events().insert(calendarId=ID, body=event).execute()
```

### init

- SCOPE 為檢查權限所需
	- calendar, v3: 因為有修改內容，故去掉 read-only
	- gmail, v1: 因為需要寄信，固權限需要加上 send
- creds 為 credentials，認證用
- UTC 預設為台灣時區(+8)
- constructor 先是進行權限檢查，當前路徑內沒有權限所需相關檔案便無法使用
	- 第一次使用時會換產生 token，以便下次使用

### add_event

- ID 預設為當前使用者，沒有則會跳出登入頁面，選擇使用者
- 確定輸入的格式符合需求後，將其分切，並存到 `dict` 中
	- 開始時間為當日00:00
- 沒用到 resp，但保留該變數以利之後使用

### show_event

- 主要參考 quickstart.py
- 預設為: 當前使用者，從現在的當地時間開始，最近10筆 event，各別輸出 event
- 呼叫 events 中的 list()
	- `timeMin`: 從 timeMin 這個時間開始搜尋 event
	- `singleEvent`: 是否要各別輸出 event，待查
- 用 re.sub 將輸出時間轉換成一般習慣的格式
	- yyyy-mm-dd HH:MM
	- 為當地時間(UTC)

### mail_create

- 使用 MIME 的格式
- 目前只能傳送文字
- python 3 之後 `urlsafe_b64encode` 需要先轉成 bytes， encode 完再 decode

### mail_send

- 寄信給指定對象

## 問題

- 資料銜接困難
	- 設計函式時沒有構想好回傳值
- JS渲染處理困難
	- requests 不好解決
	- selenium 太慢
- selenium
	- headless 找不到資料
	- 效能低下

## 參考

### 目標網站

- [ecourse 2](https://ecourse2.ccu.edu.tw/)

### 實作範例

#### 爬蟲

- [requests + bs4 模擬登入](https://ithelp.ithome.com.tw/articles/10193266)
- [Python 爬蟲學習筆記(一)](https://medium.com/@yanweiliu/python%E7%88%AC%E8%9F%B2%E5%AD%B8%E7%BF%92%E7%AD%86%E8%A8%98-%E4%B8%80-beautifulsoup-1ee011df8768)
- [給初學者的 Python 網頁爬蟲](http://blog.castman.net/%E6%95%99%E5%AD%B8/2016/12/22/python-data-science-tutorial-3.html)
- [爬蟲實戰2 完善版](https://ithelp.ithome.com.tw/articles/10207440)

- [selenium 定位](https://huilansame.github.io/huilansame.github.io/archivers/father-brother-locate)
- [selenium 下載設定](https://www.itread01.com/content/1547280554.html)
- [selenium 常用操作](https://www.itread01.com/articles/1476048648.html)

#### PDF reader

- [PDF utf8](https://blog.csdn.net/qq_29750461/article/details/80011255)
- [PDFminer3k 圖解](https://blog.csdn.net/mingyuli/article/details/79737634)

#### Google Calendar

- [Calendar Quick Start](https://developers.google.com/calendar/quickstart/python)
- [Calendar Create Event](https://developers.google.com/calendar/create-events)

### 技術細節

#### crawler

- [爬蟲簡介](https://elitedatascience.com/python-web-scraping-libraries)
- [lxml.html](https://lxml.de/lxmlhtml.html)
- [一般網站防爬蟲機制](https://ithelp.ithome.com.tw/articles/10191165)
- [查看隱藏 token 的方法](https://blog.csdn.net/qq_39708579/article/details/79353981)
- [XPath 基本用法](https://kknews.cc/zh-tw/code/5g2nb22.html)
- [XPath 教學](https://www.w3schools.com/xml/xpath_intro.asp)
- [CSS selector 教學](https://www.w3schools.com/cssref/default.asp)
- [Python re 模塊教學](http://blog.fantasy.codes/python/2013/07/02/py-re-module/)
- [python 正規表示法使用技巧](https://codertw.com/%E7%A8%8B%E5%BC%8F%E8%AA%9E%E8%A8%80/363649/)
- [Regular Expression](https://poychang.github.io/note-regular-expression/)
- [正規表示法字串比對](https://larry850806.github.io/2016/06/23/regex/)
- [python.org match vs search](https://docs.python.org/2/library/re.html#search-vs-match)
- [Beautiful Soup 抓取與解析網頁資料](https://blog.gtwang.org/programming/python-beautiful-soup-module-scrape-web-pages-tutorial/2/)
- [Beautiful Soup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [HTTP 狀態碼](https://developer.mozilla.org/zh-TW/docs/Web/HTTP/Status)
- [HTTP 狀態碼詳細版](https://blog.miniasp.com/post/2009/01/16/Web-developer-should-know-about-HTTP-Status-Code)
- [CSS 偽元素](https://www.oxxostudio.tw/articles/201706/pseudo-element-1.html)
- [selenium docs](https://selenium-python.readthedocs.io/index.html)

#### PDF reader

- `pdfminer3k`

#### Google Calendar

- [Google API](http://googleapis.github.io/google-api-python-client/docs/epy/googleapiclient.discovery-module.html#build)
- [Calendar API](https://developers.google.com/calendar/v3/reference/)
- [Google API client for Python Docs](https://github.com/googleapis/google-api-python-client/tree/master/docs)
- [API list & version](https://github.com/googleapis/google-api-python-client/blob/master/docs/dyn/index.md)
- [API Setup](https://github.com/googleapis/google-api-python-client/blob/master/docs/start.md)