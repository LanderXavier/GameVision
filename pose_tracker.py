import cv2
import mediapipe as mp
import pygame
import numpy as np

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

class PoseTracker:
    def __init__(self, cap):
        self.cap = cap
        self.mp_pose = mp.solutions.pose
        self.left_pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=0,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.right_pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=0,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Índices mediapipe
        self.LEFT_WRIST  = 15
        self.RIGHT_WRIST = 16

        # Conexiones del esqueleto a dibujar
        self.CONNECTIONS = [
            (11, 12),
            (11, 13), (13, 15),
            (12, 14), (14, 16),
            (11, 23), (12, 24),
            (23, 24),
            (23, 25), (25, 27),
            (24, 26), (26, 28),
        ]

        self.p1_pos = None
        self.p2_pos = None
        self.left_landmarks_px = {}
        self.right_landmarks_px = {}

    def _extract_landmarks(self, results, x_offset=0, x_scale=1.0, flip_x=False):
        landmarks_px = {}

        if not results.pose_landmarks:
            return landmarks_px

        for i, point in enumerate(results.pose_landmarks.landmark):
            if point.visibility > 0.4:
                x = point.x
                if flip_x:
                    x = 1.0 - x
                landmarks_px[i] = (int((x * x_scale + x_offset)), int(point.y * SCREEN_HEIGHT))

        return landmarks_px

    def process_frame(self, frame):
        """Retorna surface pygame o None"""
        if frame is None:
            return None

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        h, w = frame.shape[:2]
        half_w = w // 2

        left_rgb = rgb[:, :half_w]
        right_rgb = rgb[:, half_w:]

        left_results = self.left_pose.process(left_rgb)
        right_results = self.right_pose.process(right_rgb)

        self.left_landmarks_px = self._extract_landmarks(left_results, x_offset=0, x_scale=half_w)
        self.right_landmarks_px = self._extract_landmarks(right_results, x_offset=half_w, x_scale=half_w)

        self.p1_pos = self.left_landmarks_px.get(self.LEFT_WRIST)
        self.p2_pos = self.right_landmarks_px.get(self.LEFT_WRIST)

        surface = pygame.surfarray.make_surface(np.transpose(rgb, (1, 0, 2)))
        return surface

    def process(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return self.process_frame(frame)

    def draw_skeleton(self, screen):
        """Dibuja el esqueleto sobre la pantalla"""
        for landmarks_px, color in ((self.left_landmarks_px, (0, 255, 150)),
                                    (self.right_landmarks_px, (255, 120, 0))):
            for a, b in self.CONNECTIONS:
                if a in landmarks_px and b in landmarks_px:
                    pygame.draw.line(screen, color,
                                     landmarks_px[a],
                                     landmarks_px[b], 2)

            for pos in landmarks_px.values():
                pygame.draw.circle(screen, (255, 255, 0), pos, 5)

    def get_positions(self):
        return self.p1_pos, self.p2_pos