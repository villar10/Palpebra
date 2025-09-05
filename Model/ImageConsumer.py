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
                    left_iris_pos  = fa.faces[0].get_landmark_pos(fa.faces[0].left_eye_center_index).tolist()
                    right_iris_pos = fa.faces[0].get_landmark_pos(fa.faces[0].right_eye_center_index).tolist()

                    #TODO: For Chiho, use get_landmarks_pos function from Face class to get all contours around the eye. Alternatively, we could just return the whole faces meshes if desired. Put this behind a setting that is by default ON but can be turned off to improve performance and logging. Also, we can consider improving logging I/O performance by wrapping the write command in a simple "every 20 frames" type loop to reduce I/O demands without sacrificing data loss in the event of a crash.
                    left_eyelid_loc = fa.faces[0].get_landmarks_pos(fa.faces[0].left_eyelids_indices).tolist()
                    right_eyelid_loc = fa.faces[0].get_landmarks_pos(fa.faces[0].right_eyelids_indices).tolist()

                    left_eye_loc = fa.faces[0].get_landmarks_pos(fa.faces[0].left_eye_contour_indices).tolist()
                    right_eye_loc = fa.faces[0].get_landmarks_pos(fa.faces[0].right_eye_contour_indices).tolist()

                    # Plot eye opening on each eye
                    cv.putText(image, f"{left_eye_opening:2.2f}", (int(left_iris_pos[0]+30), int(left_iris_pos[1])), cv.FONT_HERSHEY_SIMPLEX, .75, (255, 255, 255) if left_eye_opening>0.5 else (255,0,0),2)
                    cv.putText(image, f"{right_eye_opening:2.2f}", (int(right_iris_pos[0]-150), int(right_iris_pos[1])), cv.FONT_HERSHEY_SIMPLEX, .75, (255, 255, 255) if right_eye_opening>0.5 else (255,0,0),2)

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
                        
                    if blink_ready:
                        if num_blinks_in_window <= self.config.blink_threshold:
                            cv.putText(image, f"Blinks in last {self.config.blink_window_size} seconds : {num_blinks_in_window}", (10, 50), cv.FONT_HERSHEY_SIMPLEX, .75, (255, 0, 0),4)
                        else:
                            cv.putText(image, f"Blinks in last {self.config.blink_window_size} seconds : {num_blinks_in_window}", (10, 50), cv.FONT_HERSHEY_SIMPLEX, .75, (0, 255, 0),2)

                    # # Blink duration
                    cv.putText(image, f"Last Blink Duration (s) : {last_blink_duration:2.2f}s", (10, 75), cv.FONT_HERSHEY_SIMPLEX, .75, (0, 0, 0),2)
                    
                else:
                    one_face_detected = False
                    #TODO: Here, we should reset the variables that are logged to prevent duplicate logging of the same data point. These should probably instead be replaced with None or NaN, something to distinguish it from the rest of the data.

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
                    if one_face_detected:
                        self.report_facade.write_data(log_time = curr_frame_time, left_eye_opening = left_eye_opening, right_eye_opening = right_eye_opening, perclos = short_perclos, is_blink = is_blink, last_blink_duration = last_blink_duration, blink_rate = blink_rate, one_face_detected = one_face_detected, left_iris_loc = left_iris_pos, left_eyelid_loc = left_eyelid_loc, left_eye_loc = left_eye_loc, right_iris_loc = right_iris_pos, right_eyelid_loc = right_eyelid_loc, right_eye_loc = right_eye_loc)
                    else:
                        self.report_facade.write_data(log_time = curr_frame_time, left_eye_opening = "NaN", right_eye_opening = "NaN", perclos = "NaN", is_blink = "NaN", last_blink_duration = "NaN", blink_rate = "NaN", one_face_detected = one_face_detected,  left_iris_loc = "NaN", left_eyelid_loc = "NaN", left_eye_loc = "NaN", right_iris_loc = "NaN", right_eyelid_loc = "NaN", right_eye_loc = "NaN")
                except:
                    print("Unable to write to report: ", sys.exc_info())
                        
                qt_image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format.Format_RGB888)
                self.inner_image_update_signal.emit(qt_image)