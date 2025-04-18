import numpy as np
import cv2 as cv
import time
from FaceAnalyzer import FaceAnalyzer 
from Model.CaptureConfig import CaptureConfig
from Utils.ReportGenerator import ReportGenerator
import queue
import sys

from PyQt6.QtCore import QThread, pyqtSignal, QObject

from PyQt6.QtGui import QImage

class ImageConsumer(QObject):
    image_update_signal = pyqtSignal(QImage)
    
    def __init__(self, config: CaptureConfig, queue_reference: queue.Queue, report_facade: ReportGenerator) -> None:
        super().__init__()
        self.config = config
        self.report_facade = report_facade
        self.queue = queue_reference
        self.video_analysis = None
        self.video_stream = None
        
    def start_video_stream(self):
        self.video_stream = ImageConsumer.ImageStreamer(self.queue)
        self.video_stream.inner_image_update_signal.connect(self.output_image)
        self.video_stream.start()
        
    def end_video_stream(self):
        self.video_stream.quit()
        
    def start_video_analysis(self):
        self.video_analysis = ImageConsumer.ImageAnalyzer(config=self.config, queue_reference=self.queue, report_facade=self.report_facade)
        self.video_analysis.inner_image_update_signal.connect(self.output_image)
        self.report_facade.initial_setup()
        self.video_analysis.start()
        
    def end_video_analysis(self):
        self.video_analysis.quit()
        
    def output_image(self, image):
        self.image_update_signal.emit(image)
        
    def shutdown(self):
        # Try to finish the threads, ignore exception if thread objects were not initialized 
        try:
            self.video_analysis.quit()
        except:
            pass
        try:
            self.video_stream.quit()
        except:
            pass
        
    class ImageStreamer(QThread):
        inner_image_update_signal = pyqtSignal(QImage)
        def __init__(self, queue_reference):
            super().__init__()
            self.queue_reference = queue_reference
        def run(self):
            while self.isRunning():
                image = self.queue_reference.get()
                # Convert it to RGB
                image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
                qt_image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format.Format_RGB888)
                self.inner_image_update_signal.emit(qt_image)
        
    class ImageAnalyzer(QThread):
        inner_image_update_signal = pyqtSignal(QImage)
        def __init__(self, queue_reference, config, report_facade):
            super().__init__()
            self.queue_reference = queue_reference
            self.report_facade = report_facade
            self.config = config
            
        def run(self):
            # Blinks counter
            n_blinks = 0

            # FPS processing
            prev_frame_time = time.time()
            curr_frame_time = time.time()

            # Prepare buffers
            blink_buffer = []
            short_perclos_buffer = []

            #Setup bools
            short_perclos_ready = False
            blink_ready = False
            PayingAttention = False
            one_face_detected = False

            # Build face analyzer
            fa = FaceAnalyzer(max_nb_faces=1)
            # Main Loop
            while self.isRunning():
                # Process fps
                curr_frame_time = time.time()
                dt = curr_frame_time-prev_frame_time
                prev_frame_time = curr_frame_time
                fps = 1/dt
                # Read an image from the camera
                image = self.queue_reference.get()
                # Convert it to RGB
                image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
                #cv.imshow('RGB image',image)
                # Process it
                fa.process(image)
                #Now if we find a face

                if fa.nb_faces==1:
                    one_face_detected = True
                    # Computes eyes opening level and blinks
                    left_eye_opening, right_eye_opening, is_blink, last_blink_duration = fa.faces[0].process_eyes(image, detect_blinks=True, blink_th=self.config.blink_detection_threshold) #, normalize=True   blink_th=0.35   # TODO: Determine what values are best here - should we normalize?

                    # Compute perclos items
                    # TODO: Below call for short_perclos may need to change fps to the config specified FPS. Currently, the buffer depth passed to compute perclos is dynamic which may lead to unexepcted behavior with the guaranteed fluctuations in calculated frame rate.
                    short_perclos = fa.faces[0].compute_perclos(left_eye_opening, right_eye_opening, self.config.perclos_window_size * int(fps), short_perclos_buffer, threshold=(self.config.perclos_high_threshold / 100))*100    #Gives result over time window in percentage, change threshold to .2 as default 
                    #print("Short perclos: ", short_perclos)
                    
                    if len(short_perclos_buffer) >= (self.config.perclos_window_size * int(fps)):
                        short_perclos_ready = True

                    fa.faces[0].draw_eyes_landmarks(image)
                    # Get eyes positions
                    left_eye_pos  = fa.faces[0].get_landmark_pos(fa.faces[0].left_eye_center_index)
                    right_eye_pos = fa.faces[0].get_landmark_pos(fa.faces[0].right_eye_center_index)
                    
                    # Plot eye opening on each eye
                    cv.putText(image, f"{left_eye_opening:2.2f}", (int(left_eye_pos[0]+30), int(left_eye_pos[1])), cv.FONT_HERSHEY_SIMPLEX, .75, (255, 255, 255) if left_eye_opening>0.5 else (255,0,0),2)
                    cv.putText(image, f"{right_eye_opening:2.2f}", (int(right_eye_pos[0]-150), int(right_eye_pos[1])), cv.FONT_HERSHEY_SIMPLEX, .75, (255, 255, 255) if right_eye_opening>0.5 else (255,0,0),2)

                    # Only after 15 seconds that we can use this perclos
                    if short_perclos_ready:
                        if short_perclos < self.config.perclos_low_threshold:
                            cv.putText(image, f"Perclos ({self.config.perclos_window_size} seconds) : {short_perclos:2.2f}%", (10, 25), cv.FONT_HERSHEY_SIMPLEX, .75, (0, 255, 0),2)
                        elif (short_perclos >= self.config.perclos_low_threshold) and (short_perclos < self.config.perclos_high_threshold):
                            cv.putText(image, f"Perclos ({self.config.perclos_window_size} seconds) : {short_perclos:2.2f}%", (10, 25), cv.FONT_HERSHEY_SIMPLEX, .75, (255, 170, 0),4)
                        else:
                            cv.putText(image, f"Perclos ({self.config.perclos_window_size} seconds) : {short_perclos:2.2f}%", (10, 25), cv.FONT_HERSHEY_SIMPLEX, .75, (255, 0, 0),4)



                    #Blink items
                    blink_buffer.append(is_blink)
                    blink_buffer_len = self.config.blink_window_size * int(fps)
                    #print("Expected len:", blink_buffer_len)
                    #print("Current len:", len(blink_buffer))

                    if len(blink_buffer) >= blink_buffer_len:
                        blink_ready = True

                    while len(blink_buffer) > blink_buffer_len:     # TODO: Is this necessary? If so, then perclos buffer should have similar statement. If not, then remove this.
                        blink_buffer.pop(0)
                    bb = np.array(blink_buffer)
                    num_blinks_in_window = ((bb == 1).astype(int).sum())
                    #blink_rate = (num_blinks_in_window / self.config.blink_window_size)*100    # Represents the number of blinks as a percentage of the total blink window size
                    blink_rate = num_blinks_in_window / (self.config.blink_window_size / 60)    # Finds blink rate by looking at number of blinks over the last blink_window_size seconds, and converting to blinks per minute
                    
                    # print("Blink rate: ", blink_rate)
                    # print("Blinks in last", self.config.blink_window_size, "seconds: ", num_blinks_in_window)

                    if is_blink:
                        n_blinks += 1   # Running counter of total blinks. Likely no longer needed
                        
                    # TODO: implement blink detection
                    if blink_ready:
                        if num_blinks_in_window <= self.config.blink_threshold:
                            cv.putText(image, f"Blinks in last {self.config.blink_window_size} seconds : {num_blinks_in_window}", (10, 50), cv.FONT_HERSHEY_SIMPLEX, .75, (255, 0, 0),4)
                        else:
                            cv.putText(image, f"Blinks in last {self.config.blink_window_size} seconds : {num_blinks_in_window}", (10, 50), cv.FONT_HERSHEY_SIMPLEX, .75, (0, 255, 0),2)

                    # # Blink duration
                    cv.putText(image, f"Last Blink Duration (s) : {last_blink_duration:2.2f}s", (10, 75), cv.FONT_HERSHEY_SIMPLEX, .75, (0, 0, 0),2)
                    
                else:
                    one_face_detected = False

                # TO-DO: review paying attention metrics for calculation
                # if blink_ready is True and short_perclos_ready is True:
                #     if (short_perclos > 20) or ((short_perclos > 10) and (num_blinks_in_window <= self.config.blink_threshold)):
                #         PayingAttention = False
                #     else:
                #         PayingAttention = True
                #         try:
                #             self.report_facade.write_data(curr_frame_time, left_eye_opening, right_eye_opening, is_blink, last_blink_duration, short_perclos, blink_rate, num_blinks_in_window, PayingAttention)
                #         except:
                #             print("Unable to write to report: ", sys.exc_info())
                #     # TO-DO: review paying attention metrics
                #     # if PayingAttention:
                #     #     cv.putText(image, f"Paying Attention? : Yes", (10, 135), cv.FONT_HERSHEY_SIMPLEX, .75, (0, 255, 0),2)
                #     # else:
                #     #     cv.putText(image, f"Paying Attention? : No", (10, 135), cv.FONT_HERSHEY_SIMPLEX, .75, (255, 0, 0),2)
                # else:
                #     cv.putText(image, f"Paying Attention? : N/A", (10, 135), cv.FONT_HERSHEY_SIMPLEX, .75, (0, 255, 0),2)
                #     try:
                #         self.report_facade.write_data(curr_frame_time, left_eye_opening, right_eye_opening, is_blink, last_blink_duration, short_perclos, blink_rate, num_blinks_in_window, None)
                #     except:
                #         print("Unable to write to report: ", sys.exc_info())
                
                try:
                    self.report_facade.write_data(log_time = curr_frame_time, left_eye_opening = left_eye_opening, right_eye_opening = right_eye_opening, perclos = short_perclos, is_blink = is_blink, last_blink_duration = last_blink_duration, blink_rate = blink_rate, one_face_detected = one_face_detected)      # TODO: Current behavior is to write data at every frame, regardless of whether a face is detected. If a face is not detected or multiple faces detected, it will simply write the most recent values, creating "fake" data. Also, if no face detected in initial frames, this will throw exception. We may consider moving this into the above "if" block if a face is detected, and if face is not detected, write a row of data that uses some threshold value. For now, will create simple boolean for tracking whether face is detected in that frame so user can decide whether they want to throw that data out.
                except:
                    print("Unable to write to report: ", sys.exc_info())
                        
                qt_image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format.Format_RGB888)
                self.inner_image_update_signal.emit(qt_image)