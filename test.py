#!/usr/bin/python3
from gpiozero import LED
import PySimpleGUI as sg
import face_recognition
import cv2
import numpy as np
import pickle
import pyttsx3
import speech_recognition as sr
# import threading
import wikipedia
from PIL import Image, ImageTk
import io
import time
import os
import random
import pandas as pd
import subprocess
import requests
proc = subprocess.Popen(["ls"])

# proc = subprocess.Popen(["lxterminal", "-e" , "/bin/bash -c 'source /opt/ros/kinetic/setup.bash && export ROS_MASTER_URI=http://192.168.1.4:11311 && export ROS_HOSTNAME=192.168.1.26 && rostopic pub /chatter std_msgs/String \"GOAL Test\"'"])
face_confidence = 0.5
close_loop = False
detection_confidence = 0.0
red = LED(23)
red.off()
green = LED(22)
green.off()
screen_window = (800, 480)  # (640, 480)  # 800x480 || 1280x720
slideshow_window = (480, 270)  # (400, 225)  # 480x270 || 720x405
opencv_window = (240, 270)  # (200, 225)  # 240x270 || 360x400
column_window = (320, 480)  # (320, 480)  # 320x480 || 500x720
logo_window = (120, 120)  # (120, 120)  # 100x100 || 200x200
speech_text = ''
engine = pyttsx3.init()  # object creation
engine.setProperty('voice', 'english')
engine.setProperty('rate', 155)     # setting up new voice rate
engine.setProperty('volume', 1.0)
PROMPT_LIMIT = 3
recognizer = sr.Recognizer()
microphone = sr.Microphone()#sample_rate=32000, device_index=2)
recognizer.pause_threshold = 1.2
recognizer.operation_timeout = 8.0
all_face_encodings = {}
with open('dataset_faces.dat', 'rb') as f:
    all_face_encodings = pickle.load(f)
# Load a sample picture and learn how to recognize it.
known_face_names = list(all_face_encodings.keys())
known_face_encodings = np.array(list(all_face_encodings.values()))
# Initialize some variables
face_locations = []
face_encodings = []
process_this_frame = True
folder = 'slideshow'          # if you want to use a file instead of data, then use this in Image Element
img_types = (".png", ".jpg", "jpeg", ".tiff", ".bmp")
prevtime = time.time()
slide_time = 5
flist0 = os.listdir(folder)
fnames = [f for f in flist0 if os.path.isfile(os.path.join(folder, f)) and f.lower().endswith(img_types)]
num_files = len(fnames)                # number of iamges found
if num_files == 0:
    sg.popup('No files in slideshow folder')
    raise SystemExit()
del flist0                             # no longer needed
fid = 0
logo = r'logo.png'          # if you want to use a file instead of data, then use this in Image Element
DISPLAY_TIME_MILLISECONDS = 4000
df = pd.read_excel('questions.xlsx')
ans_list = list(df['Answers'])
ques_list = list(df['Questions'])


