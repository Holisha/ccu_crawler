# TODO: email sending function
from __future__ import print_function
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from base64 import urlsafe_b64encode
import urllib.error as error
import os
import pickle
import re
import sys
from datetime import datetime, date, timedelta


def date_adjust(time_list):
    # input is a list
    # 0: year, 1: month, 2: day, 3: hour, 4: minute
    deadline = date(int(time_list[0]), int(time_list[1]), int(time_list[2])) - timedelta(days=1)
    tmp = re.split('-' ,deadline.isoformat())
    tmp.append('23')
    tmp.append('59')

    return tmp

class GoogleApi(): # calendar api only, v3 is current version
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
                    os.path.join(self.location, 'credentials.json'), SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(os.path.join(self.location, api_name + '_token.pickle'), 'wb') as token:
                pickle.dump(creds, token)

        self.service = build(api_name, api_version, credentials=creds)

    def add_event(self, event_name, event_time, ID='primary', UTC='+08:00'):
        if self.location != 'calendar':
            print(f'error service! You\'re calling {self.location}')
            return
        
        self.UTC = UTC  # Taiwan is +08:00

        # event time format: yyyy/mm/dd HH:MM
        if not re.search(r'^\d{4}\D\d+\D\d+\D*\d+:\d{2}$', event_time):
            print('time format error\nyyyy/mm/dd HH:MM')
            return
        

        # 0: year, 1: month, 2: day, 3: hour, 4: minute
        time_list = re.split(r'\D', event_time)

        # if deadline end in 00:00, modify the date and time of deadline to 23:59 and day - 1
        if re.match(r'0\d', time_list[3]):
            time_list = date_adjust(time_list)

        event = {
            'summary': f'{event_name}',
            'start': {'dateTime': f'{time_list[0]}-{time_list[1]}-{time_list[2]}T00:00:00{self.UTC}'},
            'end': {'dateTime': f'{time_list[0]}-{time_list[1]}-{time_list[2]}T{time_list[3]}:{time_list[4]}:00{self.UTC}'},
        }

        resp = self.service.events().insert(calendarId=ID, body=event).execute()
        print(f'{event_name} event added')
        # print(event)

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

            print(f'event: {event["summary"]}\nfrom:{start}\nto:  {end}')

    def mail_create(self, sender, to, subject, msg_text, send=True):
        if self.location != 'gmail':
            print(f'error service! You\'re calling {self.location}')
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
    """ calendar = GoogleApi('calendar', 'v3')
    # print(sys.argv[1])
    # calendar.add_event('test', sys.argv[1])
    calendar.add_event('time test', '2020-2-24 00:04')
    calendar.show_event() """

    mail = GoogleApi('gmail', 'v1')
    MAIL = 'fan89511@gmail.com'
    mail.mail_create(MAIL, MAIL, 'test', 'testing')

