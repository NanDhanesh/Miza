# eyes.py
import cv2
import numpy as np
import time

class EyeTracker:
    def __init__(self):
        self.cap = None
        self.focus_time = 0
        self.start_time = None
        self.running = False

    def start(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open webcam")
            return

        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.focus_time = 0
        self.start_time = time.time()
        self.running = True

    def step(self):
        if not self.running:
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        eyes_detected = False
        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray)
            if len(eyes) > 0:
                eyes_detected = True
                break

        if eyes_detected:
            self.focus_time += 1  # Each frame = ~1 step; you can calibrate this

    def stop(self):
        self.running = False
        total_time = time.time() - self.start_time
        if self.cap:
            self.cap.release()
        focus_score = self.focus_time / total_time if total_time > 0 else 0
        return round(focus_score, 2)