def game():
    WORDS = ["apple", "banana", "grape", "orange", "mango", "lemon"]
    NUM_GUESSES = 3
    LIMIT = 3
    word = random.choice(WORDS)
    # print(word)
    speech_text = (
        "I'm thinking of one of these words:\n"
        "{words}\n"
        "You have {n} tries to guess which one.\n"
    ).format(words=', '.join(WORDS), n=NUM_GUESSES)

    # show instructions and wait 3 seconds before starting the game
    # print(instructions)
    '''myobj = gTTS(text=instructions, lang=language, slow=False)
    myobj.save("Intro.mp3")
    playsound('Intro.mp3')'''
    engine.say(speech_text)
    # window.write_event_value('-THREAD-', speech_text)
    print(speech_text)
    engine.runAndWait()
    for i in range(NUM_GUESSES):
        # get the guess from the user
        # if a transcription is returned, break out of the loop and
        #     continue
        # if no transcription returned and API request failed, break
        #     loop and continue
        # if API request succeeded but no transcription was returned,
        #     re-prompt the user to say their guess again. Do this up
        #     to PROMPT_LIMIT times
        for j in range(LIMIT):
            speech_text = 'Guess {}.'.format(i + 1)
            # print(speech_text)
            '''myobj = gTTS(text=speech_text, lang=language, slow=False)
            myobj.save("guess_text{}_{}.mp3".format(i+1,j+1))
            playsound("guess_text{}_{}.mp3".format(i+1,j+1))'''
            engine.say(speech_text)
            # window.write_event_value('-THREAD-', speech_text)
            print(speech_text)
            engine.runAndWait()
            guess = recognize_speech_from_mic(recognizer, microphone)
            if guess["transcription"]:
                break
            if not guess["success"]:
                break
            speech_text = "I didn't catch that. What did you say?\n"
            # print(speech_text)
            '''myobj = gTTS(text=speech_text, lang=language, slow=False)
            myobj.save("nani{}_{}.mp3".format(i+1,j+1))
            playsound("nani{}_{}.mp3".format(i+1,j+1))'''
            engine.say(speech_text)
            # window.write_event_value('-THREAD-', speech_text)
            print(speech_text)
            engine.runAndWait()
        # if there was an error, stop the game
        if guess["error"]:
            speech_text = "ERROR: {}".format(guess["error"])
            # print(speech_text)
            '''myobj = gTTS(text=speech_text, lang=language, slow=False)
            myobj.save("error{}.mp3".format(i+1))
            playsound("error{}.mp3".format(i+1))'''
            engine.say(speech_text)
            # window.write_event_value('-THREAD-', speech_text)
            print(speech_text)
            engine.runAndWait()
            break

        # show the user the transcription
        speech_text = "You said: {}".format(guess["transcription"])
        # print(speech_text)
        '''myobj = gTTS(text=speech_text, lang=language, slow=False)
        myobj.save("yousay{}.mp3".format(i+1))
        playsound("yousay{}.mp3".format(i+1))'''
        engine.say(speech_text)
        # window.write_event_value('-THREAD-', speech_text)
        print(speech_text)
        engine.runAndWait()
        # determine if guess is correct and if any attempts remain
        guess_is_correct = word.lower() in guess["transcription"].lower()
        user_has_more_attempts = i < NUM_GUESSES - 1

        # determine if the user has won the game
        # if not, repeat the loop if user has more attempts
        # if no attempts left, the user loses the game
        if guess_is_correct:
            speech_text = "Correct! You win!"
            # print(speech_text)
            '''myobj = gTTS(text=speech_text, lang=language, slow=False)
            myobj.save("winner.mp3")
            playsound("winner.mp3")'''
            engine.say(speech_text)
            # window.write_event_value('-THREAD-', speech_text)
            print(speech_text)
            engine.runAndWait()
            break
        elif user_has_more_attempts:
            speech_text = "Incorrect. Try again.\n"
            # print(speech_text)
            '''myobj = gTTS(text=speech_text, lang=language, slow=False)
            myobj.save("lose{}.mp3".format(i+1))
            playsound("lose{}.mp3".format(i+1))'''
            engine.say(speech_text)
            # window.write_event_value('-THREAD-', speech_text)
            print(speech_text)
            engine.runAndWait()
        else:
            speech_text = "Sorry, you lose!\nI was thinking of '{}'.".format(word)
            # print(speech_text)
            '''myobj = gTTS(text=speech_text, lang=language, slow=False)
            myobj.save("lose.mp3")
            playsound("lose.mp3")'''
            engine.say(speech_text)
            # window.write_event_value('-THREAD-', speech_text)
            print(speech_text)
            engine.runAndWait()
            break


def search(query):
    global ans_list, ques_list
    query = query.split(' ')
    query = " ".join(query[0:])
    answered = False
    for i in range(len(ques_list)):
        if (type(ques_list[i]) != str):
            continue
        if ques_list[i].lower() in query.lower():
            answered = True
            if (type(ans_list[i]) != str):
                speech_text = "No valid answer provided."
                engine.say(speech_text)
                print(speech_text)
                engine.runAndWait()
            else:
                speech_text = ans_list[i]
                engine.say(speech_text)
                print(speech_text)
                engine.runAndWait()
            break
    if not answered:
        speech_text = "Ok, I am asking to one of my friend for that, wait."
        engine.say(speech_text)
        print(speech_text)
        engine.runAndWait()
        try:
            speech_text = wikipedia.summary(query, sentences=1)
            engine.say(speech_text)
            # window.write_event_value('-THREAD-', speech_text)
            print(speech_text)
            engine.runAndWait()
        except Exception as e:
            print(str(e))
            speech_text = "Sorry I could find anything either."
            engine.say(speech_text)
            # window.write_event_value('-THREAD-', speech_text)
            print(speech_text)
            engine.runAndWait()


