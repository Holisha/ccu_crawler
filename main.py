from __future__ import print_function
from getpass import getpass
from datetime import datetime
import argparse
import os

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
    parser = argparse.ArgumentParser(description='ecourse 2 crawler controller')

    # google api setting
    # TODO

    # download setting
    parser.add_argument('--download', action='store_true', default=False,
                        help='download file from ecourse 2 (default: false)')
    parser.add_argument('--timeout', type=int, default=600,
                        help='set the donwloading waiting time (default: 600)')
    parser.add_argument('--path', type=str, default=os.path.join(os.getcwd(), 'course'),
                        help='set the download path (default: cwd + course)')
    parser.add_argument('--daily', action='store_true',  default=False,
                        help='get daily curriculum (default: false)')

    args = parser.parse_args()
    if not os.path.exists(args.path):
        print(f'path {args.path} not found')
        os._exit(0)

    # USERNAME = '406410093'
    USERNAME = input('username:')

    PASSWORD = getpass('password:')

    # os.path.join(os.getcwd(), 'course')

    print(f'\n<start the crawler at {datetime.now()}>\n')

    course = Crawler(USERNAME, PASSWORD, args.download)
    course.setup(
                    URL,
                    path=args.path,
                    daily=args.daily,
                    timeout=args.timeout
                 )

    # get in progress course info
    # course.login(URL)
    # course.get_progress()
    # course.daily_curriculum()

    # TEST_URL = ['https://ecourse2.ccu.edu.tw/course/view.php?id=6054']      # CO
    # TEST_URL = ['https://ecourse2.ccu.edu.tw/course/view.php?id=6050']      # OS
    # TEST_URL.append('https://ecourse2.ccu.edu.tw/course/view.php?id=6068')  # CV
    # course.get_course(TEST_URL)


    # load the noticed info to google api
    cal = GoogleApi('calendar', 'v3')

    if args.daily:
        mail = GoogleApi('gmail', 'v1')
        mail.mail_create(MAIL, MAIL, '今日公告', course.curriculum)

    
    # add attendee
    attendee = [
        {'email': 'fan89511@gmail.com'}
    ]

    for title, deadline in course.event.items():
        # print(f'{title}: {deadline}')
        if deadline.endswith('No deadline currently'):
            # print('skipped')
            continue

        # event name, event time, attendees
        cal.add_event(title, deadline, attendees=attendee)
    
    # cal.show_event()

    print(f'\n<end of crawler at {datetime.now()}>\n')

if __name__ == '__main__':
    main()