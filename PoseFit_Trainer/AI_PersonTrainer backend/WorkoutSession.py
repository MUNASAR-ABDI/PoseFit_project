import uuid
from datetime import datetime
import cv2
import numpy as np
from typing import Optional, Dict, Any

class WorkoutSession:
    def __init__(self, sets: int, reps: int, camera_index: int, user_profile: dict, exercise_type: str):
        self.id = str(uuid.uuid4())
        self.sets = sets
        self.reps = reps
        self.camera_index = camera_index
        self.user_profile = user_profile
        self.exercise_type = exercise_type.lower().replace("-", "_")
        
        # Performance metrics
        self.current_set = 1
        self.current_rep = 0
        self.total_reps_completed = 0
        self.calories_burned = 0
        self.completion_percentage = 0
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        
        # Exercise module will be set by the AiTrainer
        self.exercise_module = None
        
        # Video stream will be initialized when needed
        self.video_stream = None
        
        # Camera setup
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise ValueError(f"Failed to open camera at index {camera_index}")
            
    def process_frame(self, frame_rgb: np.ndarray, pose_landmarks) -> Dict[str, Any]:
        """
        Process a single frame using the exercise module.
        
        Args:
            frame_rgb (np.ndarray): The RGB frame to process
            pose_landmarks: MediaPipe pose landmarks
            
        Returns:
            Dict[str, Any]: Dictionary containing processing results and metrics
        """
        if self.exercise_module is None:
            raise ValueError("Exercise module not initialized")
            
        # Process the frame using the exercise module
        results = self.exercise_module.process_frame(frame_rgb, pose_landmarks)
        
        # Update session metrics
        self.current_rep = results.get("current_rep", self.current_rep)
        self.total_reps_completed = results.get("total_reps", self.total_reps_completed)
        self.calories_burned = results.get("calories_burned", self.calories_burned)
        
        # Calculate completion percentage
        total_reps_required = self.sets * self.reps
        self.completion_percentage = (self.total_reps_completed / total_reps_required) * 100
        
        return {
            "current_set": self.current_set,
            "current_rep": self.current_rep,
            "total_reps": self.total_reps_completed,
            "calories_burned": self.calories_burned,
            "completion_percentage": self.completion_percentage,
            "exercise_type": self.exercise_type,
            **results  # Include any additional results from the exercise module
        }
        
    def complete_workout(self) -> Dict[str, Any]:
        """
        Complete the workout session and return final metrics.
        
        Returns:
            Dict[str, Any]: Final workout metrics and statistics
        """
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        # Release camera
        if self.cap is not None:
            self.cap.release()
        
        return {
            "session_id": self.id,
            "exercise_type": self.exercise_type,
            "total_sets": self.sets,
            "total_reps": self.total_reps_completed,
            "calories_burned": self.calories_burned,
            "duration_seconds": duration,
            "completion_percentage": self.completion_percentage,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat()
        }
        
    def __del__(self):
        """Cleanup resources when the session is destroyed"""
        if self.video_stream is not None:
            self.video_stream.stop()
        if hasattr(self, 'cap') and self.cap is not None:
            self.cap.release() 