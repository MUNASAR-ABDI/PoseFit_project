from abc import ABC, abstractmethod
from typing import Dict, Any
import numpy as np
import mediapipe as mp

class BaseExercise(ABC):
    def __init__(self):
        """Initialize MediaPipe pose detection"""
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Exercise state
        self.current_rep = 0
        self.total_reps = 0
        self.calories_burned = 0
        self.form_feedback = ""
        
    @abstractmethod
    def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Process a single frame and detect exercise movement.
        
        Args:
            frame (np.ndarray): The frame to process
            
        Returns:
            Dict[str, Any]: Dictionary containing processing results and metrics
        """
        pass
        
    @abstractmethod
    def detect_movement(self, landmarks) -> bool:
        """
        Detect if the current pose constitutes a valid exercise movement.
        
        Args:
            landmarks: MediaPipe pose landmarks
            
        Returns:
            bool: True if a valid movement is detected
        """
        pass
        
    @abstractmethod
    def calculate_calories(self) -> float:
        """
        Calculate calories burned based on exercise type and reps.
        
        Returns:
            float: Calories burned
        """
        pass
        
    @abstractmethod
    def check_form(self, landmarks) -> str:
        """
        Check if the current pose has correct form.
        
        Args:
            landmarks: MediaPipe pose landmarks
            
        Returns:
            str: Feedback on form, empty string if form is correct
        """
        pass
        
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current exercise metrics.
        
        Returns:
            Dict[str, Any]: Current exercise metrics
        """
        return {
            "current_rep": self.current_rep,
            "total_reps": self.total_reps,
            "calories_burned": self.calories_burned,
            "form_feedback": self.form_feedback
        }
        
    def __del__(self):
        """Clean up MediaPipe resources"""
        if hasattr(self, 'pose'):
            self.pose.close() 