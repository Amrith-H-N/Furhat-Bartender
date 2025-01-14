from furhat_remote_api import FurhatRemoteAPI 
import time 
import pyjokes 
import python_weather 
import asyncio 
import os 
from pygooglenews import GoogleNews 
gestures = [{'duration': 0.96, 'name': 'BigSmile'}, {'duration': 0.4, 'name': 
'Blink'}, {'duration': 1.0, 'name': 'BrowFrown'}, {'duration': 1.0, 'name': 
'BrowRaise'}, {'duration': 0.4, 'name': 'CloseEyes'}, {'duration': 3.0, 'name': 
'ExpressAnger'}, {'duration': 3.0, 'name': 'ExpressDisgust'}, {'duration': 3.0, 
'name': 'ExpressFear'}, {'duration': 3.0, 'name': 'ExpressSad'}, {'duration': 3.0, 
'name': 'GazeAway'}, {'duration': 1.6, 'name': 'Nod'}, {'duration': 0.96, 'name': 
'Oh'}, {'duration': 0.4, 'name': 'OpenEyes'}, {'duration': 2.0, 'name': 'Roll'}, 
{'duration': 1.2, 'name': 'Shake'}, {'duration': 1.04, 'name': 'Smile'}, 
{'duration': 0.96, 'name': 'Surprise'}, {'duration': 1.6, 'name': 'Thoughtful'}, 
{'duration': 0.67, 'name': 'Wink'}] 
def get_news(): 
    # Create a GoogleNews object 
    gn = GoogleNews() 
    # Search for news articles 
    result = gn.top_news() 
    # Print  the titles of the articles 
    articles = result['entries'] 
    for article in articles: 
        print(article.title) 
    return articles 

async def getweather() -> None: 
    # declare  the client. the measuring unit used defaults to the metric system (celcius, km/h, etc.) 
    async with python_weather.Client(unit=python_weather.IMPERIAL) as client: 
    # fetch  a weather forecast from a city 
        weather  = await client.get('Uppsala') 
    # returns the current day's forecast temperature (int) 
    return weather.temperature 

furhat = FurhatRemoteAPI("localhost") 
voices = furhat.get_voices() 
#gestures =  furhat.get_gestures() 
print(gestures) 
# Select a character for the virtual Furhat 
furhat.set_face(character="Isabel", mask="adult") 
# Set the voice of the robot 
furhat.set_voice(name='Joanna') 
def speak(input): 
    # Have Furhat greet the user 
    furhat.say(text=str(input), blocking=True) 

def gesture(value): 
    furhat.gesture(name=str(value)) 

def listen(): 
    # Listen to the user's response 
    response = furhat.listen() 
    # Check  if listening was successful 
    if response.success and response.message: 
        print("User said:", response.message) 
        return response.message 
    else: 
        print("Listening failed or no speech detected.") 
    return 0 

def script(): 
    time.sleep(10) 
    j=0 
    speak("hello human") 
    gesture(gestures[0]["name"]) 
    while(True): 
        speak("What is your name") 
        gesture(gestures[3]["name"]) 
        name = listen() 
        if name!=0: 
            speak("nice to meet you "+name) 
            gesture(gestures[6]["name"]) 
            break 
        else: 
            speak("I didnt get your name") 
            speak("How can I help you "+ name) 
            j=0 
            while(True): 
                question = listen() 
                time.sleep(1) 
                gesture(gestures[j]["name"]) 
                j=j+1 
                if j>len(gestures): 
                    j=0 
                    if question=="tell me a joke": 
                        My_joke = pyjokes.get_joke(language="en", category="neutral") 
                        speak(My_joke) 
                    if question =="what is the weather today": 
                        temp = asyncio.run(getweather()) 
                        temp = (temp - 32) / 1.8 
                        speak(str(temp)+"degree celcius") 
                    if question == "what is today's news": 
                        articles = get_news() 
                        i=0 
                        for article in articles: 
                            speak(str(article.title)) 
                            time.sleep(3) 
                            i=i+1 
                            if i > 5: 
                                break 

if __name__  == "__main__": 
    if os.name == 'nt': 
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) 
    script() 