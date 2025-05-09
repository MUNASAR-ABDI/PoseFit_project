import cv2
import mediapipe as mp
import numpy as np
from ExercisesModule import simulate_target_exercies
import argparse

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='AI Personal Trainer')
    parser.add_argument('--exercise', type=str, required=True, help='Exercise name')
    parser.add_argument('--sets', type=int, required=True, help='Number of sets')
    parser.add_argument('--reps', type=int, required=True, help='Number of reps per set')
    parser.add_argument('--user_email', type=str, required=True, help='User email')
    args = parser.parse_args()

    print(f"Starting AI Personal Trainer for {args.exercise}...")
    print(f"Sets: {args.sets}, Reps: {args.reps}")
    print("Press 'q' to quit")
    
    # Initialize MediaPipe
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 980)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 550)
    
    # Initialize exercise module
    exercise = simulate_target_exercies(
        sets=args.sets,
        reps=args.reps
    )
    
    # Call the specific exercise method based on the exercise name
    exercise_method = getattr(exercise, args.exercise, None)
    if not exercise_method:
        print(f"Exercise {args.exercise} not found")
        return
    
    # Start the exercise
    exercise_method()
                
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 