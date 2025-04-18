from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QLineEdit,
    QLabel
)

from PyQt6.QtGui import (
    QFont,
    QIntValidator,
    QDoubleValidator
)

from Model.CaptureConfig import CaptureConfig

class AdvancedConfigurationModal(QDialog):
    def __init__(self, parent, config = CaptureConfig):
        super().__init__(parent)
        self.config = config
        
        self.setWindowTitle("Advanced Perclos Configuration")

        QBtn = (
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Reset | QDialogButtonBox.StandardButton.Cancel
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.save_config)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.button(QDialogButtonBox.StandardButton.Reset).clicked.connect(self.reset_config)
        
        perclos_high_threshold_label = QLabel("Perclos High Threshold")
        perclos_high_threshold_label.setFont(QFont('Arial font', 10))
        self.perclos_high_threshold_input = QLineEdit(parent=self)
        self.perclos_high_threshold_input.setValidator(QIntValidator(bottom=0, top=100))
        self.perclos_high_threshold_input.setText(str(self.config.perclos_high_threshold))
        
        perclos_mid_threshold_label = QLabel("Perclos Mid Threshold")
        perclos_mid_threshold_label.setFont(QFont('Arial font', 10))
        self.perclos_mid_threshold_input = QLineEdit(parent=self)
        self.perclos_mid_threshold_input.setValidator(QIntValidator(bottom=0, top=100))
        self.perclos_mid_threshold_input.setText(str(self.config.perclos_mid_threshold))
        
        perclos_low_threshold_label = QLabel("Perclos Low Threshold")
        perclos_low_threshold_label.setFont(QFont('Arial font', 10))
        self.perclos_low_threshold_input = QLineEdit(parent=self)
        self.perclos_low_threshold_input.setValidator(QIntValidator(bottom=0, top=100))
        self.perclos_low_threshold_input.setText(str(self.config.perclos_low_threshold))
        
        perclos_window_size_label = QLabel("Perclos Window Size (s)")
        perclos_window_size_label.setFont(QFont('Arial font', 10))
        self.perclos_window_size_input = QLineEdit(parent=self)
        self.perclos_window_size_input.setValidator(QIntValidator(bottom=1))
        self.perclos_window_size_input.setText(str(self.config.perclos_window_size))
        
        blink_detection_threshold_label = QLabel("Blink Detection Threshold")
        blink_detection_threshold_label.setFont(QFont('Arial font', 10))
        self.blink_detection_threshold_input = QLineEdit(parent=self)
        self.blink_detection_threshold_input.setValidator(QDoubleValidator(bottom=0.001, decimals=5))
        self.blink_detection_threshold_input.setText(str(self.config.blink_detection_threshold))
        
        blink_window_size_label = QLabel("Blink Window Size (s)")
        blink_window_size_label.setFont(QFont('Arial font', 10))
        self.blink_window_size_input = QLineEdit(parent=self)
        self.blink_window_size_input.setValidator(QIntValidator(bottom=1))
        self.blink_window_size_input.setText(str(self.config.blink_window_size))
        
        fps_label = QLabel("FPS (Frames per second)")
        fps_label.setFont(QFont('Arial font', 10))
        self.fps_input = QLineEdit(parent=self)
        self.fps_input.setValidator(QIntValidator(bottom=1))
        self.fps_input.setText(str(self.config.fps))
        
        
        layout = QVBoxLayout()
        layout.addWidget(perclos_high_threshold_label)
        layout.addWidget(self.perclos_high_threshold_input)
        layout.addWidget(perclos_mid_threshold_label)
        layout.addWidget(self.perclos_mid_threshold_input)
        layout.addWidget(perclos_low_threshold_label)
        layout.addWidget(self.perclos_low_threshold_input)
        layout.addWidget(perclos_window_size_label)
        layout.addWidget(self.perclos_window_size_input)
        layout.addWidget(blink_detection_threshold_label)
        layout.addWidget(self.blink_detection_threshold_input)
        layout.addWidget(blink_window_size_label)
        layout.addWidget(self.blink_window_size_input)
        layout.addWidget(fps_label)
        layout.addWidget(self.fps_input)
        
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
        
    def reset_config(self):
        self.config.reset()
        self.perclos_high_threshold_input.setText(str(self.config.perclos_high_threshold))
        self.perclos_mid_threshold_input.setText(str(self.config.perclos_mid_threshold))
        self.perclos_low_threshold_input.setText(str(self.config.perclos_low_threshold))
        self.perclos_window_size_input.setText(str(self.config.perclos_window_size))
        self.blink_detection_threshold_input.setText(str(self.config.blink_detection_threshold))
        self.blink_window_size_input.setText(str(self.config.blink_window_size))
        self.fps_input.setText(str(self.config.fps))
        
    def save_config(self):
        self.config.set_perclos_high_threshold(self.perclos_high_threshold_input.text())
        self.config.set_perclos_mid_threshold(self.perclos_mid_threshold_input.text())
        self.config.set_perclos_low_threshold(self.perclos_low_threshold_input.text())
        self.config.set_perclos_window_size(self.perclos_window_size_input.text())
        self.config.set_blink_detection_threshold(self.blink_detection_threshold_input.text())
        self.config.set_blink_window_size(self.blink_window_size_input.text())
        self.config.set_fps(self.fps_input.text())
        self.accept()
        