import cv2
import mediapipe as mp
import numpy as np
import time

class HandTracker:
    def __init__(self, cap):
        self.cap = cap
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.pos = None
        self.pos_list = []
        self.close_start = None
        self.CLOSE_THRESHOLD = 1.2
        self.click_armed = True
        self.open_frames = 0

    def is_hand_closed(self, landmarks):
        tips = [8, 12, 16, 20]
        mcp  = [5,  9, 13, 17]
        closed_fingers = 0
        for tip, base in zip(tips, mcp):
            if landmarks[tip].y > landmarks[base].y:
                closed_fingers += 1
        return closed_fingers >= 3

    def process_frame(self, frame):
        click = False
        self.pos_list = []

        if frame is None:
            return None, None, False

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        if results.multi_hand_landmarks:
            h, w = frame.shape[:2]
            for hand in results.multi_hand_landmarks:
                lm = hand.landmark
                x = int(lm[9].x * w)
                y = int(lm[9].y * h)
                self.pos_list.append((x, y))

            self.pos = self.pos_list[0] if self.pos_list else None

            lm = results.multi_hand_landmarks[0].landmark
            hand_closed = self.is_hand_closed(lm)
            if hand_closed:
                self.open_frames = 0
                if self.click_armed:
                    if self.close_start is None:
                        self.close_start = time.time()
                    elif time.time() - self.close_start >= self.CLOSE_THRESHOLD:
                        click = True
                        self.click_armed = False
                        self.close_start = None
            else:
                self.close_start = None
                self.open_frames += 1
                if self.open_frames >= 4:
                    self.click_armed = True
        else:
            self.pos = None
            self.pos_list = []
            self.close_start = None
            self.open_frames = 0

        return rgb, self.pos, click

    def get_positions(self):
        return self.pos_list

    def process(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, None, False
        return self.process_frame(frame)

    def get_close_progress(self):
        if self.close_start is None:
            return 0.0
        return min((time.time() - self.close_start) / self.CLOSE_THRESHOLD, 1.0)