def recognize_speech_from_mic(recognizer, microphone):
    """Transcribe speech from recorded from `microphone`.

    Returns a dictionary with three keys:
    "success": a boolean indicating whether or not the API request was
               successful
    "error":   `None` if no error occured, otherwise a string containing
               an error message if the API could not be reached or
               speech was unrecognizable
    "transcription": `None` if speech could not be transcribed,
               otherwise a string containing the transcribed text
    """
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    '''speech_text = 'Speak!'
    engine.say(speech_text)
    # window.write_event_value('-THREAD-', speech_text)
    print(speech_text)
    engine.runAndWait()'''
    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }
    speech_text = 'Please Speak'
    engine.say(speech_text)
    # window.write_event_value('-THREAD-', speech_text)
    print(speech_text)
    engine.runAndWait()
    with microphone as source:
        # recognizer.adjust_for_ambient_noise(source, 1.0)
        try:
            audio = recognizer.listen(source, timeout=5)
        except sr.WaitTimeoutError:
            response["error"] = "Timed out watitng for User Input"
            return response
        # audio = recognizer.listen(source, timeout=4)
        # audio = recognizer.record(source, duration=4.5)

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #     update the response object accordingly
    try:
        response["transcription"] = recognizer.recognize_google(audio, language="en-US")
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response


def mic_listen():
    global face_names
    for j in range(PROMPT_LIMIT):
        guess = recognize_speech_from_mic(recognizer, microphone)
        if guess["transcription"]:
            break
        if not guess["success"]:
            break
        speech_text = "Please try again"
        engine.say(speech_text)
        # window.write_event_value('-THREAD-', speech_text)
        print(speech_text)
        engine.runAndWait()
    if guess["error"]:
        speech_text = "ERROR: {}".format(guess["error"])
        engine.say(speech_text)
        # window.write_event_value('-THREAD-', speech_text)
        print(speech_text)
        engine.runAndWait()
        speech_text = "Have a good day!"
        engine.say(speech_text)
        # window.write_event_value('-THREAD-', speech_text)
        print(speech_text)
        engine.runAndWait()
        return guess
    return guess


def listen_carefully(keywords):
    guess = mic_listen()
    if guess["error"]:
        return guess
    for i in keywords:
        if i.lower() in guess["transcription"].lower():
            return guess
    speech_text = "You said: {}".format(guess["transcription"])
    # engine.say(speech_text) # repeating user input
    # window.write_event_value('-THREAD-', speech_text)
    print(speech_text)
    return(guess)

    # print(speech_text)
    engine.runAndWait()
    speech_text = "Please confirm by saying 'Yes! I confirm' or 'No! I want to change'"
    engine.say(speech_text)
    # window.write_event_value('-THREAD-', speech_text)
    print(speech_text)
    engine.runAndWait()
    confirm = mic_listen()
    if confirm["error"]:
        return confirm
    if ("confirm" in confirm["transcription"].lower()) or ("yes" in confirm["transcription"].lower()):
        return guess
    elif ("quit" in confirm["transcription"].lower()) or ("stop" in confirm["transcription"].lower()) or ("skip" in confirm["transcription"].lower()):
        confirm["success"] = False
        confirm["error"] = "User skipped"
        return confirm
    else:
        speech_text = "Oh, I'm sorry for the inconvinience, can you type what you said?"
        engine.say(speech_text)
        # window.write_event_value('-THREAD-', speech_text)
        print(speech_text)
        engine.runAndWait()
        correct_response = {"success": True, "error": None,"transcription": None}
        correction = sg.popup_get_text(message='Please enter details', title='Correction', keep_on_top=True, location=(0, 200))
        correct_response["transcription"] = correction
        return correct_response


