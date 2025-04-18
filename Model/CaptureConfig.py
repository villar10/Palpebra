class CaptureConfig:
    # Default values
    DEFAULT_PERCLOS_HIGH_THRESHOLD = int(20)   #As percentage (i.e., 20 = 20%, 15 = 15%)
    DEFAULT_PERCLOS_MID_THRESHOLD = int(15)  #As percentage (i.e., 20 = 20%, 15 = 15%)
    DEFAULT_PERCLOS_LOW_THRESHOLD = int(10)  #As percentage (i.e., 20 = 20%, 15 = 15%)
    DEFAULT_PERCLOS_WINDOW_SIZE = int(15)        #In seconds
    DEFAULT_BLINK_THRESHOLD = int(2)     #Threshold for number of blinks over BLINK_WINDOW_SIZE. As int
    DEFAULT_BLINK_DETECTION_THRESHOLD = float(0.35)
    DEFAULT_BLINK_WINDOW_SIZE = int(15)          #In seconds
    DEFAULT_FPS = int(40)
    
    def __init__(self) -> None:
        self.reset()
        
    def reset(self):
        self.perclos_high_threshold = self.DEFAULT_PERCLOS_HIGH_THRESHOLD
        self.perclos_mid_threshold = self.DEFAULT_PERCLOS_MID_THRESHOLD
        self.perclos_low_threshold = self.DEFAULT_PERCLOS_LOW_THRESHOLD
        self.perclos_window_size = self.DEFAULT_PERCLOS_WINDOW_SIZE
        self.blink_threshold = self.DEFAULT_BLINK_THRESHOLD
        self.blink_detection_threshold = self.DEFAULT_BLINK_DETECTION_THRESHOLD
        self.blink_window_size = self.DEFAULT_BLINK_WINDOW_SIZE
        self.fps = self.DEFAULT_FPS
        self.camera = None
        self.participant_id = ""
        self.condition = ""
        self.report_directory = ""
        
    def set_camera(self, camera):
        self.camera = camera
        
    def set_perclos_high_threshold(self, perclos_high_threshold):
        self.perclos_high_threshold = int(perclos_high_threshold)
        
    def set_perclos_mid_threshold(self, perclos_mid_threshold):
        self.perclos_mid_threshold = int(perclos_mid_threshold)
        
    def set_perclos_low_threshold(self, perclos_low_threshold):
        self.perclos_low_threshold = int(perclos_low_threshold)
        
    def set_perclos_window_size(self, perclos_window_size):
        self.perclos_window_size = int(perclos_window_size)
        
    def set_blink_threshold(self, blink_threshold):
        self.blink_threshold = int(blink_threshold)

    def set_blink_detection_threshold(self, blink_detection_threshold):
        self.blink_detection_threshold = float(blink_detection_threshold)
    
    def set_blink_window_size(self, blink_window_size):
        self.blink_window_size = int(blink_window_size)
        
    def set_fps(self, fps):
        self.fps = int(fps)    
        
    def set_participant_id(self, participant_id):
        self.participant_id = participant_id
        
    def set_condition(self, condition):
        self.condition = condition
        
    def set_report_directory(self, report_directory):
        self.report_directory = report_directory
        
    def as_list(self):
        ans = []
        ans.append(self.perclos_high_threshold)
        ans.append(self.perclos_mid_threshold)
        ans.append(self.perclos_low_threshold)
        ans.append(self.perclos_window_size)
        #ans.append(self.blink_threshold)
        ans.append(self.blink_detection_threshold)
        ans.append(self.blink_window_size)
        ans.append(self.fps)
        
        return ans
        