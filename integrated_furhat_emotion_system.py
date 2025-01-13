
import cv2
import asyncio
import time
import os
import numpy as np
from keras.models import load_model
from furhat_remote_api import FurhatRemoteAPI
import pyjokes
import python_weather
from pygooglenews import GoogleNews

# Load the trained emotion detection model
model = load_model('path_to_the_model')  
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# Initialize Furhat API
furhat = FurhatRemoteAPI("localhost")
furhat.set_face(character="Isabel", mask="adult")
furhat.set_voice(name='Joanna')

gestures = [{'duration': 0.96, 'name': 'BigSmile'}, {'duration': 0.4, 'name': 'Blink'},
            {'duration': 1.0, 'name': 'BrowFrown'}, {'duration': 1.0, 'name': 'BrowRaise'},
            {'duration': 0.4, 'name': 'CloseEyes'}, {'duration': 3.0, 'name': 'ExpressAnger'},
            {'duration': 3.0, 'name': 'ExpressDisgust'}, {'duration': 3.0, 'name': 'ExpressFear'},
            {'duration': 3.0, 'name': 'ExpressSad'}, {'duration': 3.0, 'name': 'GazeAway'},
            {'duration': 1.6, 'name': 'Nod'}, {'duration': 0.96, 'name': 'Oh'},
            {'duration': 0.4, 'name': 'OpenEyes'}, {'duration': 2.0, 'name': 'Roll'},
            {'duration': 1.2, 'name': 'Shake'}, {'duration': 1.04, 'name': 'Smile'},
            {'duration': 0.96, 'name': 'Surprise'}, {'duration': 1.6, 'name': 'Thoughtful'},
            {'duration': 0.67, 'name': 'Wink'}]

def get_news():
    gn = GoogleNews()
    result = gn.top_news()
    articles = result['entries']
    return articles

async def getweather():
    async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
        weather = await client.get('Uppsala')
    return weather.temperature

def speak(input_text):
    furhat.say(text=str(input_text), blocking=True)

def gesture(value):
    furhat.gesture(name=str(value))

def detect_emotion(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized_frame = cv2.resize(gray_frame, (48, 48))
    resized_frame = np.expand_dims(resized_frame, axis=0) / 255.0
    prediction = model.predict(resized_frame)
    emotion_index = np.argmax(prediction)
    return emotion_labels[emotion_index]

def main():
    cap = cv2.VideoCapture(0)
    time.sleep(5)  # Allow camera to initialize
    
    speak("Hello! I am your friendly bartender Furhat. How are you feeling today?")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        
        emotion = detect_emotion(frame)
        print(f"Detected emotion: {emotion}")
        
        if emotion == "Happy":
            speak("You look happy! How about a joke to keep the mood light?")
            joke = pyjokes.get_joke(language="en", category="neutral")
            speak(joke)
            gesture("Smile")
        
        elif emotion == "Sad":
            speak("Oh, you look a bit down. Want to talk about it? Maybe I can cheer you up.")
            gesture("ExpressSad")
        
        elif emotion == "Neutral":
            speak("All good, I see. What can I get you to drink today?")
            gesture("Nod")
        
        elif emotion == "Angry":
            speak("You seem upset. Can I help you with something?")
            gesture("ExpressAnger")
        
        # Break on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    main()
