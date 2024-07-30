import speech_recognition as sr
from gtts import gTTS
import pygame
import google.generativeai as genai
import re
import tkinter as tk
from tkinter import StringVar, PhotoImage
from PIL import Image, ImageTk
import time
import os
import sys
import os
from pathlib import Path
from PIL import Image, ImageTk
# Configure the Generative AI with API key
genai.configure(api_key='YOUR_API_KEY')
model = genai.GenerativeModel('gemini-1.0-pro-latest')

def convert_to_normal_passage(text, word_limit=100):
    cleaned_text = text.replace("*", "").replace("**", "")
    sentences = re.split(r'(?<=[.!?]) +', cleaned_text)
    accumulated_words = []
    total_words = 0
    
    for sentence in sentences:
        sentence_words = sentence.split()
        if total_words + len(sentence_words) <= word_limit:
            accumulated_words.extend(sentence_words)
            total_words += len(sentence_words)
        else:
            break
    limited_text = " ".join(accumulated_words)
    
    return limited_text

def update_status(new_status, icon=None):
    status_var.set(new_status)
    if icon:
        icon_label.config(image=icon)
        icon_label.image = icon
    else:
        icon_label.config(image='')
    root.update_idletasks()

def generate_unique_filename(base_filename):
    timestamp = int(time.time())
    filename, file_extension = os.path.splitext(base_filename)
    return f"{filename}_{timestamp}{file_extension}"

# def resource_path(relative_path):
#     """Get the absolute path to a resource, works for development and PyInstaller bundle."""
#     try:
#         # PyInstaller creates a temp folder and stores path in _MEIPASS
#         base_path = sys._MEIPASS
#     except Exception:
#         base_path = Path(__file__).parent
#     return os.path.join(base_path, relative_path)

def resize_icon(image_path, size=(50, 50)):
    with Image.open(image_path) as img:
        img = img.resize(size, Image.ANTIALIAS)
        return ImageTk.PhotoImage(img)

def listen_and_respond():
    recognizer = sr.Recognizer()
    with sr.Microphone(device_index=2, sample_rate = 48000) as source:
        update_status("Listening...")
        try:
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=6)
        except sr.WaitTimeoutError:
            update_status("No speech.")
            root.after(1000, listen_and_respond)
            return

    try:
        update_status("Processing...")
        text = recognizer.recognize_google(audio)
        text = convert_to_normal_passage(text)
        print("Converted audio to text:", text)
        
        if "ok google" in text.lower():
            update_status("Detected 'OK Google'. Exiting...")
            root.quit()
            return
        else:
            update_status("No 'OK Google'.")

        update_status("Generating...")
        response = model.generate_content("what is " + text).text
        response = convert_to_normal_passage(response)
        print(response)

        if response.strip():  # Check if the response is not empty or just whitespace
            filename = generate_unique_filename('output.mp3')
            update_status("Speaking...")
            tts = gTTS(text=response, lang='en')
            tts.save(filename)
            print(f"Saved audio to {filename}")

            pygame.mixer.init()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                continue
        else:
            update_status("No text to speak.")

        update_status("Waiting...")
        root.after(1000, listen_and_respond)  # Schedule the next listen

    except sr.UnknownValueError:
        update_status("Could not understand audio")
        root.after(1000, listen_and_respond)  # Continue listening
    except sr.RequestError as e:
        update_status(f"Request error; {e}")
        root.after(1000, listen_and_respond)  # Continue listening

# Initialize GUI
root = tk.Tk()
root.title("Voice Assistant")

# Set fixed size for the window
root.geometry("200x150")  # Width x Height
root.resizable(False, False)  # Disable resizing

status_var = StringVar()
status_label = tk.Label(root, textvariable=status_var, font=("Arial", 10))
status_label.pack(pady=10)

# Load and resize icons
# listening_icon = resize_icon("https://ibb.co/KGP7Dvd")
# processing_icon = resize_icon("https://ibb.co/xs791qS")
# speaking_icon = resize_icon("https://ibb.co/fNK83VP")
# error_icon = resize_icon("https://ibb.co/tzTQzMt")
# exit_icon = resize_icon("https://ibb.co/WfJfjHH")
# idle_icon = resize_icon("https://ibb.co/pZ8C8r4")
# # Label for displaying icons
icon_label = tk.Label(root)
icon_label.pack()

TEXT_OUTPUT_FILENAME = 'output.mp3'
status_var.set("Ready to listen...")
root.after(1000, listen_and_respond)

root.mainloop()
