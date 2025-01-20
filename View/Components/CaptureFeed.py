from PyQt6.QtWidgets import ( 
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QMessageBox,
    QSizePolicy
)

from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt

from Model.ImageConsumer import ImageConsumer
from Model.ImageProducer import ImageProducer
from Model.CaptureConfig import CaptureConfig
from Utils.ReportGenerator import ReportGenerator


from View.Components.Stopwatch import Stopwatch

import queue

class CaptureFeed(QWidget):
    def __init__(self, navigation_handler, capture_config: CaptureConfig, logger) -> None:
        super().__init__()
        self.navigation_handler = navigation_handler
        self.config = capture_config
        self.logger = logger
        
        self.stopwatch = Stopwatch()
        
        self.report_facade = ReportGenerator(self.config)
        
        
        self.logger.initialize()
        
        layout = QHBoxLayout()
        buttons = QHBoxLayout()
        inputs = QVBoxLayout()
                
        self.video_feed = QLabel()
        
        self.start_trial_button = QPushButton("Start Trial")
        self.start_trial_button.setFixedSize(100, 50)
        self.start_trial_button.clicked.connect(self.start_trial)
        
        self.end_trial_button = QPushButton("End trial")
        self.end_trial_button.setFixedSize(100, 50)
        self.end_trial_button.clicked.connect(self.end_trial)
        self.end_trial_button.setEnabled(False)
        
        exit_button = QPushButton("Exit")
        exit_button.setFixedSize(100, 50)
        exit_button.clicked.connect(self.exit)
        
        condition_label = QLabel("Condition")
        condition_label.setFont(QFont('Arial font', 10))
        self.condition_input = QLineEdit(parent=self)
        
        buttons.addWidget(self.start_trial_button)
        buttons.addWidget(self.end_trial_button)
        buttons.addWidget(exit_button)
        buttons.setSpacing(10)
        
        inputs.addWidget(self.stopwatch, alignment=Qt.AlignmentFlag.AlignCenter)    
        inputs.addWidget(condition_label, alignment=Qt.AlignmentFlag.AlignCenter)
        inputs.addWidget(self.condition_input, alignment=Qt.AlignmentFlag.AlignCenter) 
        
        inputs.addLayout(buttons)
        inputs.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.video_feed, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(inputs)
    
        self.setLayout(layout)
        
        initial_queue = queue.Queue(maxsize=5)
        self.producer = ImageProducer(config=capture_config, queue_reference=initial_queue)
        self.consumer = ImageConsumer(config=capture_config, queue_reference=initial_queue, report_facade=self.report_facade)
        
        self.consumer.image_update_signal.connect(self.update_video)
        
    def update_video(self, frame):
        self.video_feed.setPixmap(QPixmap.fromImage(frame))
    
    def start_streaming(self):
        self.producer.start_video_capture()
        self.consumer.start_video_stream()
                
    def start_trial(self):
        self.logger.log_button_pressed("Start Trial")
        condition = self.condition_input.text()
        if not condition:
            QMessageBox.critical(self, "Invalid configuration", "Condition cannot be empty")
            self.logger.log_failure("Tried to start trial without condition")
            return
        
        self.config.set_condition(condition)
        self.condition_input.setEnabled(False)
        self.start_trial_button.setEnabled(False)
        self.end_trial_button.setEnabled(True)
        
        self.consumer.end_video_stream()
        self.producer.stop_video_capture()
        
        new_queue = queue.Queue(maxsize=5)
        self.consumer.queue = new_queue
        self.producer.queue = new_queue
        
        self.stopwatch.start()
        self.consumer.start_video_analysis()
        self.producer.start_video_capture()
        
    def end_trial(self):
        self.logger.log_button_pressed("End Trial")
        self.stopwatch.stop()
        trial_duration = self.stopwatch.get_current_time()
        self.stopwatch.reset()
        self.consumer.end_video_analysis()
        self.producer.stop_video_capture()
        
        self.condition_input.setEnabled(True)
        self.start_trial_button.setEnabled(True)
        self.end_trial_button.setEnabled(False)
        
        self.report_facade.generate_summary_report(trial_duration)
        
        new_queue = queue.Queue(maxsize=5)
        self.consumer.queue = new_queue
        self.producer.queue = new_queue
        
        self.producer.start_video_capture()
        self.consumer.start_video_stream()
        
    def exit(self):
        self.consumer.shutdown()
        self.producer.shutdown()
        self.navigation_handler("configuration")