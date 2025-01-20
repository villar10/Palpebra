from PyQt6.QtWidgets import (
    QMainWindow,
    QStackedWidget
)

from View.Components.InitialPage import InitialPage
from View.Components.CaptureConfiguration import CaptureConfiguration
from View.Components.CaptureFeed import CaptureFeed
from Model.CaptureConfig import CaptureConfig
from Utils.Logger import Logger

class Container(QMainWindow):
    def __init__(self) -> None:
        super(Container, self).__init__()
        
        self.setWindowTitle("Data capturing GUI")

        self.initial_page = InitialPage(navigation_handler=self.navigate, exit_handler=self.exit_app)
        self.configuration_page = CaptureConfiguration(navigation_handler=self.navigate, configuration_handler=self.save_and_start)
        
        
        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)
        self.stacked.addWidget(self.initial_page)
        self.stacked.addWidget(self.configuration_page)
        
        # Initialize Container to the Initial page
        self.stacked.setCurrentWidget(self.initial_page)
        
        self.showMaximized() 
        self.show()
        
    def navigate(self, page: str):
        if(page == "configuration"):
            self.stacked.setCurrentWidget(self.configuration_page)
        elif(page == "video_feed"):
            self.stacked.setCurrentWidget(self.video_feed)
        elif(page == "initial"):
            self.stacked.setCurrentWidget(self.initial_page)
    
    def save_and_start(self, config: CaptureConfig):
        self.config = config
        self.start_capture()
        
    def start_capture(self):
        self.logger = Logger(self.config.report_directory, self.config.participant_id)
        self.video_feed = CaptureFeed(navigation_handler=self.navigate, capture_config=self.config, logger=self.logger)
        self.stacked.addWidget(self.video_feed)
        self.navigate("video_feed")
        self.video_feed.start_streaming()
        
    def exit_app(self):
        self.close()
        