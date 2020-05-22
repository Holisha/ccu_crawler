from __future__ import print_function
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from base64 import urlsafe_b64encode, b32encode
import os
import pickle
import re
import sys
from datetime import datetime, date, timedelta


class GoogleApi():
    r"""
    call a class object to control goole api
    processing version: <calendar, v3>, <gmail, v1>

    calendar function has:
        add_event: create a new calendar event in particular calendar (default is primary calendar)
        show_event: show the 10 (or more) of upcoming events in particular calendar(defalut is primary calendar)
        check_repetitive: Avoid to add same event in calendar (called in add_event)
        date_adjust: make the 24:00 to 23:59 and day - 1
    
    gmail function:
        mail_create: create an email which contain text only
        mail_send: send created email(called in mail_create)
    """
    date_format = r'^\d{4}\D\d+\D\d+\D*\d+:\d{2}$'

    def __init__(self, api_name, api_version):
        self.location = api_name

        if self.location == 'calendar':
            # rewrite required, so it can't be read-only
            SCOPES = ['https://www.googleapis.com/auth/calendar']
        elif self.location == 'gmail':
            # need the access to send email
            SCOPES = ['https://www.googleapis.com/auth/gmail.send']

        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(os.path.join(self.location, api_name + '_token.pickle')):
            with open(os.path.join(self.location, api_name + '_token.pickle'), 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    os.path.join(self.location, 'credentials.json'), SCOPES
                )

                creds = flow.run_local_server(port=0)
                # creds = flow.run_console()
            # Save the credentials for the next run
            with open(os.path.join(self.location, api_name + '_token.pickle'), 'wb') as token:
                pickle.dump(creds, token)

        # self.service = build(api_name, api_version, http=creds.authorize(Http()))
        self.service = build(api_name, api_version, credentials=creds)

    def add_event(self, event_name, event_time, start_time=None ,ID='primary', UTC='+08:00', notice='all', attendees=None, check=True, from_today=True):
        # TODO: add information

        if self.location != 'calendar':
            print(f'ServiceError: You\'re calling {self.location}')
            return
        
        self.UTC = UTC  # Taiwan is +08:00

        if start_time is None:
            start_time = event_time

        # time format: yyyy/mm/dd HH:MM
        if not re.search(self.date_format, event_time) or not re.search(self.date_format, start_time):
            print('FormatError: recommend format is yyyy/mm/dd HH:MM')
            return
        
        # check whether the start time is later than event time or not
        if start_time > event_time:
            print('TimeError: start time is later than event time')
            return

        # 0: year, 1: month, 2: day, 3: hour, 4: minute
        time_list = re.split(r'\D', event_time)
        start_list = re.split(r'\D', start_time)

        # if deadline end in 00:00, modify the date and time of deadline to 23:59 and day - 1
        if re.match(r'0\d', time_list[3]):
            time_list = self.date_adjust(time_list)

            # modify start time if is same day as event time
            if start_time == event_time:
                start_list = self.date_adjust(start_list, end=False)
        # if start time = event time and which is at 23:59
        elif start_time == event_time:
            start_list[3] = '00'
            start_list[4] = '00'

        # check the time
        if from_today and event_time < str(datetime.today()):
            print(f'TimeExceeded: {event_name} {event_time}')
            return

        event = {
            'summary': f'{event_name}',
            'start': {
                'dateTime': f'{start_list[0]}-{start_list[1]}-{start_list[2]}T{start_list[3]}:{start_list[4]}:00{self.UTC}'
            },
            'end': {
                'dateTime': f'{time_list[0]}-{time_list[1]}-{time_list[2]}T{time_list[3]}:{time_list[4]}:00{self.UTC}'
            },
        }

        # add
        if attendees:
            event['attendees'] = attendees

        if check and self.check_repetitive(ID, event_name):
            return

        resp = self.service.events().insert(calendarId=ID,
                                            body=event, 
                                            sendUpdates=notice).execute()
        print(f'{event_name} event added')
        # print(resp['id'])

    def show_event(self, ID='primary', result=10, time_min=datetime.utcnow().isoformat()+'Z', single=True, order='startTime'):
        events_result = self.service.events().list(calendarId=ID, timeMin=time_min,
                                                    maxResults=10, singleEvents=single,
                                                    orderBy=order).execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))

            # change the time struct to normal format
            start = re.sub(r':\d+\+.*', '\0', start)
            end = re.sub(r':\d+\+.*', '\0', end)
            start = re.sub(r'T', ' ', start)
            end = re.sub(r'T', ' ', end)

            print(f'event: {event["summary"]}\nfrom:{start}\nto:  {end}\n{event["id"]}')

    def check_repetitive(self, ID, event_name):
        event_list = self.service.events().list(calendarId=ID, timeMin=datetime.utcnow().isoformat()+'z',
                                        singleEvents=True, orderBy='startTime').execute()
            
        for event in event_list['items']:
            if event['summary'] == event_name:
                print(f'EventExist: {event_name} was already in the calendar')
                return True

        return False

    @staticmethod
    def date_adjust(time_list, end=True):
        # input is a list, end is return end of the day
        # 0: year, 1: month, 2: day, 3: hour, 4: minute
        deadline = date(int(time_list[0]), int(time_list[1]), int(time_list[2])) - timedelta(days=1)
        tmp = re.split('-' ,deadline.isoformat())

        if end:
            tmp.append('23')
            tmp.append('59')
        else:
            tmp.append('00')
            tmp.append('00')

        return tmp

    def mail_create(self, sender, to, subject, msg_text, send=True):
        if self.location != 'gmail':
            print(f'ServiceError: You\'re calling {self.location}')
            return

        # message = MIMEText(msg_text)
        message = MIMEMultipart('mixed')
        message['From'] = sender
        message['To'] = to
        message['Subject'] = Header(subject, 'utf-8')

        message.attach(MIMEText(msg_text, 'plain', 'utf-8'))
        message = urlsafe_b64encode(message.as_bytes()).decode()

        if send:
            self.mail_send(message={'raw':message})
        else:
            return {'raw':urlsafe_b64encode(message.as_bytes()).decode()}

    def mail_send(self, message, user_id='me'):
        try:
            self.service.users().messages().send(
                userId=user_id, body=message).execute()
        except error.HTTPError as errors:
            print (f'An error occurred: {errors}')

if __name__ == '__main__':
    attendee = [
        {'email': 'fan89511@gmail.com'}
    ]
    calendar = GoogleApi('calendar', 'v3')
    # print(sys.argv[1])
    # calendar.add_event('test', sys.argv[1])
    # calendar.add_event('影像處理概論-midterm', '2020-05-13 17:30','2020-05-13 16:10', attendees=attendee)
    calendar.add_event('深度學習概論-HW4_Resnet', '2020-05-22 23:59', attendees=attendee)
    calendar.add_event('深度學習概論-Lab4_CNN', '2020-05-22 23:59', attendees=attendee)
    # calendar.add_event('編譯器設計-midterm', '2020-4-27 00:00')
    # calendar.add_event('time test 2', '2020-3-24 00:04') 
    # calendar.show_event()

    """ mail = GoogleApi('gmail', 'v1')
    MAIL = 'fan89511@gmail.com'
    mail.mail_create(MAIL, MAIL, 'test', 'testing')
 """
