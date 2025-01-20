import os
import sys
import csv

from datetime import datetime

class Logger:
    headers = ['timestamp', 'event', 'element']
    def __init__(self, logs_directory, participant_id):
        self.logs_directory = logs_directory + "\\diagnosis"
        self.session_logs = self.logs_directory + f"\\P{participant_id}_{datetime.now().strftime('%Y%m%d_%H-%M-%S')}" 
        self.logs_file = self.session_logs + "\\logs.csv"
        
    def initialize(self):
        try:
            os.mkdir(self.logs_directory)
        except:
            pass
        
        try:
            os.mkdir(self.session_logs)
        except:
            pass
            
        self.initialize_logs_file()
            
    def initialize_logs_file(self):
        with(open(self.logs_file, 'a', newline='')) as logs_file:
            writer = csv.writer(logs_file)
            writer.writerow(self.headers)
            
    def generic_log(self, event, element):
        timestamp = datetime.now().strftime('%Y%m%d_%H-%M-%S')
        with(open(self.logs_file, 'a', newline='')) as logs_file:
            writer = csv.writer(logs_file)
            writer.writerow([timestamp, event, element])
        
    def log_button_pressed(self, button):
        self.generic_log('button pressed', button)
            
    def log_failure(self, failure):
        self.generic_log("failure", failure)
        
        
        