from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QPushButton,
    QWidget,
    QLabel,
    QLineEdit,
    QMessageBox,
    QFileDialog
)

from PyQt6.QtGui import (
    QFont
)

from PyQt6.QtCore import Qt

from View.Components.AdvancedConfigurationModal import AdvancedConfigurationModal
from Model.CaptureConfig import CaptureConfig
import Utils.CameraDetector as cam_detector

import os

class CaptureConfiguration(QWidget):
    def __init__(self, navigation_handler, configuration_handler) -> None:
        super().__init__()
        self.navigation_handler = navigation_handler
        self.configuration_handler = configuration_handler
        
        self.available_cameras = cam_detector.find_cameras()
        
        self.layout = QVBoxLayout()
        self.buttons = QHBoxLayout()
        self.create_buttons()
        
        self.config = CaptureConfig()
        
        # align layout itself
        self.build_layout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.setLayout(self.layout)
    
    def navigate_back(self):
        self.config.reset()
        self.navigation_handler("initial")
        
    def create_buttons(self):
        self.start_button = QPushButton("Save and start")
        self.start_button.setFixedSize(100, 50)
        self.start_button.clicked.connect(self.create_config)
        self.start_button.setEnabled(False)
        
        self.advanced_configuration_button = QPushButton("Advanced Configurations")
        self.advanced_configuration_button.setFixedSize(150, 50)
        self.advanced_configuration_button.clicked.connect(self.advanced_configurations)
        
        back_button = QPushButton("Go Back")
        back_button.setFixedSize(100, 50)
        back_button.clicked.connect(self.navigate_back)
        
        self.buttons.addWidget(self.start_button)
        self.buttons.addWidget(self.advanced_configuration_button)
        self.buttons.addWidget(back_button)
        
    def build_layout(self):
        title = QLabel("Capture configuration")
        title.setFont(QFont('Arial font', 25))
        
        camera_selection_label = QLabel("Select the camera to be used in the capture")
        camera_selection_label.setFont(QFont('Arial font', 10))
        
        camera_selection = QComboBox()
        camera_selection.addItem("None")
        camera_selection.addItems(list(self.available_cameras.values()))
        camera_selection.currentTextChanged.connect(self.camera_selection)
        
        participant_id_label = QLabel("Participant ID")
        participant_id_label.setFont(QFont('Arial font', 10))
        self.participant_id_input = QLineEdit(parent=self)
        
        self.select_location_button = QPushButton("Select report location")
        self.select_location_button.adjustSize()
        self.select_location_button.clicked.connect(self.select_report_location)
        
        # align layout elements
        self.layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(camera_selection_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(camera_selection, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(participant_id_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.participant_id_input, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.select_location_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addLayout(self.buttons)
        
    def create_config(self):
        participant_id = self.participant_id_input.text()
        if not participant_id:
            QMessageBox.critical(self, "Invalid configuration", "Participant ID cannot be empty")
        elif not self.config.report_directory:
            QMessageBox.critical(self, "Invalid configuration", "Please select a report location")
        else:
            self.config.set_participant_id(participant_id)
            self.configuration_handler(self.config)
        
    def select_report_location(self):
        location = str(QFileDialog.getExistingDirectory(self, "Select Directory", directory=os.path.expanduser("~/Desktop")))
        self.config.set_report_directory(location)
        self.select_location_button.setText(self.config.report_directory)
        self.select_location_button.adjustSize()
        
    def camera_selection(self, camera):
        if(camera != "None"):
            self.config.set_camera(self.camera_index(camera))
            self.start_button.setEnabled(True)
        else:
            self.start_button.setEnabled(False)
            
    def camera_index(self, camera_name: str):
        # list out keys and values separately
        key_list = list(self.available_cameras.keys())
        val_list = list(self.available_cameras.values())

        position = val_list.index(camera_name)
        return key_list[position]
    
    def advanced_configurations(self):
        modal = AdvancedConfigurationModal(parent=self, config=self.config)
        modal.exec()
        
        
            
              
        
        

        
       
        