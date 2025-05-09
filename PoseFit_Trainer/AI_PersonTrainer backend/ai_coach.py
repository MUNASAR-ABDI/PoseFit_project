import cv2
import numpy as np
import mediapipe as mp
from typing import List, Dict, Any

class AICoach:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Define exercise-specific angle thresholds
        self.exercise_thresholds = {
            "pushup": {
                "elbow_angle": {"min": 80, "max": 160},
                "shoulder_angle": {"min": 70, "max": 160}
            },
            "squat": {
                "knee_angle": {"min": 70, "max": 170},
                "hip_angle": {"min": 60, "max": 170}
            }
        }
    
    def calculate_angle(self, a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
        """Calculate the angle between three points."""
        ba = a - b
        bc = c - b
        
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)
        
        return np.degrees(angle)
    
    def get_keypoint_coords(self, keypoints: List[Dict[str, Any]], name: str) -> np.ndarray:
        """Get coordinates for a specific keypoint by name."""
        for kp in keypoints:
            if kp["name"] == name:
                return np.array([kp["x"], kp["y"]])
        return None
    
    def analyze_pose_for_exercise(self, keypoints: List[Dict[str, Any]], exercise_id: str) -> bool:
        """Analyze if a rep is completed based on pose keypoints and exercise type."""
        if exercise_id not in self.exercise_thresholds:
            return False
            
        if exercise_id == "pushup":
            # Get relevant keypoints
            shoulder = self.get_keypoint_coords(keypoints, "RIGHT_SHOULDER")
            elbow = self.get_keypoint_coords(keypoints, "RIGHT_ELBOW")
            wrist = self.get_keypoint_coords(keypoints, "RIGHT_WRIST")
            
            if all(p is not None for p in [shoulder, elbow, wrist]):
                # Calculate elbow angle
                elbow_angle = self.calculate_angle(shoulder, elbow, wrist)
                
                # Check if angle is within pushup range
                thresholds = self.exercise_thresholds["pushup"]["elbow_angle"]
                return thresholds["min"] <= elbow_angle <= thresholds["max"]
                
        elif exercise_id == "squat":
            # Get relevant keypoints
            hip = self.get_keypoint_coords(keypoints, "RIGHT_HIP")
            knee = self.get_keypoint_coords(keypoints, "RIGHT_KNEE")
            ankle = self.get_keypoint_coords(keypoints, "RIGHT_ANKLE")
            
            if all(p is not None for p in [hip, knee, ankle]):
                # Calculate knee angle
                knee_angle = self.calculate_angle(hip, knee, ankle)
                
                # Check if angle is within squat range
                thresholds = self.exercise_thresholds["squat"]["knee_angle"]
                return thresholds["min"] <= knee_angle <= thresholds["max"]
        
        return False
    
    def analyze_workout_video(
        self,
        video_path: str,
        exercise_id: str,
        expected_sets: int,
        expected_reps: int
    ) -> Dict[str, Any]:
        """Analyze a complete workout video and return performance metrics."""
        cap = cv2.VideoCapture(video_path)
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        rep_count = 0
        set_count = 1
        current_set_reps = 0
        
        # Track exercise state
        in_rep = False
        last_rep_frame = 0
        min_frames_between_reps = fps  # Minimum 1 second between reps
        
        try:
            while cap.isOpened():
                success, frame = cap.read()
                if not success:
                    break
                
                # Convert frame to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process frame
                results = self.pose.process(frame_rgb)
                
                if results.pose_landmarks:
                    # Convert landmarks to our keypoint format
                    h, w = frame.shape[:2]
                    keypoints = []
                    for landmark in results.pose_landmarks.landmark:
                        keypoints.append({
                            "x": landmark.x * w,
                            "y": landmark.y * h,
                            "score": landmark.visibility,
                            "name": self.mp_pose.PoseLandmark(len(keypoints)).name
                        })
                    
                    # Check if rep is completed
                    rep_completed = self.analyze_pose_for_exercise(keypoints, exercise_id)
                    
                    current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
                    
                    # State machine for counting reps
                    if rep_completed and not in_rep and \
                       (current_frame - last_rep_frame) > min_frames_between_reps:
                        in_rep = True
                        rep_count += 1
                        current_set_reps += 1
                        last_rep_frame = current_frame
                        
                        # Check if set is complete
                        if current_set_reps >= expected_reps:
                            set_count += 1
                            current_set_reps = 0
                            
                    elif not rep_completed and in_rep:
                        in_rep = False
                        
        finally:
            cap.release()
        
        # Calculate performance metrics
        completion_percentage = min(100, (rep_count / (expected_sets * expected_reps)) * 100)
        
        return {
            "total_reps": rep_count,
            "completed_sets": set_count - 1,
            "completion_percentage": completion_percentage,
            "exercise_id": exercise_id
        }

# Create global instance
ai_coach = AICoach() 