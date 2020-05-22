from PyQt5.QtCore import Qt, QDate, QTime, QDateTime
from PyQt5.QtWidgets import (QMainWindow, QCalendarWidget, QApplication, QWidget, QLabel, QComboBox, QDateTimeEdit, QPushButton, QLineEdit,
                            QVBoxLayout, QHBoxLayout, QGridLayout,  QGroupBox,
                            QSizePolicy, QStyleFactory)

from goapi import GoogleApi

# TODO: add course list, attendees blocks
class EventController(QWidget):
    def __init__(self, parent=None, default_style='Fusion'):
        super(EventController, self).__init__(parent)

        # main window attribute
        self.setGeometry(300, 100, 800, 800)
        self.setWindowTitle('Event controller')
        QApplication.setStyle(QStyleFactory.create(default_style))

        # needed information
        self.course_list = []
        self.event_list = []

        # call google api
        self.google_cal = GoogleApi('calendar', 'v3')
        self.attendee = []

        # create groups to control widgets position
        self.create_course_group()

        # set style
        style_layout = QHBoxLayout()
        style_label = QLabel('Style:')
        # QLabel.setBuddy

        style_combo = QComboBox()
        style_combo.addItems(QStyleFactory.keys())
        style_combo.activated[str].connect(self.change_style)

        # set style combo box index
        style_index = QStyleFactory.keys()
        style_index = style_index.index(default_style)
        style_combo.setCurrentIndex(style_index)

        style_layout.addWidget(style_label)
        style_layout.addWidget(style_combo)
        style_layout.addStretch(1)

        # set submit button
        submit_layout = QHBoxLayout()
        
        submit_btn = QPushButton('Submit')
        submit_btn.clicked.connect(self.submit_event)

        clean_btn = QPushButton('Clean')
        clean_btn.clicked.connect(self.clean_all)

        submit_layout.addStretch(1)
        submit_layout.addWidget(submit_btn)
        submit_layout.addWidget(clean_btn)

        # set main layout
        main_layout = QGridLayout()
        main_layout.addLayout(style_layout, 0, 0, 1, 2)
        main_layout.addWidget(self.course_group, 1, 0)
        main_layout.addLayout(submit_layout, 2, 0, 1, 2)

        self.setLayout(main_layout)

    def change_style(self, style_name):
        QApplication.setStyle(QStyleFactory.create(style_name))
        QApplication.setPalette(QApplication.style().standardPalette())

    def submit_event(self):
        course_name = self.course_combo.currentText()
        event_type = self.event_combo.currentText()
        desc = self.desc_line_edit.text()

        event_info = f'{course_name}-{event_type}{desc}'
        print(event_info, end=' ')

        start_time = self.start_datetime.dateTime().toString(Qt.ISODate)[:-3]
        end_time = self.end_datetime.dateTime().toString(Qt.ISODate)[:-3]

        print(f'{start_time} -- {end_time}')
        self.google_cal.add_event(event_info, start_time=start_time, event_time=end_time, attendees=self.attendee)

    def clean_all(self):
        """
        reset all parameter
        """
        # reset course_group
        self.course_combo.setCurrentIndex(0)
        self.event_combo.setCurrentIndex(0)
        
        # reset desc line edit
        self.desc_line_edit.clear()

        # reset start
        self.start_datetime.setDateTime(QDateTime.currentDateTime())

        # reset terminal time
        self.end_datetime.setDate(QDate.currentDate())
        self.end_datetime.setTime(QTime(23, 59))
        

    def create_course_group(self):
        self.course_group = QGroupBox('course group')

        self.course_list.extend(['ML', 'DL', 'CD'])
        
        self.event_list.extend(['HW', 'assignment', 'exam', 'lab', 'midterm', 'final'])

        # course name block
        course_layout = QVBoxLayout()
        course_label = QLabel('Course name')

        self.course_combo = QComboBox()
        self.course_combo.addItems(self.course_list)

        # course_layout.addStretch(1)
        course_layout.addWidget(course_label)
        course_layout.addWidget(self.course_combo)
        course_layout.addStretch(1)

        # event type block
        event_layout = QVBoxLayout()
        event_label = QLabel('Event type')

        self.event_combo = QComboBox()
        self.event_combo.addItems(self.event_list)

        # event_layout.addStretch(1)
        event_layout.addWidget(event_label)
        event_layout.addWidget(self.event_combo)
        event_layout.addStretch(1)

        # event description
        desc_layout = QVBoxLayout()
        desc_label = QLabel('Description')

        self.desc_line_edit = QLineEdit()
        self.desc_line_edit.setMaxLength(5)

        # desc_layout.addStretch(1)
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_line_edit)
        desc_layout.addStretch(1)

        # start datetime block
        start_layout = QVBoxLayout()
        start_label = QLabel('Start time')

        self.start_datetime = QDateTimeEdit()
        self.start_datetime.setCalendarPopup(True)
        self.start_datetime.setMinimumDateTime(QDateTime.currentDateTime())
        self.start_datetime.dateChanged.connect(self.datetime_synch)

        # start_layout.addStretch(1)
        start_layout.addWidget(start_label)
        start_layout.addWidget(self.start_datetime)
        start_layout.addStretch(1)

        # end datetime block
        end_layout = QVBoxLayout()
        end_label = QLabel('Terminate time')

        self.end_datetime = QDateTimeEdit()
        self.end_datetime.setCalendarPopup(True)
        self.end_datetime.setMinimumDate(QDate.currentDate())
        self.end_datetime.setTime(QTime(23, 59))

        # end_layout.addStretch(1)
        end_layout.addWidget(end_label)
        end_layout.addWidget(self.end_datetime)
        end_layout.addStretch(1)

        # layout box
        layout = QHBoxLayout()
        layout.addLayout(course_layout)
        layout.addLayout(event_layout)
        layout.addLayout(desc_layout)
        layout.addLayout(start_layout)
        layout.addLayout(end_layout)
        layout.addStretch(1)
        
        self.course_group.setLayout(layout)

    # change end datetime binding to start_datetime
    def datetime_synch(self, date):

        self.end_datetime.setDate(date)
        self.end_datetime.setTime(
            QTime(23, 59)
        )
            

if __name__ == '__main__':
    app = QApplication([])

    controller = EventController()
    controller.show()
    app.exec_()
