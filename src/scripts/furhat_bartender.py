from ollama import chat
from furhat_remote_api import FurhatRemoteAPI
import time
import asyncio
import os
import random
from emotion_detection import (
    EmotionDetectionService,
)  # Import our emotion detection class


class EmotionalFurhatBartender:
    def __init__(self):
        # Initialize Furhat connection
        self.furhat = FurhatRemoteAPI("localhost")

        # Initialize emotion detection
        self.emotion_service = EmotionDetectionService()
        self.emotion_service.start()

        # Set up Furhat appearance
        self.furhat.set_face(character="Isabel", mask="adult")
        self.furhat.set_voice(name="Joanna")

        # Map emotions to gestures for more natural responses
        self.emotion_gestures = {
            "happy": {"duration": 0.96, "name": "BigSmile"},
            "sad": {"duration": 1.6, "name": "Thoughtful"},
            "angry": {"duration": 1.0, "name": "BrowRaise"},
            "surprise": {"duration": 0.96, "name": "Surprise"},
            "fear": {"duration": 1.0, "name": "BrowRaise"},
            "disgust": {"duration": 1.0, "name": "BrowFrown"},
            "neutral": {"duration": 0.96, "name": "Smile"},
        }

        # Emotional response templates
        self.emotional_responses = {
            "happy": [
                "Glad to see you're in good spirits!",
                "Your smile is contagious!",
                "Having a great day, aren't you?",
            ],
            "sad": [
                "Hey, everything alright?",
                "Sometimes talking helps. I'm here to listen.",
                "Let me know if you need someone to talk to.",
            ],
            "angry": [
                "I sense you might be having a rough day.",
                "Take it easy, we'll make sure you have a good time.",
                "Deep breaths - let's start with something refreshing.",
            ],
            "surprise": [
                "Oh! Something unexpected?",
                "That's quite a reaction!",
                "Must be something interesting!",
            ],
            "neutral": [
                "What can I get you?",
                "Any preferences tonight?",
                "Looking for something specific?",
            ],
        }

        # Drink recommendations based on emotion
        self.emotional_drinks = {
            "happy": ["Champagne", "Fruity cocktails", "Party punches"],
            "sad": ["Hot toddy", "Warm mulled wine", "Comfort cocktails"],
            "angry": ["Calming herbal mocktails", "Smooth whiskey", "Relaxing teas"],
            "surprise": ["Mystery cocktail", "Bartender's special", "Exotic blends"],
            "neutral": ["Classic cocktails", "House specials", "Popular mixes"],
        }

    def speak(self, text):
        """Have Furhat speak the given text"""
        print(f"Bartender says: {text}")
        self.furhat.say(text=str(text), blocking=True)

    def gesture_for_emotion(self, detected_emotion):
        """Select appropriate gesture based on detected emotion"""
        gesture_info = self.emotion_gestures.get(
            detected_emotion, self.emotion_gestures["neutral"]
        )
        self.furhat.gesture(name=gesture_info["name"])

    def listen(self):
        """Listen for user input"""
        response = self.furhat.listen()
        if response.success and response.message:
            print(f"Customer said: {response.message}")
            return response.message
        return None

    def get_emotional_response(self, detected_emotion):
        """Get appropriate response based on emotional state"""
        responses = self.emotional_responses.get(
            detected_emotion, self.emotional_responses["neutral"]
        )
        return random.choice(responses)

    def get_bartender_response(self, user_input, context, detected_emotion):
        """Get response from Ollama with emotional awareness"""
        try:
            # Include emotional context in the prompt
            emotional_context = f"""
            Customer's current emotional state: {detected_emotion}
            Recommended approach: {self.get_emotional_response(detected_emotion)}
            Suggested drinks: {', '.join(self.emotional_drinks.get(detected_emotion, []))}
            """

            response = chat(
                model="llama3.2",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are an emotionally intelligent bartender.
                        Current customer emotion: {detected_emotion}
                        
                        Guidelines:
                        - Adapt your tone to match the customer's emotional state
                        - If customer seems upset, be more empathetic and supportive
                        - If customer is happy, match their energy
                        - Maintain professional boundaries while being friendly
                        - Suggest drinks appropriate for their mood
                        - Keep responses concise and natural
                        - make friendly responses 
                        - do not be formal
                        Current context: {context}
                        {emotional_context}""",
                    },
                    {"role": "user", "content": user_input},
                ],
            )
            return response.message.content
        except Exception as e:
            print(f"Error getting Ollama response: {e}")
            return "Sorry, give me a moment to collect my thoughts."

    def run_bar(self):
        """Main bartender interaction loop"""
        try:
            # Initial greeting
            time.sleep(10)  # Give Furhat time to initialize
            self.speak("Welcome! I'll be your bartender tonight.")

            # Get customer's name
            while True:
                self.speak("What's your name, friend?")
                name = self.listen()
                if name:
                    break
                self.speak("Sorry, it's a bit loud in here. Could you repeat that?")

            # Main interaction loop
            context = f"Speaking with customer named {name}."
            # Get current emotional state
            detected_emotion = self.emotion_service.get_current_emotion()
            print(f"current emotion:{detected_emotion}")

            # Update gesture based on emotion
            self.gesture_for_emotion(detected_emotion)

            self.speak(self.get_emotional_response(detected_emotion))

            # Listen for customer input
            self.speak("What can I get you?")

            while True:
                # Get current emotional state
                detected_emotion = self.emotion_service.get_current_emotion()
                print(f"current emotion:{detected_emotion}")

                # Update gesture based on emotion
                self.gesture_for_emotion(detected_emotion)

                if random.random() < 0.5:
                    self.speak(self.get_emotional_response(detected_emotion))

                user_input = self.listen()

                if not user_input:
                    time.sleep(3)
                    continue

                if user_input.lower() in [
                    "goodbye",
                    "bye",
                    "exit",
                    "quit",
                    "thanks",
                    "thank you",
                ]:
                    self.speak("Take care! Hope to see you again soon!")
                    break

                # Get contextual response considering emotion
                response = self.get_bartender_response(
                    user_input, context, detected_emotion
                )
                self.speak(response)

                # Update context
                context += f"\nCustomer emotion: {detected_emotion}\nCustomer: {user_input}\nBartender: {response}"
                time.sleep(0.5)

        except Exception as e:
            print(f"Error in bar operation: {e}")
        finally:
            # Clean up
            self.emotion_service.stop()


if __name__ == "__main__":
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    bartender = EmotionalFurhatBartender()
    bartender.run_bar()
