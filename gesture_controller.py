"""
Gesture Recognition Module for Snake Game
Handles stable one-hand index fingertip tracking using MediaPipe
"""

from collections import deque
from typing import Deque, Optional, Tuple

import cv2
import mediapipe as mp
import numpy as np


class GestureController:
    def __init__(self):
        """Initialize MediaPipe hands and the stabilized zone controller."""
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils

        # Keep tracking lightweight for smoother real-time control.
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=0,
            min_detection_confidence=0.65,
            min_tracking_confidence=0.65,
        )

        self.current_direction: Optional[str] = None

        # Average the last few fingertip positions to reduce jitter.
        self.position_history: Deque[np.ndarray] = deque(maxlen=5)

        # A large center dead zone makes controls easier to hold steady.
        self.center_dead_zone = 0.16

        # Ignore tiny position changes to avoid noisy direction updates.
        self.movement_threshold = 0.015
        self.previous_smoothed_tip: Optional[np.ndarray] = None

        # Require a region to remain stable for a few frames before changing.
        self.pending_direction: Optional[str] = None
        self.pending_frames = 0
        self.required_stable_frames = 3

    def detect_gestures(self, frame: np.ndarray) -> Tuple[Optional[str], np.ndarray]:
        """
        Detect the index fingertip position and convert it into a stable direction.

        Returns:
            Tuple of (direction, annotated_frame)
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hand_results = self.hands.process(rgb_frame)
        annotated_frame = frame.copy()

        frame_height, frame_width = frame.shape[:2]
        self._draw_zones(annotated_frame, frame_width, frame_height)

        if hand_results.multi_hand_landmarks:
            hand_landmarks = hand_results.multi_hand_landmarks[0]

            # Draw the hand skeleton lightly for feedback.
            self.mp_drawing.draw_landmarks(
                annotated_frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(70, 180, 110), thickness=1, circle_radius=1),
                self.mp_drawing.DrawingSpec(color=(60, 120, 220), thickness=1),
            )

            index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
            fingertip = np.array([index_tip.x, index_tip.y], dtype=np.float32)
            self.position_history.append(fingertip)
            smoothed_tip = np.mean(self.position_history, axis=0)

            self._draw_fingertip(annotated_frame, smoothed_tip, frame_width, frame_height)
            candidate_direction = self._get_zone_direction(smoothed_tip)
            self._update_stable_direction(smoothed_tip, candidate_direction)
        else:
            self.position_history.clear()
            self.previous_smoothed_tip = None
            self.pending_direction = None
            self.pending_frames = 0

        self._draw_status(annotated_frame)
        return self.current_direction, annotated_frame

    def _get_zone_direction(self, fingertip: np.ndarray) -> Optional[str]:
        """Map the smoothed fingertip into one of four large screen zones."""
        center = np.array([0.5, 0.5], dtype=np.float32)
        offset = fingertip - center

        if np.linalg.norm(offset) < self.center_dead_zone:
            return None

        if abs(offset[0]) > abs(offset[1]):
            return "RIGHT" if offset[0] > 0 else "LEFT"
        return "DOWN" if offset[1] > 0 else "UP"

    def _update_stable_direction(
        self, smoothed_tip: np.ndarray, candidate_direction: Optional[str]
    ):
        """Only accept a direction when the fingertip stays stable in that region."""
        if self.previous_smoothed_tip is not None:
            movement = np.linalg.norm(smoothed_tip - self.previous_smoothed_tip)
            if movement < self.movement_threshold and candidate_direction == self.current_direction:
                self.previous_smoothed_tip = smoothed_tip
                return

        self.previous_smoothed_tip = smoothed_tip

        if candidate_direction is None:
            self.pending_direction = None
            self.pending_frames = 0
            return

        if candidate_direction == self.current_direction:
            self.pending_direction = None
            self.pending_frames = 0
            return

        if candidate_direction != self.pending_direction:
            self.pending_direction = candidate_direction
            self.pending_frames = 1
            return

        self.pending_frames += 1
        if self.pending_frames >= self.required_stable_frames:
            self.current_direction = candidate_direction
            self.pending_direction = None
            self.pending_frames = 0

    def _draw_zones(self, frame: np.ndarray, width: int, height: int):
        """Draw faint directional guides and the center dead zone."""
        center_x = width // 2
        center_y = height // 2
        dead_zone_radius = int(min(width, height) * self.center_dead_zone)

        cv2.line(frame, (0, center_y), (width, center_y), (50, 50, 50), 1)
        cv2.line(frame, (center_x, 0), (center_x, height), (50, 50, 50), 1)
        cv2.circle(frame, (center_x, center_y), dead_zone_radius, (0, 200, 255), 1)

        cv2.putText(frame, "UP", (center_x - 18, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (90, 90, 90), 1)
        cv2.putText(frame, "DOWN", (center_x - 30, height - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (90, 90, 90), 1)
        cv2.putText(frame, "LEFT", (12, center_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (90, 90, 90), 1)
        cv2.putText(frame, "RIGHT", (width - 58, center_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (90, 90, 90), 1)

    def _draw_fingertip(self, frame: np.ndarray, fingertip: np.ndarray, width: int, height: int):
        """Draw the smoothed fingertip position."""
        point = (int(fingertip[0] * width), int(fingertip[1] * height))
        cv2.circle(frame, point, 8, (0, 255, 255), 2)
        cv2.circle(frame, point, 3, (0, 255, 255), -1)

    def _draw_status(self, frame: np.ndarray):
        """Keep the camera view simple and readable."""
        cv2.putText(
            frame,
            f"Direction: {self.current_direction or 'HOLD'}",
            (10, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (240, 240, 240),
            2,
        )

    def reset_gesture_state(self):
        """Reset gesture state when restarting the game."""
        self.position_history.clear()
        self.previous_smoothed_tip = None
        self.pending_direction = None
        self.pending_frames = 0
        self.current_direction = None
