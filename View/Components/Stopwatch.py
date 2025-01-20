# Source: https://www.youtube.com/watch?v=UKs0xhxSOg0

from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout
)

from PyQt6.QtGui import (
    QFont
)

from PyQt6.QtCore import QTime, QTimer

class Stopwatch(QWidget):
    def __init__(self):
        super().__init__()
        self.time = QTime(0, 0, 0, 0)
        self.time_label = QLabel("00:00:00.00", self)
        self.time_label.setFont(QFont('Arial font', 35))
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.count)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.time_label)

        self.setLayout(vbox)
        
    def start(self):
        self.timer.start(10)

    def stop(self):
        self.timer.stop()
        
    def reset(self):
        self.timer.stop()
        self.time = QTime(0, 0, 0, 0)
        self.time_label.setText(self.get_current_time())
        
    def get_current_time(self):
        hours = self.time.hour()
        minutes = self.time.minute()
        seconds = self.time.second()
        milliseconds = self.time.msec() // 10
        return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:02}"

    def count(self):
        self.time = self.time.addMSecs(10)
        self.time_label.setText(self.get_current_time())