def assistant(name, face_encoding):
    # window.write_event_value('-THREAD-', "entered def assisstant")
    # window['out'].update("chech check")
    global face_names, all_face_encodings, known_face_names, known_face_encodings, proc, fid, prevtime
    red.on()
    if name == "Guest":
        # print("register")
        # speech_text = "Welcome Guest to Maharana Pratap Univetsity of Agriculture & Technology , Udaipur , I think I'm meeting you for the first time, may I register your details? Please respond with 'Yes! I want to register' or 'No! I want to continue', Please speak close to camera"
        speech_text = "Welcome Guest, khamaha ghanee, may I register your details or continue?"
        engine.say(speech_text)
        print(speech_text)
        engine.runAndWait()
        red.off()
        guess = listen_carefully(['register', 'yes', 'continue', 'no'])
        if guess["error"]:
            return False
        fid, prevtime = update_slide(fid, prevtime)
        event, values = window.read(timeout=45)  # timeout70
        if event == sg.WIN_CLOSED:
            return True
        if ("register".lower() in guess["transcription"].lower()) or ("yes".lower() in guess["transcription"].lower()):
            # take name, detail, save embedding
            speech_text = "Tell me your name please"
            engine.say(speech_text)
            print(speech_text)
            engine.runAndWait()
            guess = listen_carefully([])
            if guess["error"]:
                return False
            name = guess["transcription"]
            all_face_encodings[name] = face_encoding
            with open('dataset_faces.dat', 'wb') as f:
                pickle.dump(all_face_encodings, f)
            known_face_names = list(all_face_encodings.keys())
            known_face_encodings = np.array(list(all_face_encodings.values()))
            # speech_text = "Can I take your mobile number in single digits please?"
            # engine.say(speech_text)
            # print(speech_text)
            # engine.runAndWait()
            # guess = listen_carefully([])
            # if guess["error"]:
            #     return False
            fid, prevtime = update_slide(fid, prevtime)
            event, values = window.read(timeout=45)  # timeout70
            if event == sg.WIN_CLOSED:
                return True
            # mobile = guess["transcription"]
            '''speech_text = "Spell your email id please"
            engine.say(speech_text)
            print(speech_text)
            engine.runAndWait()
            guess = listen_carefully([])
            if guess["error"]:
                return False
            email = guess["transcription"]'''
            # send() email,mobile,name
            # url = 'https://clubfirstrobotics.com/utility/API/user'
            # myobj = {'CUSID': 1, 'DEVID': 1, 'NAME': name, 'PHONE': mobile}
            # x = requests.post(url, data=myobj, timeout=5)
            speech_text = "You have been successfully registered! Thank you!"
            engine.say(speech_text)
            print(speech_text)
            engine.runAndWait()
    fid, prevtime = update_slide(fid, prevtime)
    event, values = window.read(timeout=45)  # timeout70
    if event == sg.WIN_CLOSED:
        return True
    # speech_text = "Welcome " + name + ". I can register your complaint, play a game, take your feedback, answer a question or take you to some area."
    speech_text = "Hello " + name + "Khamha ghanee, What can I do for you? "
    engine.say(speech_text)
    # window.write_event_value('-THREAD-', speech_text)
    print(speech_text)
    engine.runAndWait()
    red.off()
    guess = listen_carefully(['complain', 'game', 'play', 'feedback', 'tour', 'navigate'])
    if guess["error"]:
        return False
    fid, prevtime = update_slide(fid, prevtime)
    event, values = window.read(timeout=45)  # timeout70
    if event == sg.WIN_CLOSED:
        return True
    if ("complain".lower() in guess["transcription"].lower()) or ("complain".lower() in guess["transcription"].lower()):
        # print("complaint")
        speech_text = "Tell me what went wrong, I'll try my best to resolve the issue."
        engine.say(speech_text)
        # window.write_event_value('-THREAD-', speech_text)
        print(speech_text)
        engine.runAndWait()
        comp = listen_carefully([])
        if comp["error"]:
            return False
        url = 'https://clubfirstrobotics.com/utility/API/complaint'
        myobj = {'CUSID': 1, 'DEVID': 1, 'C1': comp["transcription"], 'C2': name}
        x = requests.post(url, data=myobj, timeout=5)
        speech_text = 'Your complaint has been registerd and sent to the management.'
        engine.say(speech_text)
        # window.write_event_value('-THREAD-', speech_text)
        print(speech_text)
        engine.runAndWait()
    elif ("game".lower() in guess["transcription"].lower()) or ("play".lower() in guess["transcription"].lower()):
        # print("game")
        game()
    elif ("feedback".lower() in guess["transcription"].lower()) or ("feedback".lower() in guess["transcription"].lower()):
        # print("feedback")
        speech_text = "How was your experience here?"
        engine.say(speech_text)
        # window.write_event_value('-THREAD-', speech_text)
        print(speech_text)
        engine.runAndWait()
        feedback = listen_carefully([])
        if feedback["error"]:
            return False
        speech_text = "How many stars would you give us for our service?"
        engine.say(speech_text)
        # window.write_event_value('-THREAD-', speech_text)
        print(speech_text)
        engine.runAndWait()
        rating = listen_carefully([])
        if rating["error"]:
            return False
        url = 'https://clubfirstrobotics.com/utility/API/feedback'
        myobj = {'CUSID': 1, 'DEVID': 1, 'M1': feedback["transcription"], 'M2': rating["transcription"], 'M3': name}
        x = requests.post(url, data=myobj, timeout=5)
        speech_text = 'Your feedback has been registerd and sent to the management, Thank you!'
        engine.say(speech_text)
        # window.write_event_value('-THREAD-', speech_text)
        print(speech_text)
        engine.runAndWait()
    elif ("tour".lower() in guess["transcription"].lower()) or ("navigate".lower() in guess["transcription"].lower()):
        # print("feedback")
        speech_text = "I can take you to home, canteen, Student Section and library, where do you want to go?"
        engine.say(speech_text)
        # window.write_event_value('-THREAD-', speech_text)
        print(speech_text)
        engine.runAndWait()
        goal_pos = listen_carefully(['home', 'canteen', 'student', 'section', 'library'])
        if goal_pos["error"]:
            return False
        if ("home".lower() in goal_pos["transcription"].lower()):
            '''speech_text = "Are you sure you want me to take you there?"
            engine.say(speech_text)
            # window.write_event_value('-THREAD-', speech_text)
            print(speech_text)
            engine.runAndWait()
            goal = listen_carefully([])
            if goal["error"]:
                return False
            goal_msg = " "
            if ("yes".lower() in goal["transcription"].lower()) or ("sure".lower() in goal["transcription"].lower()):'''
            goal_msg = "GOALA"
            speech_text = "This way, follow me please, I will take you there."
            engine.say(speech_text)
            # window.write_event_value('-THREAD-', speech_text)
            print(speech_text)
            engine.runAndWait()
            proc.terminate()
            proc.wait()
            # proc = subprocess.Popen(["lxterminal", "-e", "/bin/bash -c 'source /opt/ros/kinetic/setup.bash && export ROS_MASTER_URI=http://192.168.1.106:11311 && export ROS_HOSTNAME=raspberrypi.local && rostopic pub /robot2/command std_msgs/String " + goal_msg + "'"])
            proc = subprocess.Popen(["lxterminal", "-e", "/bin/bash -c 'source /opt/ros/kinetic/setup.bash && export ROS_MASTER_URI=http://192.168.31.10:11311 && export ROS_HOSTNAME=raspberrypi.local && rostopic pub /robot2/command std_msgs/String " + goal_msg + "'"])
            window.bring_to_front()
        elif ("student".lower() in goal_pos["transcription"].lower()) or ("section".lower() in goal_pos["transcription"].lower()):
            '''speech_text = "Are you sure you want me to take you there?"
            engine.say(speech_text)
            # window.write_event_value('-THREAD-', speech_text)
            print(speech_text)
            engine.runAndWait()
            goal = listen_carefully([])
            if goal["error"]:
                return False
            goal_msg = " "
            if ("yes".lower() in goal["transcription"].lower()) or ("sure".lower() in goal["transcription"].lower()):'''
            goal_msg = "GOAL2"
            speech_text = "This way, follow me please, I will take you there."
            engine.say(speech_text)
            # window.write_event_value('-THREAD-', speech_text)
            print(speech_text)
            engine.runAndWait()
            proc.terminate()
            proc.wait()
            # proc = subprocess.Popen(["lxterminal", "-e", "/bin/bash -c 'source /opt/ros/kinetic/setup.bash && export ROS_MASTER_URI=http://192.168.1.106:11311 && export ROS_HOSTNAME=raspberrypi.local && rostopic pub /robot2/command std_msgs/String " + goal_msg + "'"])
            proc = subprocess.Popen(["lxterminal", "-e", "/bin/bash -c 'source /opt/ros/kinetic/setup.bash && export ROS_MASTER_URI=http://192.168.31.10:11311 && export ROS_HOSTNAME=raspberrypi.local && rostopic pub /robot2/command std_msgs/String " + goal_msg + "'"])
            window.bring_to_front()
        elif ("canteen".lower() in goal_pos["transcription"].lower()):
            '''speech_text = "Are you sure you want me to take you there?"
            engine.say(speech_text)
            # window.write_event_value('-THREAD-', speech_text)
            print(speech_text)
            engine.runAndWait()
            goal = listen_carefully([])
            if goal["error"]:
                return False
            goal_msg = " "
            if ("yes".lower() in goal["transcription"].lower()) or ("sure".lower() in goal["transcription"].lower()):'''
            goal_msg = "GOAL3"
            speech_text = "This way, follow me please, I will take you there."
            engine.say(speech_text)
            # window.write_event_value('-THREAD-', speech_text)
            print(speech_text)
            engine.runAndWait()
            proc.terminate()
            proc.wait()
            # proc = subprocess.Popen(["lxterminal", "-e", "/bin/bash -c 'source /opt/ros/kinetic/setup.bash && export ROS_MASTER_URI=http://192.168.1.106:11311 && export ROS_HOSTNAME=raspberrypi.local && rostopic pub /robot2/command std_msgs/String " + goal_msg + "'"])
            proc = subprocess.Popen(["lxterminal", "-e", "/bin/bash -c 'source /opt/ros/kinetic/setup.bash && export ROS_MASTER_URI=http://192.168.31.10:11311 && export ROS_HOSTNAME=raspberrypi.local && rostopic pub /robot2/command std_msgs/String " + goal_msg + "'"])
            window.bring_to_front()
        elif ("library".lower() in goal_pos["transcription"].lower()):
            '''speech_text = "Are you sure you want me to take you there?"
            engine.say(speech_text)
            # window.write_event_value('-THREAD-', speech_text)
            print(speech_text)
            engine.runAndWait()
            goal = listen_carefully([])
            if goal["error"]:
                return False
            goal_msg = " "
            if ("yes".lower() in goal["transcription"].lower()) or ("sure".lower() in goal["transcription"].lower()):'''
            goal_msg = "GOAL4"
            speech_text = "This way, follow me please, I will take you there."
            engine.say(speech_text)
            # window.write_event_value('-THREAD-', speech_text)
            print(speech_text)
            engine.runAndWait()
            proc.terminate()
            proc.wait()
            # proc = subprocess.Popen(["lxterminal", "-e", "/bin/bash -c 'source /opt/ros/kinetic/setup.bash && export ROS_MASTER_URI=http://192.168.1.106:11311 && export ROS_HOSTNAME=raspberrypi.local && rostopic pub /robot2/command std_msgs/String " + goal_msg + "'"])
            proc = subprocess.Popen(["lxterminal", "-e", "/bin/bash -c 'source /opt/ros/kinetic/setup.bash && export ROS_MASTER_URI=http://192.168.31.10:11311 && export ROS_HOSTNAME=raspberrypi.local && rostopic pub /robot2/command std_msgs/String " + goal_msg + "'"])
            window.bring_to_front()
        else:
            speech_text = "I'm sorry, I don't know where that is."
            engine.say(speech_text)
            # window.write_event_value('-THREAD-', speech_text)
            print(speech_text)
            engine.runAndWait()
    else:
        search(guess["transcription"])
        '''speech_text = "Sorry I can't do that."
        engine.say(speech_text)
        # window.write_event_value('-THREAD-', speech_text)
        print(speech_text)
        engine.runAndWait()'''
    fid, prevtime = update_slide(fid, prevtime)
    event, values = window.read(timeout=45)  # timeout70
    if event == sg.WIN_CLOSED:
        return True
    green.on()
    speech_text = "I hope I helped you, have a good day!"
    engine.say(speech_text)
    # window.write_event_value('-THREAD-', speech_text)
    print(speech_text)
    engine.runAndWait()
    green.off()
    return False
    # give options to execute, listen for response, speak, response, exit finally


