import requests
import lxml
import re
import os
import time
import pandas as pd
from lxml import html
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from getpass import getpass
import getPDF


TOKEN = 'logintoken'
LOGIN_URL = 'https://ecourse2.ccu.edu.tw/login/index.php'
URL =  'https://ecourse2.ccu.edu.tw/my/'

class Crawler():
    event = {}      # store events
    __payload = {}  # store username, password, and session key

    # to deal with special case
    key_word = ['作業', '作業投影片']

    # ecourse 2 login page & header
    login_url = 'https://ecourse2.ccu.edu.tw/login/index.php'
    headers = {
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding' : 'gzip, deflate, br',
    'Accept-Language' : 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6,zh-CN;q=0.5',
    'Cache-Control' : 'max-age=0',
    'Connection' : 'keep-alive',
    'Content-Length' : '80',
    'Content-Type' : 'application/x-www-form-urlencoded',
    'Origin' : 'https://ecourse2.ccu.edu.tw/',
    'Referer' : 'https://ecourse2.ccu.edu.tw/',
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    }

    # CCU one login page
    one_login_url = "https://cas.ccu.edu.tw/login?service=https%3A%2F%2Fportal.ccu.edu.tw%2Flogin_check_cas.php"

    def __init__(self, username, password):
        print(f'username:{username}')
        self.__payload['username'] = username
        self.__payload['password'] = password

    def login(self, url, login_url=login_url):
        # login with post method
        # cookies will change when request another page
        self.headers['Referer'] = login_url
        session_requests = requests.session()
        self.request = session_requests.get(login_url)

        tree = html.fromstring(self.request.text)
        token = list(set(tree.xpath('//input[@name="'+ TOKEN +'"]/@value')))
        if token:
            self.__payload['logintoken'] = token
        self.request = session_requests.post(login_url, data = self.__payload, headers = self.headers)
        self.request = session_requests.get(url, headers= dict(Referer = url))

        self.test_connection(self.request)

    # return DataFrame
    def get_progress(self):
        self.soup = bs(self.request.text, 'lxml')
        course_name = []
        course_href = []
        course_info = self.soup.find_all(href=re.compile(r'^.*/course/.*id=[89]\d{3}$'))
        for course in course_info:
            if not course.string:
                continue
            course_name.append(course.string)
            course_href.append(course['href'])

        self.get_course(course_href)
        # if require course info

        for idx, name in enumerate(course_name):
            course_name[idx] = re.sub(r'\(\d{7}_\d{2}\)', '', name)

        self.course_data = pd.DataFrame({'course name': course_name, 'course href': course_href})

    # print course_name only, just for debug
    def print_course(self, soup):
        for course_name in soup.find_all(href=re.compile(r'^.*/course/.*id=[89]\d{3}$')):
            if course_name:
                print(course_name.string + ':' + course_name['href'])

    # return events
    def get_course(self, url_list):
        # print(len(url_list))
        # print(self.headers['Referer'])
        tmp = []
        for url in url_list:
            self.login(url, self.headers['Referer'])
            course_soup = bs(self.request.text, 'lxml')

            # initial dictionary value to list data structure
            title = course_soup.find('a', href=url)['title']
            self.event[title] = list()

            # get announcement and forum
            self.get_ctopics(title, course_soup)

            img = course_soup.find_all('img', src=re.compile(r'https://ecourse2\.ccu\.edu\.tw/theme/image\.php/lambda/assign/\d{10}/icon'))
            if img:
                for icon in img:
                    tmp.append(icon.find_parent('a')['href'])

                date = self.get_time(tmp)
                self.event[title] = date

            # To deal with pdf file
            elif self.check_pdf(course_soup):
                date_list = []

                pdf_soup = self.key_soup.find_all('a', href=re.compile(r'^.*/resource/.*id=\d+$'))
                for pdf_href in pdf_soup:
                    tmp.append(pdf_href['href'])
                    self.login(pdf_href['href'], self.headers['Referer'])
                    # print(self.request.status_code)

                    # To deal with pdf link
                    file_info = self.soup.find('div', class_='resourceworkaround')
                    if file_info:
                        # print(file_info.find('a')['href'])
                        self.login(file_info.find('a')['href'], login_url=self.headers['Referer'])

                    # get pdf info
                    reader = getPDF.PDF()
                    reader.url_pdf(self.request.content)
                    
                    # return date and time in str
                    date_list.append(reader.find_deadline())
                    
                    self.event[title] = date_list
            else:
                print(f'There\'s no homework in {title} now')
                # os._exit(0)

        # tmp list
        # print(*tmp, sep='\n')
        
        return self.event

    def get_ctopics(self, title, soup):
        # TODO: deal with announcement and forum
        
        announcement = []
        for tmp in soup.select('div.format_topcoll_tooltip a[href]'):
            for i in tmp.stripped_strings:
                announcement.append(i)

        # self.announcement = title + '\n' + '\n'.join(announcement)
        # print(self.announcement)
        # os._exit(0)
        return title + '\n' + '\n'.join(announcement)

    # check wehter pdf file exist in keyword list section
    def check_pdf(self, soup):
        for key in self.key_word:
            self.key_soup = soup.find('li', attrs={'aria-label' : key})
            if self.key_soup:
                # print(f'key word is:{key}')
                break

        if self.key_soup and self.key_soup.find('img', src=re.compile(r'https://ecourse2\.ccu\.edu\.tw/theme/image\.php/lambda/core/\d{10}/f/pdf\-24')):
            return True

        # print('pdf not found')
        return False
    
    # print the homework deadline
    def get_time(self, url_list):
        date_list = []

        for url in url_list:
            self.login(url, self.headers['Referer'])
            soup = bs(self.request.text, 'lxml')

            tmp = soup.find('th', string='作業期限')    # e course2 homework <th> string
            if tmp and tmp.find_next_sibling('td').string:
                date_str = re.findall(r'\d+' ,tmp.find_next_sibling('td').string)
                date = ' '.join(date_str)    # merge the list to str

                # turn str to time struct
                date = time.strptime(date, "%Y %m %d %H %M")
                date = time.strftime("%Y-%m-%d %H:%M", date)

                # print(f'{title}\n{date}')
                date_list.append(date)
        
        return date_list

    def test_connection(self, request):
        self.soup = bs(request.text, 'lxml')

        if not request.status_code == requests.codes.ok:    # 200
            print('fail connection')
            os._exit(0)
        else:
            # print('connection succeed')
            faliure_tag = self.soup.find_all(id='notice')
            if faliure_tag:
                for tag in faliure_tag:
                    print(tag.string)
                print('login fail')
                os._exit(0)

    # craw by selenium, performance is not good as excepted
    def daily_curriculum(self):
        # TODO: performance enhance
        # hide the browser
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1200x600')

        # open Chrome browser
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(self.one_login_url)
        driver.implicitly_wait(30)

        # login
        user = driver.find_element_by_name('username')
        user.send_keys(self.__payload['username'])
        pwd = driver.find_element_by_name('password')
        pwd.send_keys(self.__payload['password'])
        pwd.send_keys(Keys.RETURN)
        driver.implicitly_wait(30)

        # get curriculum schedule
        tmp = driver.find_element_by_id('w_DailyCourse').text
        driver.implicitly_wait(30)
        driver.quit()
        
        # get target information
        tmp = tmp.split('\n')
        # pop date list
        tmp.pop(1)

        """ previous = tmp[2]   # start from the first class
        for idx, string in enumerate(tmp[3:], 3):
            if string[12:] == previous[12:]:
                # union the time
                print(f'{string}\t {previous}')
                tmp[idx] = string.replace(string[0:4], previous[0:4])
                tmp.pop(idx-1)
            
            previous = string """
        
        # get daily curriculum schedule
        self.curriculum = "\n".join(tmp)
        
        try:
            # get course name
            today_course = []
            for string in tmp[2:]:
                today_course.append(
                    string.split(' ')[1]
                )
            for idx, course_name in enumerate(self.course_data.iloc[:, 0]):
                if course_name in today_course:
                    self.curriculum += self.get_ctopics(course_name, course_data.iloc[idx, 1])
        except:
            print('course data isn\'t exists!')
        


if __name__ == '__main__':
    # USERNAME = input('username:')
    USERNAME = '406410093'
    PASSWORD = getpass()
    TEST_URL = ['https://ecourse2.ccu.edu.tw/course/view.php?id=6054']
    # TEST_URL.append('https://ecourse2.ccu.edu.tw/course/view.php?id=6068')  # OS

    course = Crawler(USERNAME, PASSWORD)
    course.login(URL)

    # course.get_progress()

    course.get_course(TEST_URL)
    # print(course.event)
    # course.print_course()
    # print(course.course_data)