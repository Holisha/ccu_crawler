from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtWidgets import (QMainWindow, QCalendarWidget, QApplication, QWidget, QLabel, QComboBox, QDateTimeEdit,
                            QVBoxLayout, QHBoxLayout, QGridLayout,  QGroupBox,
                            QSizePolicy, QStyleFactory)

class EventController(QWidget):
    def __init__(self, parent=None):
        super(EventController, self).__init__(parent)

        # main window attribute
        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Event controller')

        # needed information
        self.course_list = []
        self.event_list = []

        # create groups
        self.create_course_group()

        # set style
        style_layout = QHBoxLayout()
        style_label = QLabel('Style:')
        # QLabel.setBuddy

        style_combo = QComboBox()
        style_combo.addItems(QStyleFactory.keys())
        style_combo.activated[str].connect(self.change_style)

        style_layout.addWidget(style_label)
        style_layout.addWidget(style_combo)
        style_layout.addStretch(1)

        # set main layout
        main_layout = QGridLayout()
        main_layout.addLayout(style_layout, 0, 0, 1, 2)
        main_layout.addWidget(self.course_group, 1, 0)

        self.setLayout(main_layout)

    def change_style(self, style_name):
        QApplication.setStyle(QStyleFactory.create(style_name))
        QApplication.setPalette(QApplication.style().standardPalette())

    def create_course_group(self):
        self.course_group = QGroupBox('course group')

        self.course_list.extend(['ML', 'DL'])
        
        self.event_list.extend(['midterm', 'assignment', 'exam', 'lab'])

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

        # start datetime block
        start_layout = QVBoxLayout()
        start_label = QLabel('Start time')

        self.start_datetime = QDateTimeEdit()
        self.start_datetime.setCalendarPopup(True)
        self.start_datetime.setMinimumDate(QDate.currentDate())
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

        # end_layout.addStretch(1)
        end_layout.addWidget(end_label)
        end_layout.addWidget(self.end_datetime)
        end_layout.addStretch(1)

        # layout box
        layout = QHBoxLayout()
        layout.addLayout(course_layout)
        layout.addLayout(event_layout)
        layout.addLayout(start_layout)
        layout.addLayout(end_layout)
        layout.addStretch(1)
        
        self.course_group.setLayout(layout)

    # change end datetime binding by start_datetime
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
