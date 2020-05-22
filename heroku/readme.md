# Heroku version template

- 僅為參考樣板
- 版本為 ccu crawler 1.3

## 使用說明

- [詳細教學](https://djangogirlstaipei.herokuapp.com/tutorials/deploy-to-heroku/?os=windows)

### 下載 heroku 工具

- 需先下載 heroku cli 以方便後續程序
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

### heroku 設定

1. 輸入 `heroku login` 登入
2. 安裝 heroku 用的套件
    - `pip install dj-database-url gunicorn dj-static`
3. 將用到 package 寫到 `requirements.txt`
4. 寫個 `Procfile` 指定要執行的指令
  - ex: `crawler: python main.py`
  - crawler: heroku 上的 dyno 可以辨識的名稱
    - 在 heroku 上呼叫 `crawler` 則執行 `python main.py`
    - 可以理解成要執行的**指令名稱**
5. 根據使用者需求，寫 `.gitignore`

### 部署到 heroku

部署前須完成事項
- 註冊 heroku
- 安裝 heroku Toolbelt
- 寫好設定檔
    - Procfile, requirements ...

#### 建立 git repository

```
git init
git add .
git commit -m "your message"
```
#### 建立 app

```
heroku create ccu_crawler
heroku git:remote -a ccu_crawler
heroku config:set USERNAME=your_id
heroku config:set PASSWORD=your_password
git push heroku master
```

### 查看程式狀態

- `heroku logs`: 查看近期 log
- `heroku logs -n 500`: 查看近 500 行 log
- `heroku logs --tail`: 動態追蹤
