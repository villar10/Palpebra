from PyQt6.QtCore import QThread
import queue
import cv2 as cv
import time

from Model.CaptureConfig import CaptureConfig

class ImageProducer():
    def __init__(self, queue_reference: queue, config: CaptureConfig) -> None:
        self.config = config
        self.queue = queue_reference
        self.image_collection = ImageProducer.ImageCollector(self)
        self.cap = cv.VideoCapture(self.config.camera, cv.CAP_DSHOW)
        self.cap.set(cv.CAP_PROP_FPS, self.config.fps)
        self.capturing = True
        
    def start_video_capture(self):
        self.capturing = True
        
        while not self.cap.isOpened():
                print(f"Capture with camera {self.config.camera} not initialized")
        
        self.image_collection.start()
        
    def stop_video_capture(self):
        self.capturing = False
        self.image_collection.quit()
        
    def shutdown(self):
        self.stop_video_capture()
        self.cap.release()
    
    class ImageCollector(QThread):
        def __init__(self, collection_reference) -> None:
            super().__init__()
            self.image_collection = collection_reference
            
        def run(self):
            while self.image_collection.capturing:
                start_time = time.time()
                ret, frame = self.image_collection.cap.read()
                    
                if not ret:
                    print("WARNING: Frame not returned from webcam. This is normal during shut down.")
                    break
                if not self.image_collection.queue.full():  # Avoid filling the queue with too many frames
                    self.image_collection.queue.put(frame)
                
                # Wait to maintain the frame rate
                time.sleep(max(0, (1 / self.image_collection.config.fps) - (time.time() - start_time)))
        