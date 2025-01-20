from PyQt6.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel
)

from PyQt6.QtGui import (
    QFont
)

from PyQt6.QtCore import Qt
import sys

class InitialPage(QWidget):
    def __init__(self, navigation_handler, exit_handler) -> None:
        super().__init__()
        self.navigation_handler = navigation_handler
        self.exit_handler = exit_handler
        
        layout = QVBoxLayout()
        buttons = QHBoxLayout()
        
        start_button = QPushButton("Configure new capture")
        start_button.setFixedSize(200, 50)
        start_button.clicked.connect(self.navigate_to_config)
        exit_button = QPushButton("Exit")
        exit_button.setFixedSize(100, 50)
        exit_button.clicked.connect(self.exit_handler)
        
        title = QLabel("Palpebra: PERCLOS Data Collection")
        title.setFont(QFont('Arial font', 25))
        
        # align layout elements
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        buttons.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)
        buttons.addWidget(exit_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(buttons)
        
        # align layout itself
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        
        self.setLayout(layout)
        
    def navigate_to_config(self):
        self.navigation_handler("configuration")
        
       
        