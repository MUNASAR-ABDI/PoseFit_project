from typing import Dict, Any
import numpy as np
import cv2
from .base_exercise import BaseExercise


class SquatExercise(BaseExercise):
    def __init__(self):
        super().__init__()
        self.squat_position = False  # Tracks if user is in squat position
        self.hip_threshold = 0.1  # Threshold for hip position relative to knees
        self.knee_angle_threshold = 100  # Threshold for knee angle in degrees

    def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Process a single frame for squat detection"""
        # Convert the BGR image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame and get pose landmarks
        results = self.pose.process(image)

        if not results.pose_landmarks:
            return {
                "rep_detected": False,
                "metrics": self.get_metrics(),
                "form_feedback": "No pose detected",
            }

        # Draw the pose landmarks on the frame
        self.mp_draw.draw_landmarks(
            frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
        )

        # Check form and detect movement
        self.form_feedback = self.check_form(results.pose_landmarks)
        movement_detected = self.detect_movement(results.pose_landmarks)

        if movement_detected and not self.form_feedback:
            self.current_rep += 1
            self.total_reps += 1
            self.calories_burned = self.calculate_calories()

        return {
            "rep_detected": movement_detected,
            "metrics": self.get_metrics(),
            "form_feedback": self.form_feedback,
        }

    def detect_movement(self, landmarks) -> bool:
        """Detect if a squat movement has been completed"""
        # Get relevant landmarks
        hip = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP]
        knee = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_KNEE]
        ankle = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_ANKLE]

        # Calculate knee angle
        knee_angle = self._calculate_angle(hip, knee, ankle)

        # Check if user is in squat position
        if not self.squat_position and knee_angle < self.knee_angle_threshold:
            self.squat_position = True
            return False

        # Check if user has completed squat
        if self.squat_position and knee_angle > 160:
            self.squat_position = False
            return True

        return False

    def calculate_calories(self) -> float:
        """Calculate calories burned from squats"""
        # Average calories burned per squat (rough estimate)
        calories_per_squat = 0.32
        return self.total_reps * calories_per_squat

    def check_form(self, landmarks) -> str:
        """Check squat form and provide feedback"""
        hip_l = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP]
        hip_r = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_HIP]
        knee_l = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_KNEE]
        knee_r = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_KNEE]
        ankle_l = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_ANKLE]
        ankle_r = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_ANKLE]

        # Check if hips are level
        hip_diff = abs(hip_l.y - hip_r.y)
        if hip_diff > self.hip_threshold:
            return "Keep your hips level"

        # Check if knees are aligned with feet
        knee_ankle_l = abs(knee_l.x - ankle_l.x)
        knee_ankle_r = abs(knee_r.x - ankle_r.x)
        if knee_ankle_l > self.hip_threshold or knee_ankle_r > self.hip_threshold:
            return "Keep your knees aligned with your feet"

        # Check depth
        knee_angle_l = self._calculate_angle(hip_l, knee_l, ankle_l)
        knee_angle_r = self._calculate_angle(hip_r, knee_r, ankle_r)
        if (
            self.squat_position
            and min(knee_angle_l, knee_angle_r) > self.knee_angle_threshold
        ):
            return "Squat deeper"

        return ""

    def _calculate_angle(self, a, b, c) -> float:
        """Calculate angle between three points"""
        a = np.array([a.x, a.y])
        b = np.array([b.x, b.y])
        c = np.array([c.x, c.y])

        ba = a - b
        bc = c - b

        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)

        return np.degrees(angle)