def get_img_data(f, maxsize=screen_window, first=False):
    """Generate image data using PIL
    """
    img = Image.open(f)
    img.thumbnail(maxsize)
    if first:                     # tkinter is inactive the first time
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)


def update_slide(fid, prevtime):
    if time.time() - prevtime > slide_time:
        fid += 1
        if fid >= num_files:
            fid -= num_files
        filename = os.path.join(folder, fnames[fid])
        prevtime = time.time()
        window["-SIMAGE-"].update(data=get_img_data(filename, first=True, maxsize=slideshow_window))
    return fid, prevtime


# def the_gui():
#    global speech_text, engine, PROMPT_LIMIT, recognizer, microphone, all_face_encodings, known_face_encodings, known_face_names, face_encodings, face_locations
#    global folder, img_types, prevtime, slide_time, fnames, num_files, fid, logo, DISPLAY_TIME_MILLISECONDS, face_names, process_this_frame
filename = os.path.join(folder, fnames[fid])
sg.theme("Black")
sg.Window('Welcome to Club First', [[sg.Image(data=get_img_data(logo, first=True), size=screen_window)]], size=screen_window, no_titlebar=False, keep_on_top=True, location=(0, 0)).read(timeout=DISPLAY_TIME_MILLISECONDS, close=True,)
sg.theme("LightBlue4")
slideshow_column = [

    # [sg.Text("SlideShow")],

    # [sg.Text(size=(30, 1), key="-TOUT-", text="this line describes the image")],
    [sg.Output(key="out", size=(57, 5), background_color='White', font=("Helvetica", 11), text_color='Black', pad=((0, 0), (20, 0)), echo_stdout_stderr=False)],
    # [sg.Text(text='Adjusting microphone for ambient noise, please remain silent for 5 seconds.', pad=((0, 0), (45, 0)), font=("Helvetica", 18), text_color='Black', background_color='White', key='trans', size=(55, 5))],

    # [sg.Image(data=get_img_data(filename, first=True, maxsize=(720, 720)), key="-SIMAGE-", background_color="White", size=(720, 720))], ]
    [sg.Image(key="-SIMAGE-", background_color='White', pad=((0, 0), (40, 0)), data=get_img_data(filename, first=True, maxsize=slideshow_window), size=slideshow_window)],

    ]

