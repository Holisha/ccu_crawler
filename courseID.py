import requests
import lxml
from bs4 import BeautifulSoup as bs

URL = 'https://kiki.ccu.edu.tw/~ccmisp06/Course/'
ID = [4104, 4106]

website = requests.get(URL)
website.encoding = 'utf-8'
soup = bs(website.text, 'lxml')

for i in ID:
    tag = soup.find(href = str(i) + '.html')
    print(tag)

