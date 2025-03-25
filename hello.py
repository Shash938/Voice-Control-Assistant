import speech_recognition as sr
import cv2
import mediapipe as mp
import pyautogui
import webbrowser
import subprocess
import os
import time
import threading

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

recognizer = sr.Recognizer()
WAKE_WORD = "hello"  
SCROLL_SENSITIVITY = 10

def listen_for_wake_word():
    try:
        with sr.Microphone() as source:
            print("Hello: Waiting for the wake word...")
            recognizer.adjust_for_ambient_noise(source)
            while True:
                print("Hello: Listening...")
                audio = recognizer.listen(source, timeout=2, phrase_time_limit=3)  
                try:
                    command = recognizer.recognize_google(audio).lower()
                    print(f"Heard: {command}")
                    if WAKE_WORD in command:
                        print(f"Hello: Wake word detected! How can I assist you?")
                        return True
                except sr.UnknownValueError:
                    print("Hello: Could not understand audio. Please try again.")
                except sr.RequestError as e:
                    print(f"Hello: Speech service error: {e}. Retrying...")
                    time.sleep(2)
                except sr.WaitTimeoutError:
                    print("Hello: Listening timed out. Waiting for the wake word...")
    except AttributeError:
        print("Hello: Microphone is not accessible. Please check your microphone and PyAudio installation.")
        return False
    except Exception as e:
        print(f"Hello: An error occurred: {e}")
        return False

def detect_gesture():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    prev_y = 0
    scroll_mode = False
    frame_counter = 0
    skip_frames = 2

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_counter += 1
        if frame_counter % skip_frames != 0:
            continue

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                index_x = int(index_tip.x * frame.shape[1])
                index_y = int(index_tip.y * frame.shape[0])
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                thumb_x = int(thumb_tip.x * frame.shape[1])
                thumb_y = int(thumb_tip.y * frame.shape[0])
                distance = ((thumb_x - index_x) ** 2 + (thumb_y - index_y) ** 2) ** 0.5

                if distance < 50:
                    print("Hello: Gesture detected - Play/Pause")
                    pyautogui.press("space")
                    time.sleep(1)

                if thumb_y < index_y and abs(thumb_x - index_x) < 50:
                    if not scroll_mode:
                        print("Hello: Thumbs up detected. Scroll mode enabled.")
                        scroll_mode = True
                    if prev_y != 0:
                        delta_y = thumb_y - prev_y
                        if abs(delta_y) > SCROLL_SENSITIVITY:
                            scroll_amount = int(-delta_y / SCROLL_SENSITIVITY)
                            pyautogui.scroll(scroll_amount)
                            print(f"Hello: Scrolling {scroll_amount} units")
                    prev_y = thumb_y
                else:
                    if scroll_mode:
                        print("Hello: Thumbs up released. Scroll mode disabled.")
                        scroll_mode = False
                    prev_y = 0

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def main():
    print("Hello: Initializing...")
    print("Hello: Hello! I am ready to assist you.")
    while True:
        if listen_for_wake_word():
            command = listen_for_command()
            if command:
                if "exit" in command or "quit" in command:
                    print("Hello: Shutting down. Goodbye!")
                    break
                execute_command(command)

if __name__ == "__main__":
    main()