image_viewer_column = [

    # [sg.Listbox(values=[], enable_events=True, size=(30, 5), key="-FILE LIST-")],
    [sg.Image(data=get_img_data(logo, first=True, maxsize=logo_window), pad=((0, 0), (12, 0)), key="-LOGO-", size=logo_window)],
    # [sg.Input(size=(15, 1), key='-IN-'), sg.Button('SEND', button_color=(sg.YELLOWS[0], sg.BLUES[0]), bind_return_key=True)],
    # [sg.Input(size=(15, 1), key='-IN-'), sg.Button('SEND', bind_return_key=True)],
    [sg.Image(filename="", key="-IMAGE-", background_color='White', pad=((0, 0), (20, 0)), size=opencv_window)], ]

layout = [

    [

        sg.Column(layout=slideshow_column, vertical_alignment='top', element_justification='center', justification='center'),

        sg.Column(layout=image_viewer_column, size=column_window, vertical_alignment='top', element_justification='center'),

    ]]

window = sg.Window("Club First", layout, location=(0, 0), no_titlebar=False, keep_on_top=False, size=screen_window).finalize()  # add size instead
# Run the Event Loop
cap = cv2.VideoCapture(0)
window['out'].update("What I say will Print here.......Searching for a face........")
speech_text = "Adjusting microphone for ambient noise, please remain silent for 1 second."
# engine.say(speech_text)
# window['trans'](speech_text)
print(speech_text)
# engine.runAndWait()
with microphone as source:
    recognizer.adjust_for_ambient_noise(source, 1.0)
