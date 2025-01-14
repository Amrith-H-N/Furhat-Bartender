import cv2
import joblib
from feat import Detector
from PIL import Image
import numpy as np
import time
import threading
from queue import Queue
from collections import Counter
import logging


class EmotionDetectionService:
    def __init__(self, model_path="../model/"):
        # Initialize variables
        self.running = False
        self.current_emotion = "unknown"
        self.emotion_history = []
        self.history_size = 10  # Keep track of last 10 emotions for stability

        # Threading components
        self.thread = None
        self.lock = threading.Lock()
        self.emotion_queue = Queue(maxsize=100)

        # Emotion detection components
        self.model_pkl = "best_emotion_model_RandomForest_kaggle_working.pkl"
        self.detector = Detector(device="cuda")
        self.model = joblib.load(model_path + self.model_pkl)

        # Emotion mapping
        self.emotion_labels = {
            0: "neutral",
            1: "happy",
            2: "sad",
            3: "surprise",
            4: "fear",
            5: "disgust",
            6: "angry",
        }

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("EmotionDetection")

    def extract_features(self, frame):
        try:
            # Convert frame to format expected by py-feat
            frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            # Detect faces and extract features
            detections = self.detector.detect_faces(frame_pil)
            if len(detections) == 0:
                return None

            detected_landmarks = self.detector.detect_landmarks(frame, detections)
            if len(detected_landmarks) == 0:
                return None

            aus = self.detector.detect_aus(frame_pil, detected_landmarks)

            # Process AUs
            if isinstance(aus, list) and len(aus) > 0:
                aus_flat = np.array(aus[0]).flatten()[:20]
                return aus_flat
            return None

        except Exception as e:
            self.logger.error(f"Error in feature extraction: {str(e)}")
            return None

    def get_dominant_emotion(self):
        """Return the most common emotion from recent history"""
        with self.lock:
            if not self.emotion_history:
                return "unknown"
            return Counter(self.emotion_history).most_common(1)[0][0]

    def get_current_emotion(self):
        """Return the current dominant emotion"""
        return self.get_dominant_emotion()

    def _process_frame(self, frame):
        """Process a single frame and return detected emotion"""
        features = self.extract_features(frame)
        if features is not None and len(features) > 0:
            try:
                emotion_idx = self.model.predict([features])[0]
                return self.emotion_labels.get(emotion_idx, "unknown")
            except Exception as e:
                self.logger.error(f"Error in emotion prediction: {str(e)}")
        return "unknown"

    def _update_emotion_history(self, emotion):
        """Update the emotion history list"""
        with self.lock:
            self.emotion_history.append(emotion)
            if len(self.emotion_history) > self.history_size:
                self.emotion_history.pop(0)

    def _detection_loop(self):
        """Main detection loop running in separate thread"""
        cam = cv2.VideoCapture(0)
        desired_fps = 10
        frame_interval = 1 / desired_fps
        last_time = time.time()

        try:
            while self.running:
                # Control frame rate
                current_time = time.time()
                if current_time - last_time < frame_interval:
                    continue
                last_time = current_time

                # Read frame
                ret, frame = cam.read()
                if not ret:
                    self.logger.error("Failed to grab frame")
                    break

                # Process frame
                emotion = self._process_frame(frame)
                self._update_emotion_history(emotion)

                # Update current emotion in queue if needed
                if not self.emotion_queue.full():
                    self.emotion_queue.put(self.get_dominant_emotion())

        except Exception as e:
            self.logger.error(f"Error in detection loop: {str(e)}")
        finally:
            cam.release()

    def start(self):
        """Start the emotion detection service"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._detection_loop)
            self.thread.daemon = True
            self.thread.start()
            self.logger.info("Emotion detection service started")

    def stop(self):
        """Stop the emotion detection service"""
        self.running = False
        if self.thread:
            self.thread.join()
            self.logger.info("Emotion detection service stopped")


def main():
    """Test function to demonstrate usage"""
    emotion_service = EmotionDetectionService()
    emotion_service.start()

    try:
        while True:
            emotion = emotion_service.get_current_emotion()
            print(f"Current emotion: {emotion}")
            time.sleep(1)
    except KeyboardInterrupt:
        emotion_service.stop()


if __name__ == "__main__":
    main()
