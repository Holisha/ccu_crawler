from __future__ import print_function
from getpass import getpass
import argparse

from crawler import Crawler
from goapi import GoogleApi
from getPDF import PDF



# USERNAME = input('username:')
TOKEN = 'logintoken'
LOGIN_URL = 'https://ecourse2.ccu.edu.tw/login/index.php'
URL =  'https://ecourse2.ccu.edu.tw/my/'
TEST_URL = []
MAIL = 'fan89511@gmail.com'


def main():
    USERNAME = '406410093'
    PASSWORD = getpass()
    # TEST_URL = ['https://ecourse2.ccu.edu.tw/course/view.php?id=6054']      # CO
    # TEST_URL = ['https://ecourse2.ccu.edu.tw/course/view.php?id=6050']      # OS
    # TEST_URL.append('https://ecourse2.ccu.edu.tw/course/view.php?id=6068')  # CV
    
    # get in progress course info
    course = Crawler(USERNAME, PASSWORD)
    course.login(URL)
    # course.get_progress()
    course.daily_curriculum()
    # print(course.course_data)
    # course.get_course(TEST_URL)


    # load the noticed info to google calendar
    # cal = GoogleApi('calendar', 'v3')
    # mail = GoogleApi('gmail', 'v1')
    
    # for event in course.event:
        # for idx in range(len(course.event[event])):
            # print(str(course.event[event][idx]))
            # cal.add_event(event+'0'+str(idx+1), str(course.event[event][idx]))
    
    # print(course.course_data)
    print(course.curriculum)
    # mail.mail_create(MAIL, MAIL, '今日公告', course.curriculum)
    # cal.show_event()

if __name__ == '__main__':
    main()