speech_text = "Done! Thank you."
engine.say(speech_text)
engine.runAndWait()

while True:
    fid, prevtime = update_slide(fid, prevtime)
    event, values = window.read(timeout=45)  # timeout70
    if event == sg.WIN_CLOSED or close_loop:
        break
    for i in range(5):
        ret, frame = cap.read()
    framedd = cv2.resize(frame, opencv_window)
    imgbytes = cv2.imencode(".png", framedd)[1].tobytes()
    window["-IMAGE-"].update(data=imgbytes)
    '''elif event == '-THREAD-':
        window['trans'](values[event])
    elif event == 'SEND':
        query = values['-IN-'].rstrip()
        # EXECUTE YOUR COMMAND HERE
        # print('The command you entered was {}'.format(query), flush=True)
    elif event == "-FILE LIST-":  # A file was chosen from the listbox
        req = values["-FILE LIST-"][0]

        # print('The request you entered was {}'.format(req), flush=True)'''
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        try:
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        except Exception as e:
            print(str(e))
        rgb_small_frame = small_frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
        face_names = []
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Guest"

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            detection_confidence = face_distances[best_match_index]
            if matches[best_match_index] and detection_confidence < face_confidence:
                name = known_face_names[best_match_index]  # + str(detection_confidence)
                # print(detection_confidence)
            face_names.append(name)
            window['out'].update("")
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom + 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name + " ({:.2f})".format(detection_confidence), (left + 6, bottom + 30), font, 1.0, (255, 255, 255), 1)
                # # print(name)
            frame = cv2.resize(frame, opencv_window)
            imgbytes = cv2.imencode(".png", frame)[1].tobytes()
            window["-IMAGE-"].update(data=imgbytes)
            # threading.Thread(target=assistant, args=(name, face_encoding, ), daemon=True).start()
            close_loop = assistant(name, face_encoding)
            break  
    process_this_frame = not process_this_frame
    '''# Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom + 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name + " ({:.2f})".format(detection_confidence), (left + 6, bottom + 30), font, 1.0, (255, 255, 255), 1)
        # # print(name)
    try:
        frame = cv2.resize(frame, opencv_window)
    except Exception as e:
        print(str(e))
    try:
        imgbytes = cv2.imencode(".png", frame)[1].tobytes()
    except Exception as e:
        print(str(e))
    window["-IMAGE-"].update(data=imgbytes)
    if time.time() - prevtime > slide_time:
        fid += 1
        if fid >= num_files:
            fid -= num_files
        filename = os.path.join(folder, fnames[fid])
        prevtime = time.time()
        window["-SIMAGE-"].update(data=get_img_data(filename, first=True, maxsize=slideshow_window))
        # window["column"].update(element_justification='center')
    # window["-SIMAGE-"].expand(expand_x=True, expand_y=True, expand_row=False)
    # window["-SIMAGE-"].update(filename=FILENAME)
    # fnames = ["Register a Complaint", "Register Guest Details", "Play a Game", "Give Feedback", "Exit"]
    # window["-FILE LIST-"].update(fnames)'''

cap.release()
cv2.destroyAllWindows()
window.close()
proc.terminate()
proc.wait()

# if __name__ == '__main__':
#    the_gui()
#    print('Exiting Program')
'''elif "question" in guess["transcription"].lower():
        # print("question")
        more = True
        while more:
            speech_text = "What do you want to know about?"
            engine.say(speech_text)
            # window.write_event_value('-THREAD-', speech_text)
            print(speech_text)
            engine.runAndWait()
            guess = mic_listen()
            if guess["error"]:
                # break
                return
            search(guess["transcription"])
            speech_text = "Do you want to ask any more questions? Say YES or NO"
            engine.say(speech_text)
            # window.write_event_value('-THREAD-', speech_text)
            print(speech_text)
            engine.runAndWait()
            loop_reply = mic_listen()
            if loop_reply["error"]:
                # break
                return
            if ("yes".lower() in loop_reply["transcription"].lower()) or ("more".lower() in loop_reply["transcription"].lower()):
                more = True
            else:
                more = False'''
