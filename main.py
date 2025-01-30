import speech_recognition as sr
import webbrowser
import pyttsx3
import musicLibrary
import requests
import threading
from openai import OpenAI
import pygame
import os
from groq import Groq

recognizer = sr.Recognizer()
engine = pyttsx3.init()
newsapi = "3101354945c24d068ecabebe8445128b"

# Set the voice to male (index 0 is male in your case)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # Using male voice

# Function to speak text using pyttsx3 (male voice)
def speak(text):
    engine.say(text)
    engine.runAndWait()  # Run the speech engine


#NOT WORKING FOR AN UNKNOWN REASON
def aiProcess(command):
    client = Groq(
    api_key=os.environ.get("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"),
    )

    chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a virtual assistant named jarvis skilled in general tasks like Alexa and Google Cloud. Give short responses please"
        },
        {
            "role": "user",
            "content": command,
        }
    ],
    model="llama-3.3-70b-versatile",)
    print(chat_completion.choices[0].message.content)
    # Uncomment the following section if you want to use OpenAI
    # client = OpenAI(api_key="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")
    # completion = client.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     messages=[{"role": "system", "content": "You are a virtual assistant named jarvis skilled in general tasks like Alexa and Google Cloud. Give short responses please"},
    #               {"role": "user", "content": command}]
    # )
    # return completion.choices[0].message.content


def processCommand(c):
    global stop_reading
    
    if "open google" in c.lower():
        webbrowser.open("https://google.com")
    elif "open facebook" in c.lower():
        webbrowser.open("https://facebook.com")
    elif "open youtube" in c.lower():
        webbrowser.open("https://youtube.com")
    elif "open linkedin" in c.lower():
        webbrowser.open("https://linkedin.com")
    elif c.lower().startswith("play"):
        song = c.lower().split(" ")[1]
        link = musicLibrary.music[song]
        webbrowser.open(link)
    elif "news" in c.lower():
        r = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&apiKey={newsapi}")
        if r.status_code == 200:
            data = r.json()
            articles = data.get('articles', [])
            
            stop_reading = False  # Reset stop flag
            
            # Start listening for "stop Jarvis" in a separate thread
            stop_thread = threading.Thread(target=listen_for_stop)
            stop_thread.start()

            for article in articles:
                if stop_reading:
                    break  # Stop immediately
                speak(article['title'])  # Read the news

    else:
        # Let AI like Groq handle the request
        output = aiProcess(c)
        speak(output)

def listen_for_stop():
    """ Continuously listens for the 'stop Jarvis' command. """
    global stop_reading
    recognizer = sr.Recognizer()

    while pygame.mixer.music.get_busy():  # Run while news is playing
        with sr.Microphone() as source:
            try:
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=1)
                command = recognizer.recognize_google(audio).lower()
                if "stop jarvis" in command:
                    stop_reading = True
                    pygame.mixer.music.stop()  # Immediately stop audio
                    print("News stopped by user.")
                    break
            except sr.UnknownValueError:
                pass  # Ignore if no command is heard
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}")

if __name__ == "__main__":
    speak("Initializing Jarvis....")
    while True:
        r = sr.Recognizer()
        print("recognizing...")
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = r.listen(source, timeout=2, phrase_time_limit=1)
            word = r.recognize_google(audio)
            if word.lower() == "jarvis":
                speak("Ya")
                # Listen for command
                with sr.Microphone() as source:
                    print("Jarvis Active...")
                    audio = r.listen(source)
                    command = r.recognize_google(audio)
                    processCommand(command)

        except Exception as e:
            print("Error; {0}".format(e))
