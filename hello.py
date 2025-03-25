import speech_recognition as sr
import cv2
import mediapipe as mp
import pyautogui
import pyautogui
import webbrowser
import subprocess
import os
import time
import threading

# Initialize MediaPipe Hands for gesture recognition
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Wake word
WAKE_WORD = "hello"  

# Scroll sensitivity (adjust as needed)
SCROLL_SENSITIVITY = 10

# Function to listen for the wake word
def listen_for_wake_word():
    try:
        with sr.Microphone() as source:
            print("JARVIS: Waiting for the wake word...")
            recognizer.adjust_for_ambient_noise(source)
            while True:
                print("JARVIS: Listening...")
                audio = recognizer.listen(source, timeout=2, phrase_time_limit=3)  # Faster listening
                try:
                    command = recognizer.recognize_google(audio).lower()
                    print(f"Heard: {command}")
                    if WAKE_WORD in command:
                        print(f"JARVIS: Wake word detected! How can I assist you?")
                        return True
                except sr.UnknownValueError:
                    print("JARVIS: Could not understand audio. Please try again.")
                except sr.RequestError as e:
                    print(f"JARVIS: Speech service error: {e}. Retrying...")
                    time.sleep(2)  # Wait before retrying
                except sr.WaitTimeoutError:
                    print("JARVIS: Listening timed out. Waiting for the wake word...")
    except AttributeError:
        print("JARVIS: Microphone is not accessible. Please check your microphone and PyAudio installation.")
        return False
    except Exception as e:
        print(f"JARVIS: An error occurred: {e}")
        return False

# Function to detect hand gestures (play/pause and scroll)
def detect_gesture():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Lower resolution
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    prev_y = 0  # Store the previous y-coordinate of the thumb
    scroll_mode = False  # Toggle scroll mode
    frame_counter = 0
    skip_frames = 2  # Process every 2nd frame

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_counter += 1
        if frame_counter % skip_frames != 0:
            continue  # Skip this frame

        # Flip the frame horizontally for a mirror effect
        frame = cv2.flip(frame, 1)

        # Convert the frame to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        # Check for hand landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Get the coordinates of the index finger tip
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                index_x = int(index_tip.x * frame.shape[1])
                index_y = int(index_tip.y * frame.shape[0])

                # Get the coordinates of the thumb tip
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                thumb_x = int(thumb_tip.x * frame.shape[1])
                thumb_y = int(thumb_tip.y * frame.shape[0])

                # Calculate the distance between thumb and index finger tips
                distance = ((thumb_x - index_x) ** 2 + (thumb_y - index_y) ** 2) ** 0.5

                # Pinch gesture for play/pause
                if distance < 50:  # Adjust the threshold as needed
                    print("JARVIS: Gesture detected - Play/Pause")
                    pyautogui.press("space")
                    time.sleep(1)  # Add a delay to avoid multiple detections

                # Thumbs up gesture for scrolling
                if thumb_y < index_y and abs(thumb_x - index_x) < 50:  # Thumb above index finger
                    if not scroll_mode:
                        print("JARVIS: Thumbs up detected. Scroll mode enabled.")
                        scroll_mode = True
                    if prev_y != 0:
                        delta_y = thumb_y - prev_y
                        if abs(delta_y) > SCROLL_SENSITIVITY:
                            scroll_amount = int(-delta_y / SCROLL_SENSITIVITY)  # Invert for natural scrolling
                            pyautogui.scroll(scroll_amount)
                            print(f"JARVIS: Scrolling {scroll_amount} units")
                    prev_y = thumb_y
                else:
                    if scroll_mode:
                        print("JARVIS: Thumbs up released. Scroll mode disabled.")
                        scroll_mode = False
                    prev_y = 0

        # Exit the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Main function
def main():
    print("JARVIS: Initializing...")
    print("JARVIS: Hello! I am ready to assist you.")
    while True:
        # Wait for the wake word
        if listen_for_wake_word():
            # Listen for a command after the wake word is detected
            command = listen_for_command()
            if command:
                if "exit" in command or "quit" in command:
                    print("JARVIS: Shutting down. Goodbye!")
                    break
                execute_command(command)

if __name__ == "__main__":
    main()