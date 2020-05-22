from __future__ import print_function
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from pytz import timezone
import argparse
import os

from crawler import Crawler
from goapi import GoogleApi
from getPDF import PDF


# control scheduler
def schedule():
    scheduler = BlockingScheduler(timezone=timezone('Asia/Taipei'))
    # weekday need curriculum schedule, however, weekend don't need it
    scheduler.add_job(main, 'cron', day_of_week='mon-fri', hour=0, args=[True])
    scheduler.add_job(main, 'cron', day_of_week='sat-sun', hour=0, args=[False])

    scheduler.start()

# USERNAME = input('username:')
TOKEN = 'logintoken'
LOGIN_URL = 'https://ecourse2.ccu.edu.tw/login/index.php'
URL =  'https://ecourse2.ccu.edu.tw/my/'
TEST_URL = []
MAIL = 'fan89511@gmail.com'


def main(daily):
    print(f'\n<start the crawler at {datetime.now()}>\n')

    parser = argparse.ArgumentParser(description='ecourse 2 crawler controller')

    # download setting
    parser.add_argument('--download', action='store_true', default=False,
                        help='download file from ecourse 2 (default: false)')
    parser.add_argument('--timeout', type=int, default=600,
                        help='set the donwloading waiting time (default: 600)')
    parser.add_argument('--path', type=str, default=os.path.join(os.getcwd(), 'course'),
                        help='set the download path (default: cwd + course)')

    args = parser.parse_args()

    # environment variable for heroku
    USERNAME = os.environ['USERNAME']
    PASSWORD = os.environ['PASSWORD']

    course = Crawler(USERNAME, PASSWORD)
    course.setup(
                    URL,
                    path=args.path,
                    daily=daily,
                 )

    # load the noticed info to google api
    cal = GoogleApi('calendar', 'v3')

    if daily:
        mail = GoogleApi('gmail', 'v1')
        mail.mail_create(MAIL, MAIL, '今日公告', course.curriculum)
    
    # add attendee
    attendee = [
        {'email': 'fan89511@gmail.com'}
    ]

    for title, deadline in course.event.items():
        if deadline.endswith('No deadline currently'):
            continue
        # event name, event time, attendees
        cal.add_event(title, deadline, attendees=attendee)
    
    # cal.show_event()

    print(f'\n<end of crawler at {datetime.now()}>\n')

if __name__ == '__main__':
    main(False)
    schedule()