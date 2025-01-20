from PyQt6.QtWidgets import QApplication
from View.Components.Container import Container

import sys

class App:
    def __init__(self) -> None:
        app = QApplication(sys.argv)
        self.container = Container()
        
        app.exec()