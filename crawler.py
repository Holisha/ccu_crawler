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
from datetime import datetime
from pytz import timezone
from time import sleep
import getPDF


TOKEN = 'logintoken'
LOGIN_URL = 'https://ecourse2.ccu.edu.tw/login/index.php'
URL =  'https://ecourse2.ccu.edu.tw/my/'

# TODO: pdf crawler, add homework to daily curriculum
class Crawler():
    event = {}      # store events
    __payload = {}  # store username, password, and session key

    # to deal with special case
    key_word = ['Homework Assignment', '作業', '作業投影片', 'Homework']

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
    one_login_url = r"https://cas.ccu.edu.tw/login?service=https%3A%2F%2Fportal.ccu.edu.tw%2Flogin_check_cas.php"
    old_login_url = r"https://portal.ccu.edu.tw/login_check.php"
    one_url = r'https://portal.ccu.edu.tw/sso_index.php'

    def __init__(self, username, password, download=False):
        # print(f'username:{username}')
        self.__payload['username'] = username
        self.__payload['password'] = password

        # download option
        self.download = download

    def setup(self, url, login_url=login_url, daily=True, progress=False, processing=False, path=os.getcwd(), timeout=30):
        self.login(url, login_url)
        self.get_progress()

        if daily:
            self.daily_curriculum(progress=progress)

        if self.download and processing:
            print('developing')
            os._exit(0)
        elif self.download:
            for idx in range(self.course_data.shape[0]):
                target_dir = os.path.join(path, self.course_data.iloc[idx, 0])

                self.download_file(
                    self.__payload['username'],
                    self.__payload['password'],
                    self.course_data.iloc[idx, 1],
                    path=target_dir,
                    timeout=timeout
                )

    def login(self, url, login_url=login_url, one=False):
        # login with post method
        # cookies will change when request another page
        session_requests = requests.session()
        
        # one can't get login url
        if one:
            self.__payload.pop('logintoken')

        else:
            self.headers['Referer'] = login_url
            self.request = session_requests.get(login_url)
            tree = html.fromstring(self.request.text)
            token = list(set(tree.xpath('//input[@name="'+ TOKEN +'"]/@value')))
            if token:
                self.__payload['logintoken'] = token
        
        self.request = session_requests.post(login_url, data=self.__payload, headers=self.headers)
        # print(f'post: {self.request.url}')
        self.request = session_requests.get(url, headers=dict(Referer = login_url))
        # print(f'get: {self.request.url}')

        self.test_connection(self.request)

    def get_progress(self):
        """
        get the courses of this semester
        """
        course_name = []
        course_href = []
        course_info = self.soup.find_all(href=re.compile(r'^.*/course/.*id=[89]\d{3}$'))
        for course in course_info:
            if not course.string:
                continue
            # remove course id in course name
            tmp_name = re.sub(r'\(\d{7}_\d{2}\)', '', course.string)
            # print(tmp_name, course['href'], sep='\n')
            course_name.append(tmp_name)
            course_href.append(course['href'])

        self.get_course(course_href)
        # if require course info

        self.course_data = pd.DataFrame({'course name': course_name, 'course href': course_href})

    # print course_name only, just for debug
    def print_course(self, soup):
        for course_name in soup.find_all(href=re.compile(r'^.*/course/.*id=[89]\d{3}$')):
            if course_name:
                print(course_name.string + ':' + course_name['href'])

    # return events
    def get_course(self, url_list):
        for url in url_list:
            tmp = []
            desc = []
            date = []

            self.login(url, self.headers['Referer'])
            course_soup = bs(self.request.text, 'lxml')

            # initial dictionary value to list data structure
            title = course_soup.find('a', href=url)['title']
            title = re.sub(r'\(\d{7}_\d{2}\)', '', title)   # remove course id
            # self.event[title] = list()

            # get announcement and forum
            self.get_ctopics(title, soup=course_soup)

            img = course_soup.find_all('img', src=re.compile(r'https://ecourse2\.ccu\.edu\.tw/theme/image\.php/lambda/assign/\d{10}/icon'))
            if img:
                for icon in img:
                    if icon.has_attr('title'):
                        continue
                    # print(f'{icon}\n{icon.find_parent("a")}')
                    tmp.append(icon.find_parent('a')['href'])

                    # get homework title
                    for text in icon.next_sibling.strings:
                        desc.append(text)
                        break
                    # print(title, icon.find_parent('a')['href'], desc, sep='\n')

                # get home work time
                # return a list
                date = self.get_time(tmp)

            # To deal with pdf file
            elif self.check_pdf(course_soup):

                pdf_soup = self.key_soup.find_all('a', href=re.compile(r'^.*/resource/.*id=\d+$'))
                for pdf_href in pdf_soup:

                    tmp.append(pdf_href['href'])
                    self.login(pdf_href['href'], self.headers['Referer'])
                    # print(self.request.status_code)

                    # get homework title
                    for text in pdf_href.find('span').strings:
                        desc.append(text)
                        break

                    # To deal with pdf link
                    file_info = self.soup.find('div', class_='resourceworkaround')
                    if file_info:
                        self.login(file_info.find('a')['href'], login_url=self.headers['Referer'])

                    # get pdf info
                    reader = getPDF.PDF()
                    reader.url_pdf(self.request.content)
                    
                    # return date and time in str
                    date.append(reader.find_deadline())
                    
                # self.event[title].extend(date_list)

            else:
                print(f'There\'s no homework in {title} now')
                continue
                # os._exit(0)
            
            for idx, name in enumerate(desc):
                self.event[f'{title}-{name}'] = date[idx]


        return self.event

    def get_ctopics(self, title, url=None, soup=None, homework=True):
        # TODO: deal with announcement and forum

        if not soup and url:
            self.login(url, self.headers['Referer'])
            soup = bs(self.request.text, 'lxml')
        
        # add announcement and forum
        announcement = []
        for announce in soup.select('div.format_topcoll_tooltip a[href]'):
            tmp= []
            for content in announce.stripped_strings:
                tmp.append(content)
                
            announcement.append('->' + ', '.join(tmp))

        if announcement:
            self.announcement = title + '\n' + '\n'.join(announcement) + '\n'
        else:
            self.announcement = ''
        
        if not homework:
            return self.announcement
        
        # add homework info
        self.announcement += '\n------Homework------\n\n'
        for homework_title, deadline in self.event.items():
            
            # if no homework then skip, add to the annoucement, otherwise
            if deadline.endswith('No deadline currently'):
                continue
            elif title in homework_title and deadline >= str(datetime.today()):
                self.announcement += homework_title + ': ' + deadline + '\n'

        return self.announcement

    # check wehter pdf file exist in keyword list section
    def check_pdf(self, soup):
        for key in self.key_word:
            self.key_soup = soup.find('li', attrs={'aria-label' : key})
            if self.key_soup:
                # print(f'key word is:{key}')
                break

        if self.key_soup and \
            self.key_soup.find('img', src=re.compile(r'https://ecourse2\.ccu\.edu\.tw/theme/image\.php/lambda/core/\d{10}/f/pdf\-24')) and\
            not self.key_soup.has_attr('title'):

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

                date_list.append(date)
            else:
                date_list.append('No deadline currently')
        
        return date_list

    def test_connection(self, request):
        # print(f'test: {request.url}\n')
        self.soup = bs(request.text, 'lxml')

        if request.status_code != requests.codes.ok:    # 200
            print('fail connection')
            os._exit(0)
        else:
            # print('connection succeed')
            faliure_tag = self.soup.find_all(id='notice')
            # faliure_tag = self.soup.find_all(id='loginerrormessage')
            if faliure_tag:
                for tag in faliure_tag:
                    print(tag.string)
                print('login fail')
                os._exit(0)

    def daily_curriculum(self, progress=False, old=True):

        if progress:
            self.get_progress()

        # check is weekdays or weekends
        today = datetime.now(tz=timezone('Asia/Taipei')).isoweekday()
        if today > 5:
            self.curriculum = 'Today is weekends'
            return
        
        if old:
        # old login format
            self.__payload['acc'] = self.__payload['username']
            self.__payload['pass'] = self.__payload['password']
            self.login(self.one_url, self.old_login_url, old)


        # get today's schedule
        tmp_list = []
        schedule = []
        tmp = self.soup.select_one(f'div #w_DailyCourse #daily_course_content_{today} table')
        # print(today)
        # print(tmp)
        for idx, string in enumerate(tmp.find_all('td'), 1):
            tmp_list.append(string.string)

            if idx % 3 == 0:
                schedule.append(' '.join(tmp_list))
                tmp_list = []
        
        # remove repeated course name
        previous_string = schedule[0]
        idx = 1
        for string in schedule[1:]:
            if previous_string[12:] == string[12:]:
                schedule[idx] = string.replace(string[:6], previous_string[:6])

                # pop repeated one
                schedule.pop(idx - 1)
            else:
                idx += 1
            
            previous_string = string

        # get daily curriculum schedule
        self.curriculum = """今日課表\n"""
        self.curriculum += '\n'.join(schedule)
        
         # get course name
        self.curriculum += '\n\n----Announcement----\n\n'
        today_course = []
        for tmp in schedule:
            today_course.append(
                tmp.split(' ')[1]
            )
        # compare course
        for idx, course_name in enumerate(self.course_data.iloc[:, 0]):
            if course_name in today_course:
                self.curriculum += self.get_ctopics(course_name, self.course_data.iloc[idx, 1])

    # craw by selenium, performance is not good as excepted
    def daily_curriculum_selenium(self, progress=False):
        # TODO: performance enhance

        if progress:
            self.get_progress()

        # check is weekdays or weekends
        if datetime.now(tz=timezone('Asia/Taipei')).weekday() >= 5:
            self.curriculum = 'Today is weekends'
            return

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
        user.clear
        user.send_keys(self.__payload['username'])
        pwd = driver.find_element_by_name('password')
        pwd.clear
        pwd.send_keys(self.__payload['password'])
        pwd.send_keys(Keys.RETURN)
        driver.implicitly_wait(30)

        # get curriculum schedule
        string = driver.find_element_by_id('w_DailyCourse').text
        driver.implicitly_wait(30)
        driver.quit()
        
        # get target information
        string = string.split('\n')
        # pop date list
        string.pop(1)

        previous = string[2]   # start from the first class
        continue_flag = False
        idx = 3
        for cur in string[3:]:
            if cur[12:] == previous[12:]:
                # check whether repeated continuously
                if not continue_flag:
                    start_time = previous[:5]
                    continue_flag = True
                
                # pop repeated course
                string.pop(idx-1)

            else:
                if continue_flag:
                    string[idx-1] = previous.replace(previous[:5], start_time)
                    continue_flag = False
                
                idx += 1

            previous = cur
        # check the last course    
        if continue_flag:
            string[-1] = cur.replace(cur[:5], start_time)

        # get daily curriculum schedule
        self.curriculum = "\n".join(string)
        
        # get course name
        self.curriculum += '\n\n----Announcement----\n\n'
        today_course = []
        for tmp in string[2:]:
            today_course.append(
                tmp.split(' ')[1]
            )
        # compare course
        for idx, course_name in enumerate(self.course_data.iloc[:, 0]):
            if course_name in today_course:
                self.curriculum += self.get_ctopics(course_name, self.course_data.iloc[idx, 1])
    
    @staticmethod
    def download_file(username, password, url, path=os.getcwd(), timeout=30):

        # if directory isn't exists, then create a new one
        if not os.path.isdir(path):
            os.mkdir(path)

        options = webdriver.ChromeOptions()
        download_setting = {
            'download.default_directory': path
        }
        options.add_experimental_option('prefs', download_setting)
        # options.add_argument('headless')
        options.add_argument('window-size=1200x600')

        # by chrome
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        driver.implicitly_wait(30)

        # login data
        user = driver.find_element_by_name('username')
        user.clear
        user.send_keys(username)
        pwd = driver.find_element_by_name('password')
        pwd.clear
        pwd.send_keys(password)
        driver.implicitly_wait(30)

        pwd.send_keys(Keys.RETURN)
        driver.implicitly_wait(30)

        for link in driver.find_elements_by_css_selector('span.the_toggle.tc-medium'):
            # do not wait for already expanded div
            if link.get_attribute('aria-expanded') == 'false':
                link.click()
                driver.implicitly_wait(30)

        # click the icon by css selector
        rename = []
        for link in driver.find_elements_by_css_selector('div > a > img[src*="powerpoint"]'):

            # check wether the new one or not
            file_name = link.find_element_by_xpath('./following-sibling::span')
            if file_name:
                name = re.sub('[\\\/\*\?:\"<>| ]', '_', file_name.text)
                if name in os.listdir(path):
                    continue
                else:
                    name += '.pptx'
                    rename.append(name)
                    link.click()

            driver.implicitly_wait(30)
        
        # wait for the file
        download_wait(path, timeout)
        
        # rename
        rename_file(path, rename)

        driver.quit()
    
def download_wait(path, max_timeout=30):
    downloading = True
    seconds = 0

    while downloading and seconds < max_timeout:
        sleep(1)
        downloading = False

        for file_name in os.listdir(path):
            if file_name.endswith('.crdownload'):
                downloading = True
                
        seconds += 1

    return seconds

def rename_file(path, name_list):
    
    for idx, file_name in enumerate(os.listdir(path)):
        old_name = os.path.join(path, file_name)
        new_name = os.path.join(path, name_list[idx])
        os.rename(old_name, new_name)


if __name__ == '__main__':
    # USERNAME = input('username:')
    USERNAME = '406410093'
    PASSWORD = getpass()
    # TEST_URL = ['https://ecourse2.ccu.edu.tw/course/view.php?id=6054']
    # TEST_URL.append('https://ecourse2.ccu.edu.tw/course/view.php?id=6068')  # OS

    course = Crawler(USERNAME, PASSWORD)
    course.login(URL)

    course.get_progress()

    course.daily_curriculum()
    print(course.curriculum)

    # course.get_course(TEST_URL)
    # print(course.event)
    # course.print_course()
    # print(course.course_data)