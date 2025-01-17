import cv2
import time
from emotion_detection import EmotionDetectionService


def test_emotion_detection():
    print("Starting Emotion Detection Test...")

    # Initialize the emotion detection service
    emotion_service = EmotionDetectionService()

    try:
        # Start the service
        print("Starting emotion detection service...")
        emotion_service.start()

        # Give time for camera to initialize
        time.sleep(2)

        print("\nEmotion Detection is running...")
        print("Press ESC in the video window or Ctrl+C in terminal to exit")

        while True:
            # Get current emotion

            current_emotion = emotion_service.get_current_emotion()

            print(f"Detected Emotion: {current_emotion}")

            # Small delay to prevent CPU overuse
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        # Cleanup
        print("Stopping emotion detection service...")
        emotion_service.stop()
        print("Test completed")


if __name__ == "__main__":
    test_emotion_detection()
