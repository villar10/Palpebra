from Model.CaptureConfig import CaptureConfig

import os
import csv
from datetime import datetime
from pathvalidate import sanitize_filename

import pandas as pd
import sys

class ReportGenerator:
    config_headers = ['perclos_high_threshold', 'perclos_mid_threshold', 'perclos_low_threshold', 'perclos_window_size', 'intended_fps']
    data_headers = ['timestamp', 'left_eye_opening', 'right_eye_opening', 'perclos']
    def __init__(self, config: CaptureConfig) -> None:
        self.config = config
        self.config_report = ""
        self.data_report = ""
        self.report_location = ""
        
    def initial_setup(self):
        self.initialize_directory()
        self.initialize_reports()
    
    def initialize_directory(self):
        report_start_time = datetime.now().strftime('%Y%m%d_%H-%M-%S')
        sanitized_participant_id = sanitize_filename(self.config.participant_id)
        sanitized_condition = sanitize_filename(self.config.condition)
        self.report_location = os.path.join(self.config.report_directory, f"P{sanitized_participant_id}_webcam_eye_tracking_{sanitized_condition}_{report_start_time}")
        try:
            os.mkdir(self.report_location)
        except:
            pass
        self.config_report = os.path.join(self.report_location, "config.csv")
        self.data_report = os.path.join(self.report_location, "data.csv")
    
    def initialize_reports(self):
        with(open(file=self.config_report, mode='w', newline='')) as config_file:
            writer = csv.writer(config_file)
            writer.writerow(self.config_headers)
            
        with(open(file=self.data_report, mode='w', newline='')) as data_file:
            writer = csv.writer(data_file)
            writer.writerow(self.data_headers)
        self.write_config()
    
    def write_config(self):
        with(open(file=self.config_report, mode='a', newline='')) as config_file:
            writer = csv.writer(config_file)
            writer.writerow(self.config.as_list())
        
    def write_data(self, log_time, left_eye_opening, right_eye_opening, perclos):
        timestamp = datetime.fromtimestamp(log_time).strftime('%Y-%m-%d-%H-%M-%S-%f')
        
        with(open(file=self.data_report, mode='a', newline='')) as data_file:
            writer = csv.writer(data_file)
            writer.writerow([timestamp, left_eye_opening, right_eye_opening, perclos])
        
    def get_data_report_location(self):
        return self.data_report

    def get_config_report_location(self):
        return self.data_report
    
    def generate_summary_report(self, trial_duration):
        summary = {}
        df = pd.read_csv(self.data_report)
        raw_data = df.copy(deep=True)
        df = df.dropna()
        
        summary['avg_left_eye_opening'] = [df['left_eye_opening'].mean()]
        summary['avg_right_eye_opening'] = [df['right_eye_opening'].mean()] 
        summary['avg_perclos'] = [df['perclos'].mean()]
        summary['trial_duration'] = trial_duration
        
        try:
            with pd.ExcelWriter(f"{self.report_location}\\final_report.xlsx") as writer:  
                pd.DataFrame.from_dict(summary).to_excel(writer, sheet_name='summary', index=False)
                raw_data.to_excel(writer, sheet_name='raw_data', index=False)
        except:
            print("Unable to produce summary report", sys.exc_info())
        
        
                
        