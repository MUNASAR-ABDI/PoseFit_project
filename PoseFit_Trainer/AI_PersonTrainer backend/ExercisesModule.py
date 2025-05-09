import cv2
import numpy as np
import time
import threading
import PoseModule as pm
import queue
from threading import Thread
import VideoRecorder as vr
from datetime import datetime
import os
import uuid
from typing import Dict, Any, Optional
import mediapipe as mp
import base64


# New function for drawing attractive, smaller, and more appealing counter displays
def draw_modern_counter(
    img,
    text,
    position,
    text_color=(255, 255, 255),
    bg_color=(0, 0, 255),
    text_size=0.55,
    text_thickness=2,
):
    """Draw a modern-looking counter with 3D effect and gradient"""
    # Increase padding for bigger counters
    padding_x, padding_y = 12, 8

    # Get text dimensions
    (text_width, text_height), _ = cv2.getTextSize(
        text, cv2.FONT_HERSHEY_SIMPLEX, text_size, text_thickness
    )

    # Calculate rectangle dimensions with more generous spacing
    rect_width = text_width + padding_x * 2
    rect_height = (
        text_height + padding_y * 2 + 2
    )  # Added extra pixels for vertical spacing

    # Calculate rectangle coordinates
    x, y = position
    rect_start = (x, y)
    rect_end = (x + rect_width, y + rect_height)

    # Create a copy of the background region for blending
    roi = img[rect_start[1] : rect_end[1], rect_start[0] : rect_end[0]].copy()

    # Create a gradient background (darker at bottom, lighter at top)
    base_color = np.array(bg_color, dtype=np.float32)
    for i in range(rect_height):
        # Calculate gradient factor (0 at top, 1 at bottom)
        gradient_factor = i / rect_height
        # Darken color for gradient effect (bottom darker)
        gradient_color = np.clip(
            base_color * (0.8 + 0.4 * (1 - gradient_factor)), 0, 255
        ).astype(np.uint8)
        # Draw horizontal line with gradient color
        if i < rect_height and 0 < rect_width - 1:  # Avoid out-of-bounds errors
            cv2.line(
                roi, (0, i), (rect_width - 1, i), tuple(map(int, gradient_color)), 1
            )

    # Create a semi-transparent overlay
    overlay = roi.copy()

    # Draw dark bottom and right edges for 3D effect (shadow)
    dark_color = tuple(map(int, np.clip(np.array(bg_color) * 0.6, 0, 255)))
    cv2.line(
        overlay, (1, rect_height - 1), (rect_width - 2, rect_height - 1), dark_color, 1
    )
    cv2.line(
        overlay, (rect_width - 2, 1), (rect_width - 2, rect_height - 1), dark_color, 1
    )

    # Draw light top and left edges for 3D effect (highlight)
    light_color = tuple(map(int, np.clip(np.array(bg_color) * 1.3, 0, 255)))
    cv2.line(overlay, (1, 1), (rect_width - 2, 1), light_color, 1)
    cv2.line(overlay, (1, 1), (1, rect_height - 1), light_color, 1)

    # Add rounded corners (small radius for compact look)
    radius = 3  # Slightly larger radius
    cv2.circle(overlay, (radius + 1, radius + 1), radius, light_color, 1)  # Top-left
    cv2.circle(
        overlay, (rect_width - radius - 2, radius + 1), radius, light_color, 1
    )  # Top-right
    cv2.circle(
        overlay, (radius + 1, rect_height - radius - 1), radius, dark_color, 1
    )  # Bottom-left
    cv2.circle(
        overlay,
        (rect_width - radius - 2, rect_height - radius - 1),
        radius,
        dark_color,
        1,
    )  # Bottom-right

    # Add thin border
    border_color = tuple(map(int, np.clip(np.array(bg_color) * 0.8, 0, 255)))
    cv2.rectangle(overlay, (0, 0), (rect_width - 1, rect_height - 1), border_color, 1)

    # Blend the overlay with the original ROI
    alpha = 0.97  # Higher opacity for more vivid counters
    cv2.addWeighted(overlay, alpha, roi, 1 - alpha, 0, roi)

    # Put the blended ROI back into the image
    if (
        rect_start[1] + rect_height <= img.shape[0]
        and rect_start[0] + rect_width <= img.shape[1]
    ):
        img[rect_start[1] : rect_end[1], rect_start[0] : rect_end[0]] = roi

    # Calculate text position for perfect centering
    text_x = x + padding_x
    text_y = y + text_height + padding_y - 1  # Better vertical alignment

    # Draw text with slight shadow for better readability
    cv2.putText(
        img,
        text,
        (text_x + 1, text_y + 1),
        cv2.FONT_HERSHEY_SIMPLEX,
        text_size,
        (0, 0, 0),
        text_thickness,
    )
    cv2.putText(
        img,
        text,
        (text_x, text_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        text_size,
        text_color,
        text_thickness,
    )


class VideoStream:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 980)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 550)
        self.stream.set(cv2.CAP_PROP_FPS, 30)
        self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 2)  # Minimize buffer size

        # Initialize the queue to store frames
        self.Q = queue.Queue(maxsize=2)
        self.stopped = False

    def start(self):
        # Start a thread to read frames from the video stream
        Thread(target=self.update, args=(), daemon=True).start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return

            if not self.Q.full():
                grabbed, frame = self.stream.read()
                if not grabbed:
                    self.stop()
                    return

                # Clear queue if it has old frames
                while not self.Q.empty():
                    try:
                        self.Q.get_nowait()
                    except queue.Empty:
                        break

                self.Q.put(frame)

    def read(self):
        return self.Q.get()

    def more(self):
        return self.Q.qsize() > 0

    def stop(self):
        self.stopped = True
        self.stream.release()


class utilities:
    def __init__(self):
        pass

    def illustrate_exercise(self, example, exercise, web_mode=False):
        if web_mode:
            print(f"Web mode: Skipping illustration for {exercise}")
            return
        seconds = 3
        img = cv2.imread(example)
        img = cv2.resize(img, (980, 550))

        # Create the window with a unique name for this exercise
        window_name = "Exercise Illustration"
        if not web_mode:
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

        # Set window to be always on top and in focus
        cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

        # Show first frame
        cv2.imshow(window_name, img)
        cv2.waitKey(1)

        instruction = "Up next is " + exercise + " IN!"
        print(instruction)

        while seconds > 0:
            img = cv2.imread(example)
            img = cv2.resize(img, (980, 550))
            time.sleep(1)
            print(f"Countdown: {int(seconds)}")
            cv2.putText(
                img,
                exercise + " in: " + str(int(seconds)),
                (350, 50),
                cv2.FONT_HERSHEY_PLAIN,
                3,
                (0, 0, 255),
                5,
            )

            # Re-show the image with countdown
            if not web_mode:
                cv2.imshow(window_name, img)

            # Set window as topmost again to ensure focus
            cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

            seconds -= 1
            cv2.waitKey(1)

        # Explicitly close the window before moving on to the exercise
        if not web_mode:
            cv2.destroyWindow(window_name)

    def repitition_counter(self, per, count, direction, arm=None):
        """
        Count exercise repetitions based on movement percentage.

        Args:
            per: Percentage of movement completion (0-100)
            count: Current count value
            direction: Current movement direction (0 = down/extending, 1 = up/curling)
            arm: Optional identifier for the body part (e.g., 'left', 'right')

        Returns:
            Dictionary with updated count and direction values
        """
        # Only count at maximum curl position (85% or higher)
        max_curl_threshold = 85
        min_extend_threshold = 15

        # Direction 0 = extending/down, Direction 1 = curling/up
        if per >= max_curl_threshold and direction == 0:  # Maximum curl position
            count += 0.5
            direction = 1
            if arm:  # Log direction change if specified
                print(f"{arm} curling")

        if per <= min_extend_threshold and direction == 1:  # Full extension position
            count += 0.5
            direction = 0
            if int(count) != 0:  # Only log completed reps
                if arm:
                    print(f"{arm} rep {str(int(count))} completed")
                else:
                    print(f"Count: {str(int(count))}")

        return {"count": count, "direction": direction}

    def display_rep_count(self, img, count, total_reps):
        # Replaced with the new modern counter
        draw_modern_counter(
            img,
            f"{int(count)}/{total_reps}",
            (20, 20),
            text_color=(255, 255, 255),
            bg_color=(0, 0, 200),
        )

    def get_performance_bar_color(self, per):
        """
        Returns a color based on the performance percentage:
        - 0-25%: Red (low performance)
        - 25-50%: Yellow-Orange (moderate performance)
        - 50-75%: Yellow-Green (good performance)
        - 75-100%: Green (excellent performance)
        """
        # Ensure percentage is within bounds
        per = max(0, min(100, per))

        if 0 <= per < 25:
            # Red to Orange gradient
            r = 255
            g = int((per / 25) * 165)
            b = 0
        elif 25 <= per < 50:
            # Orange to Yellow gradient
            r = 255
            g = int(165 + ((per - 25) / 25) * 90)
            b = 0
        elif 50 <= per < 75:
            # Yellow to Yellow-Green gradient
            r = int(255 - ((per - 50) / 25) * 155)
            g = 255
            b = 0
        else:  # 75-100%
            # Yellow-Green to Green gradient
            r = int(100 - ((per - 75) / 25) * 100)
            g = 255
            b = int(((per - 75) / 25) * 100)  # Add slight blue tint at 100%

        return (b, g, r)  # OpenCV uses BGR format

    def draw_performance_bar(self, img, per, bar, color, count, is_left=True):
        """
        Draw a smaller, more aesthetically pleasing performance bar with improved positioning
        """
        # Make bars smaller and positioned better
        bar_width = 20  # Reduced width to 20 pixels

        # Left bar position (40 pixels from left edge)
        left_bar_x = 40
        # Right bar position (40 pixels from right edge)
        right_bar_x = img.shape[1] - 60

        # Set bar position based on which side
        bar_left = left_bar_x if is_left else right_bar_x
        bar_right = bar_left + bar_width

        # Smaller bar height range
        bar_top = 150  # Top position
        bar_bottom = 350  # Bottom position reduced for smaller bar

        # Calculate the fill level based on performance percentage
        bar_fill = np.interp(per, (0, 100), (bar_bottom, bar_top))

        # Draw outer rectangle (border) with gray color
        cv2.rectangle(
            img,
            (bar_left - 1, bar_top - 1),
            (bar_right + 1, bar_bottom + 1),
            (120, 120, 120),
            2,
        )

        # Draw background (unfilled portion) with dark gray
        cv2.rectangle(
            img, (bar_left, bar_top), (bar_right, bar_bottom), (50, 50, 50), cv2.FILLED
        )

        # Draw the filled portion with gradient color
        cv2.rectangle(
            img, (bar_left, int(bar_fill)), (bar_right, bar_bottom), color, cv2.FILLED
        )

        # Add percentage markers
        for i in range(25, 100, 25):
            marker_y = int(np.interp(i, (0, 100), (bar_bottom, bar_top)))
            cv2.line(
                img, (bar_left, marker_y), (bar_left + 5, marker_y), (200, 200, 200), 1
            )

        # Add percentage text at top
        text_x = bar_left - 30 if is_left else bar_right + 5
        cv2.putText(
            img,
            f"{int(per)}%",
            (text_x, bar_top - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            1,
        )


class simulate_target_exercies:
    # Dictionary to store active workout sessions
    _active_sessions = {}

    @classmethod
    def get_workout_session(cls, session_id):
        """Get an active workout session by ID"""
        return cls._active_sessions.get(session_id)

    @classmethod
    def release_all_cameras(cls):
        print("[ExercisesModule] Releasing all cameras for all active sessions...")
        for session_id, session in list(cls._active_sessions.items()):
            try:
                if hasattr(session, "release_camera"):
                    session.release_camera()
                    print(f"[ExercisesModule] Released camera for session {session_id}")
            except Exception as e:
                print(
                    f"[ExercisesModule] Error releasing camera for session {session_id}: {e}"
                )

    def initialize_video_stream(self):
        """Initialize a VideoStream instance for web streaming"""
        # Only initialize if not already done
        try:
            if not hasattr(self, "video_stream") or self.video_stream is None:
                print(
                    f"[ExercisesModule] Initializing new VideoStream for camera {self.camera_index}"
                )
                self.video_stream = VideoStream(self.camera_index)
                self.video_stream.start()
                # Wait briefly to ensure stream is running
                time.sleep(1)
                print(
                    f"[ExercisesModule] VideoStream initialized for camera {self.camera_index}"
                )
            else:
                print(
                    f"[ExercisesModule] Using existing VideoStream for camera {self.camera_index}"
                )

            # Verify stream is working
            if self.video_stream.more():
                test_frame = self.video_stream.read()
                print(
                    f"[ExercisesModule] Successfully read test frame from VideoStream: {test_frame.shape if test_frame is not None else None}"
                )
            else:
                print(f"[ExercisesModule] Warning: VideoStream has no frames available")

            return self.video_stream
        except Exception as e:
            print(f"[ExercisesModule] Error initializing VideoStream: {e}")
            # Fall back to direct camera access if VideoStream fails
            try:
                self.cap = cv2.VideoCapture(self.camera_index)
                ret, test_frame = self.cap.read()
                print(
                    f"[ExercisesModule] Fallback to direct camera access: {ret}, frame shape: {test_frame.shape if ret else None}"
                )
                return None
            except Exception as cap_err:
                print(
                    f"[ExercisesModule] Error with direct camera access too: {cap_err}"
                )
                return None

    def __init__(
        self, sets=1, reps=6, camera_index=0, exercise_type=None, session_id=None
    ):
        print(f"Initializing workout session with exercise: {exercise_type}")
        self.sets = sets
        self.reps = reps
        self.camera_index = camera_index
        self.exercise_type = exercise_type
        self.current_set = 1
        self.target_exercise = None

        # Use provided session ID or generate new one
        if session_id:
            self.session_id = session_id
            print(f"[ExercisesModule] Using provided session ID: {session_id}")
        else:
            import uuid

            self.session_id = str(uuid.uuid4())
            print(f"[ExercisesModule] Generated new session ID: {self.session_id}")

        try:
            import VideoRecorder as vr

            self.video_recorder = vr.VideoRecorder()  # Always create a VideoRecorder
            print(
                f"[ExercisesModule] Successfully initialized VideoRecorder for {exercise_type}"
            )

            # Start recording immediately with session ID
            if self.exercise_type:
                print(
                    f"[ExercisesModule] Starting recording for {self.exercise_type} with session ID {self.session_id}"
                )
                self.video_recorder.start_recording(self.exercise_type, self.session_id)
        except Exception as e:
            print(f"[ExercisesModule] Error initializing VideoRecorder: {e}")
            self.video_recorder = None

        self.user_profile = None
        self.utils = utilities()
        self.stopped = False  # Add stopped flag
        self.workout_complete = False  # Initialize workout_complete flag

        # Flag to control whether to show OpenCV windows or not
        self.web_mode = True  # Set to True for web streaming, False for desktop app

        # Store the last processed frame for web streaming
        self.last_processed_frame = None
        self.frame_lock = threading.Lock()

        # Initialize MediaPipe
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        )

        # Initialize metrics
        self.reps_completed = 0
        self.calories_burned = 0
        self.feedback = "Start exercising!"

        # Start the appropriate exercise based on exercise_type
        if self.exercise_type:
            print(f"Starting exercise: {self.exercise_type}")

            # Map common exercise names to method names
            exercise_method_map = {
                "bicep_curls": "bicep_curls",
                "push_ups": "push_ups",
                "squats": "squats",
                "mountain_climbers": "mountain_climbers",
                # Add any name variants here
            }

            # Look up in the map or use as is
            exercise_method = exercise_method_map.get(
                self.exercise_type, self.exercise_type
            )
            print(f"Using method: {exercise_method}")

            if hasattr(self, exercise_method):
                try:
                    method = getattr(self, exercise_method)
                    if callable(method):
                        # Start in a thread so it doesn't block API responses
                        if self.web_mode:
                            self.exercise_thread = threading.Thread(
                                target=method, daemon=True
                            )
                            self.exercise_thread.start()
                        else:
                            method()
                    else:
                        raise ValueError(
                            f"'{exercise_method}' is not a callable method"
                        )
                except Exception as e:
                    print(f"Error starting exercise {exercise_method}: {str(e)}")
                    print(
                        f"Available methods: {[m for m in dir(self) if not m.startswith('_') and callable(getattr(self, m))]}"
                    )
                    raise ValueError(
                        f"Failed to start exercise {exercise_method}: {str(e)}"
                    )
            else:
                available_methods = [
                    m
                    for m in dir(self)
                    if not m.startswith("_") and callable(getattr(self, m))
                ]
                print(f"Available exercise methods: {available_methods}")
                raise ValueError(
                    f"Exercise type '{exercise_method}' not supported. Available: {available_methods}"
                )

    def process_frame(self, frame_rgb=None):
        """Process a single frame and return metrics"""
        # If in web mode and no frame provided, return the last captured frame
        if self.web_mode and frame_rgb is None:
            with self.frame_lock:
                if self.last_processed_frame is not None:
                    # Encode the frame to base64 for web streaming
                    _, buffer = cv2.imencode(".jpg", self.last_processed_frame)
                    frame_b64 = base64.b64encode(buffer).decode("utf-8")

                    return {
                        "reps_completed": int(self.reps_completed),
                        "count": int(self.reps_completed),  # For frontend compatibility
                        "calories_burned": self.calories_burned,
                        "current_set": self.current_set,
                        "feedback": self.feedback,
                        "processed_image": frame_b64,  # Include the image
                        "workout_complete": self.workout_complete,
                    }

            # If no frame available, return metrics only
            return {
                "reps_completed": int(self.reps_completed),
                "count": int(self.reps_completed),
                "calories_burned": self.calories_burned,
                "current_set": self.current_set,
                "feedback": "Waiting for camera...",
                "workout_complete": self.workout_complete,
            }

        # Process provided frame (for non-web mode or direct frame processing)
        if frame_rgb is not None:
            # Process frame with MediaPipe
            results = self.pose.process(frame_rgb)

            if results.pose_landmarks:
                # Draw pose landmarks
                frame_rgb.flags.writeable = True
                self.mp_drawing.draw_landmarks(
                    frame_rgb,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style(),
                )

                # Update metrics (simplified for example)
                if self.reps_completed < self.sets * self.reps:
                    self.reps_completed += 0.1  # Increment for testing
                    self.calories_burned += 0.05

        return {
            "reps_completed": int(self.reps_completed),
            "count": int(self.reps_completed),
            "calories_burned": self.calories_burned,
            "current_set": self.current_set,
            "feedback": self.feedback,
            "workout_complete": self.workout_complete,
        }

    def get_metrics(self):
        """Get current workout metrics"""
        return {
            "reps_completed": self.reps_completed,
            "calories_burned": self.calories_burned,
            "completion_percentage": (self.reps_completed / (self.sets * self.reps))
            * 100,
            "feedback": self.feedback,
        }

    def get_feedback(self):
        """Get feedback on form and performance"""
        return "Keep going! Maintain proper form."

    def warmup(self):
        try:
            self.utils.illustrate_exercise(
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "TrainerImages",
                    "skip_illustration.jpeg",
                ),
                "WARM UP",
                web_mode=self.web_mode,
            )
            detector = pm.posture_detector()
            # Use reps directly without difficulty_level multiplier
            total_reps = self.reps

            # Initialize camera with proper error handling
            cap = cv2.VideoCapture(self.camera_index)
            self.cap = cap  # Store reference for external release
            if not cap.isOpened():
                print(f"[ERROR] Camera {self.camera_index} could not be opened.")
                print("Camera error. Please try another camera.")
                return {"calories": 0, "time_elapsed": 0}

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 980)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 550)
            start_time = time.process_time()

            # Initialize video recording if enabled
            if hasattr(self, "video_recorder") and self.video_recorder is not None:
                self.video_recorder.start_recording("Warm Up")

            window_name = "Warm Up"
            if not self.web_mode:
                cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

            # Variables to track detection quality
            stable_detection_frames = 0
            required_stable_frames = 20
            detection_ready = False
            min_landmarks_required = 15

            # Required landmarks for warmup
            required_landmarks = [0, 2, 5, 11, 12, 13, 14, 15, 16]

            exit_exercise = False
            self.current_set = 1

            while (
                self.current_set <= self.sets and not exit_exercise and not self.stopped
            ):
                print(f"Starting Set {self.current_set} of {self.sets}")

                # Initialize counters
                count = 0
                direction = 0
                last_count_update = 0
                MIN_TIME_BETWEEN_COUNTS = 0.5  # Minimum seconds between counts

                # Initialize completion percentage
                completion_pct = 0

                # Loop for one set
                while count < total_reps and not exit_exercise and not self.stopped:
                    success, img = cap.read()
                    if not success or img is None:
                        print("Failed to read from camera")
                        continue

                    img = cv2.resize(img, (980, 550))
                    img = cv2.flip(img, 1)
                    img = detector.find_person(img, draw=False)
                    landmark_list = detector.find_landmarks(img, False)

                    if landmark_list and len(landmark_list) >= min_landmarks_required:
                        # Check if required landmarks are visible
                        all_required_visible = True
                        face_visible = True
                        arms_visible = True
                        missing_parts = []

                        # Check face visibility (most important)
                        for landmark_id in [0, 2, 5]:  # Core face landmarks
                            visibility = detector.get_landmark_visibility(landmark_id)
                            if visibility < 0.7:  # Require high visibility threshold
                                face_visible = False
                                missing_parts.append("face")
                                break

                        # Check arms visibility (critical for warmup)
                        for landmark_id in [11, 12, 13, 14, 15, 16]:
                            visibility = detector.get_landmark_visibility(landmark_id)
                            if visibility < 0.6:  # Slightly lower threshold for arms
                                arms_visible = False
                                missing_parts.append("arms")
                                break

                        # We need both face and arms visible
                        all_required_visible = face_visible and arms_visible

                        if all_required_visible:
                            if not detection_ready:
                                stable_detection_frames += 1
                                if stable_detection_frames >= required_stable_frames:
                                    detection_ready = True
                                    print(
                                        "Detection stable - counting Warm Up exercises"
                                    )

                            # Only calculate angles if detection is ready
                            if detection_ready:
                                try:
                                    # Visualize arm joints for better user feedback
                                    left_shoulder = (
                                        landmark_list[11][1],
                                        landmark_list[11][2],
                                    )
                                    left_elbow = (
                                        landmark_list[13][1],
                                        landmark_list[13][2],
                                    )
                                    left_wrist = (
                                        landmark_list[15][1],
                                        landmark_list[15][2],
                                    )

                                    # Draw circles at joints for better visibility
                                    elbow_color = (255, 200, 0)  # Cyan/teal color
                                    cv2.circle(img, left_elbow, 7, elbow_color, -1)

                                    # Draw lines connecting joints
                                    line_color = (0, 255, 255)  # Yellow color
                                    cv2.line(
                                        img, left_shoulder, left_elbow, line_color, 2
                                    )
                                    cv2.line(img, left_elbow, left_wrist, line_color, 2)

                                    # Calculate angle
                                    angle = detector.find_angle(img, 11, 13, 15)
                                    print(f"Warm Up Angle: {angle:.1f}°")

                                    # 0% when arm is straight, 100% when fully bent
                                    per = np.interp(angle, (160, 120), (0, 100))
                                    bar = np.interp(angle, (160, 120), (650, 100))

                                    print(f"Warm Up Percentage: {per:.1f}%")

                                    # Get current time for rep counting
                                    current_time = time.time()

                                    # Set color based on current arm position
                                    color = utilities().get_performance_bar_color(per)

                                    # Count reps with minimum time between counts
                                    if (per >= 85 or per <= 15) and (
                                        current_time - last_count_update
                                    ) >= MIN_TIME_BETWEEN_COUNTS:
                                        color = (0, 255, 0)  # Green at counting points

                                        # Show visual feedback at maximum curl
                                        if per >= 85:
                                            cv2.putText(
                                                img,
                                                "ARM BENT!",
                                                (img.shape[1] // 2 - 150, 200),
                                                cv2.FONT_HERSHEY_SIMPLEX,
                                                0.8,
                                                (0, 255, 0),
                                                2,
                                            )
                                            print("ARM CURL DETECTED!")
                                        elif per <= 15:
                                            cv2.putText(
                                                img,
                                                "ARM STRAIGHT!",
                                                (img.shape[1] // 2 - 150, 200),
                                                cv2.FONT_HERSHEY_SIMPLEX,
                                                0.8,
                                                (0, 255, 0),
                                                2,
                                            )
                                            print("ARM EXTENSION DETECTED!")

                                        # Update count using the repitition counter
                                        result = utilities().repitition_counter(
                                            per, count, direction
                                        )
                                        if (
                                            result["count"] != count
                                        ):  # Only update timestamp if count changed
                                            last_count_update = current_time
                                        count = result["count"]
                                        direction = result["direction"]

                                    # Calculate overall performance based on rep completion
                                    completion_pct = min(
                                        100, (count / total_reps) * 100
                                    )

                                    # Draw performance bars and indicators
                                    utilities().draw_performance_bar(
                                        img, per, bar, color, count
                                    )

                                    # Draw overall performance based on rep completion
                                    cv2.rectangle(
                                        img,
                                        (img.shape[1] // 2 - 150, 20),
                                        (img.shape[1] // 2 + 150, 40),
                                        (50, 50, 50),
                                        cv2.FILLED,
                                    )
                                    cv2.rectangle(
                                        img,
                                        (img.shape[1] // 2 - 150, 20),
                                        (
                                            int(
                                                img.shape[1] // 2
                                                - 150
                                                + completion_pct * 3
                                            ),
                                            40,
                                        ),
                                        (0, 255, 0),
                                        cv2.FILLED,
                                    )
                                    cv2.putText(
                                        img,
                                        f"Performance: {int(completion_pct)}%",
                                        (img.shape[1] // 2 - 145, 35),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        0.5,
                                        (255, 255, 255),
                                        1,
                                    )

                                    # Update metrics for web mode
                                    self.reps_completed = count
                                    self.calories_burned = (
                                        count * 0.5
                                    )  # Simple calorie calculation
                                    self.feedback = "Good form! Keep going!"
                                except Exception as e:
                                    print(f"Error calculating angle: {e}")
                        else:
                            # Some required landmarks are not visible
                            if stable_detection_frames > 0:
                                stable_detection_frames = max(
                                    0, stable_detection_frames - 2
                                )

                            # If we were already counting but lost detection, reset detection status
                            if detection_ready:
                                if not face_visible:
                                    detection_ready = False
                                    print("Lost face tracking - pausing rep counting")
                                elif not arms_visible:
                                    detection_ready = False
                                    print("Lost arms tracking - pausing rep counting")

                            # Display missing body parts with clear instructions
                            if missing_parts:
                                # Remove duplicates and format nicely
                                missing_parts = list(set(missing_parts))
                                missing_text = f"Please position your {' and '.join(missing_parts)} in frame"
                                cv2.putText(
                                    img,
                                    missing_text,
                                    (img.shape[1] // 2 - 200, 70),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.7,
                                    (0, 0, 255),
                                    2,
                                )
                    else:
                        # Reset stable detection counter if we lose tracking
                        if stable_detection_frames > 0:
                            stable_detection_frames = max(
                                0, stable_detection_frames - 2
                            )
                        if detection_ready:
                            # If we were counting but completely lost detection, pause counting
                            detection_ready = False
                            print("Lost body tracking - pausing rep counting")

                        # Display guidance to get back in frame
                        cv2.putText(
                            img,
                            "Please position yourself in frame",
                            (img.shape[1] // 2 - 200, 70),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 0, 255),
                            2,
                        )

                    # Display set and rep counters with modern counters
                    draw_modern_counter(
                        img,
                        f"Set {self.current_set}/{self.sets}",
                        (10, 10),
                        text_color=(255, 255, 255),
                        bg_color=(90, 60, 40),
                    )
                    draw_modern_counter(
                        img,
                        f"Rep {int(count)}/{total_reps}",
                        (10, 55),
                        text_color=(255, 255, 255),
                        bg_color=(100, 170, 85),
                    )

                    # Display detection status message
                    if not detection_ready:
                        status_msg = f"Position your body in frame... ({stable_detection_frames}/{required_stable_frames})"
                        cv2.putText(
                            img,
                            status_msg,
                            (img.shape[1] // 2 - 200, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 0, 255),
                            2,
                        )

                    # Add text to inform user they can press 'q' to exit
                    cv2.putText(
                        img,
                        "Press 'q' to exit exercise",
                        (img.shape[1] - 230, img.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 255),
                        2,
                    )

                    # Now write the processed frame to the video recorder
                    if (
                        hasattr(self, "video_recorder")
                        and self.video_recorder is not None
                    ):
                        try:
                            # Add a frame counter to track recording progress
                            if not hasattr(self, "frames_sent_to_recorder"):
                                self.frames_sent_to_recorder = 0
                            self.frames_sent_to_recorder += 1

                            # Log every 100 frames (about 3-4 seconds at 30fps)
                            if self.frames_sent_to_recorder % 100 == 0:
                                print(
                                    f"[ExercisesModule] Sent {self.frames_sent_to_recorder} frames to video recorder"
                                )

                            # Make a copy of the frame to avoid modification issues
                            img_to_record = img.copy()
                            self.video_recorder.write_frame(img_to_record)
                        except Exception as e:
                            print(
                                f"[ExercisesModule] Error sending frame to video recorder: {e}"
                            )

                    # Store the processed frame for web streaming
                    if self.web_mode:
                        with self.frame_lock:
                            self.last_processed_frame = img.copy()

                    # Display image in desktop mode
                    if not self.web_mode:
                        cv2.imshow(window_name, img)
                        if cv2.waitKey(1) & 0xFF == ord("q"):
                            print("Exercise exited by user")
                            exit_exercise = True
                            break
                    else:
                        time.sleep(0.01)  # Small delay in web mode

                # If user wants to exit, break the outer loop too
                if exit_exercise:
                    break

                # Increment set counter after completing a set
                if count >= total_reps:
                    print(f"Completed Set {self.current_set}")
                    self.current_set += 1

                    # Give a short break between sets if not the last set
                    if self.current_set <= self.sets:
                        print(f"Take a short break before Set {self.current_set}")
                        break_timer = 10  # 10 second break
                        while (
                            break_timer > 0 and not exit_exercise and not self.stopped
                        ):
                            success, img = cap.read()
                            if success:
                                img = cv2.resize(img, (980, 550))
                                img = cv2.flip(img, 1)
                                # More appealing break timer display
                                draw_modern_counter(
                                    img,
                                    f"Break: {break_timer} sec",
                                    (img.shape[1] // 2 - 80, img.shape[0] // 2 - 20),
                                    text_color=(255, 255, 255),
                                    bg_color=(110, 190, 95),
                                    text_size=1.0,
                                )

                                # Add text to inform user they can press 'q' to exit
                                cv2.putText(
                                    img,
                                    "Press 'q' to exit exercise",
                                    (img.shape[1] - 230, img.shape[0] - 20),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.6,
                                    (255, 255, 255),
                                    2,
                                )

                                if not self.web_mode:
                                    cv2.imshow(window_name, img)
                                    if cv2.waitKey(1000) & 0xFF == ord("q"):
                                        print("Exercise exited by user during break.")
                                        exit_exercise = True
                                        break
                                else:
                                    # Store the frame for web streaming and add delay
                                    with self.frame_lock:
                                        self.last_processed_frame = img.copy()
                                    time.sleep(1.0)

                                break_timer -= 1
                            else:
                                break

            # Cleanup
            cap.release()
            self.cap = None
            if not self.web_mode:
                cv2.destroyAllWindows()

            # Calculate final metrics
            end_time = time.process_time()
            time_elapsed = end_time - start_time
            calories_burned = int(
                (time_elapsed / 60) * 8.5
            )  # Approx calories/min for warmup

            if self.current_set > self.sets:
                self.workout_complete = True

            return {
                "calories": calories_burned,
                "time_elapsed": time_elapsed,
                "reps_completed": int(count),
                "total_reps": total_reps * self.sets,
                "sets_completed": self.current_set - 1,
                "exited_early": exit_exercise,
                "workout_complete": self.workout_complete,
            }
        except Exception as e:
            print(f"Error in warmup exercise: {str(e)}")
            import traceback

            traceback.print_exc()
            # Ensure proper cleanup on error
            if hasattr(self, "cap") and self.cap is not None:
                self.cap.release()
                self.cap = None
            if (
                not self.web_mode
                and "window_name" in locals()
                and cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) >= 1
            ):
                cv2.destroyAllWindows()
            return {"calories": 0, "time_elapsed": 0, "error": str(e)}

    def check_body_in_frame(self, landmarks):
        """Check if key body parts are visible in the frame"""
        required_points = [
            0,  # nose
            11,  # left shoulder
            12,  # right shoulder
            15,  # left wrist
            16,  # right wrist
        ]

        for point in required_points:
            if (
                point >= len(landmarks) or landmarks[point][4] < 0.5
            ):  # visibility threshold
                return False
        return True

    def detect_significant_movement(self, prev_positions, current_positions):
        """Detect if there's significant movement between frames"""
        if len(prev_positions) != len(current_positions):
            return False

        for i in range(len(prev_positions)):
            # Calculate distance between previous and current position
            prev_x, prev_y = prev_positions[i]
            curr_x, curr_y = current_positions[i]

            distance = ((curr_x - prev_x) ** 2 + (curr_y - prev_y) ** 2) ** 0.5

            # If any point has moved significantly
            if distance > 20:  # threshold for movement detection
                return True

        return False

    def analyze_form_with_profile(self, detector, img, exercise_name):
        """Analyze exercise form using user profile data if available"""
        if hasattr(detector, "find_person"):
            img = detector.find_person(img, draw=False)

            if detector.results and detector.results.pose_landmarks:
                # If user profile available, pass to AIWorkoutCoach for enhanced analysis
                if hasattr(self, "user_profile") and self.user_profile:
                    # Import AIWorkoutCoach to use form analysis
                    import AIWorkoutCoach as ai_coach

                    coach = ai_coach.AIWorkoutCoach()

                    # Use the enhanced form analysis with user profile
                    detected_issues = coach.analyze_form(
                        detector.results.pose_landmarks,
                        exercise_name,
                        self.user_profile,
                    )

                    # If issues detected, display them
                    if detected_issues:
                        for issue in detected_issues:
                            print(f"Form issue detected: {issue}")

                        # Get a personalized tip based on the detected issues
                        form_tip = coach.get_exercise_tip(
                            detected_issues, self.user_profile
                        )
                        if form_tip:
                            print(form_tip)

        return img

    def push_ups(self):
        try:
            self.utils.illustrate_exercise(
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "TrainerImages",
                    "push_up_illustration.jpeg",
                ),
                "PUSH UPS",
                web_mode=self.web_mode,
            )
            detector = pm.posture_detector()
            # Use reps directly without difficulty_level multiplier
            total_reps = self.reps

            # Initialize camera with proper error handling
            cap = cv2.VideoCapture(self.camera_index)
            self.cap = cap  # Store reference for external release
            if not cap.isOpened():
                print(f"[ERROR] Camera {self.camera_index} could not be opened.")
                print("Camera error. Please try another camera.")
                return {"calories": 0, "time_elapsed": 0}

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 980)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 550)
            start_time = time.process_time()

            # Initialize video recording if enabled
            if hasattr(self, "video_recorder") and self.video_recorder is not None:
                self.video_recorder.start_recording("Push Ups")

            window_name = "Push Ups"
            if not self.web_mode:
                cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

            # Variables to track detection quality
            stable_detection_frames = 0
            required_stable_frames = 20
            detection_ready = False
            min_landmarks_required = 15

            # Required landmarks for push-ups (face and upper body)
            required_landmarks = [0, 2, 5, 11, 12, 13, 14, 15, 16]

            # Body part groups for better feedback
            body_part_groups = {
                "face": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "arms": [11, 12, 13, 14, 15, 16],
                "torso": [11, 12, 23, 24],
            }

            exit_exercise = False
            self.current_set = 1

            while (
                self.current_set <= self.sets and not exit_exercise and not self.stopped
            ):
                print(f"Starting Set {self.current_set} of {self.sets}")

                # Initialize counters
                count = 0
                direction = 0
                last_count_update = 0
                MIN_TIME_BETWEEN_COUNTS = 0.5  # Minimum seconds between counts

                # Initialize completion percentage
                completion_pct = 0

                # Loop for one set
                while count < total_reps and not exit_exercise and not self.stopped:
                    success, img = cap.read()
                    if not success or img is None:
                        print("Failed to read from camera")
                        continue

                    img = cv2.resize(img, (980, 550))
                    img = cv2.flip(img, 1)
                    img = detector.find_person(img, draw=False)
                    landmark_list = detector.find_landmarks(img, False)

                    if landmark_list and len(landmark_list) >= min_landmarks_required:
                        # Check if required landmarks are visible
                        all_required_visible = True
                        face_visible = True
                        left_arm_visible = True
                        right_arm_visible = True
                        missing_parts = []

                        # Check face visibility (most important)
                        for landmark_id in [0, 2, 5]:  # Core face landmarks
                            visibility = detector.get_landmark_visibility(landmark_id)
                            if visibility < 0.7:  # Require high visibility threshold
                                face_visible = False
                                missing_parts.append("face")
                                break

                        # Check left arm landmarks [11, 13, 15]
                        left_arm_count = 0
                        for landmark_id in [11, 13, 15]:
                            visibility = detector.get_landmark_visibility(landmark_id)
                            if visibility >= 0.6:  # Slightly lower threshold for arms
                                left_arm_count += 1
                        left_arm_visible = left_arm_count >= 2  # Need at least 2 points

                        # Check right arm landmarks [12, 14, 16]
                        right_arm_count = 0
                        for landmark_id in [12, 14, 16]:
                            visibility = detector.get_landmark_visibility(landmark_id)
                            if visibility >= 0.6:  # Slightly lower threshold for arms
                                right_arm_count += 1
                        right_arm_visible = (
                            right_arm_count >= 2
                        )  # Need at least 2 points

                        # We need face and at least one arm visible
                        all_required_visible = face_visible and (
                            left_arm_visible or right_arm_visible
                        )

                        # Add missing parts for feedback
                        if not face_visible:
                            missing_parts.append("face")
                        if not left_arm_visible and not right_arm_visible:
                            missing_parts.append("at least one arm")

                        if all_required_visible:
                            if not detection_ready:
                                stable_detection_frames += 1
                                if stable_detection_frames >= required_stable_frames:
                                    detection_ready = True
                                    print("Detection stable - counting Push Ups")

                            # Only calculate angles if detection is ready
                            if detection_ready:
                                try:
                                    # Get visibility scores for both sides
                                    left_vis = (
                                        detector.get_landmark_visibility(11)
                                        + detector.get_landmark_visibility(13)
                                        + detector.get_landmark_visibility(15)
                                    )
                                    right_vis = (
                                        detector.get_landmark_visibility(12)
                                        + detector.get_landmark_visibility(14)
                                        + detector.get_landmark_visibility(16)
                                    )

                                    # Determine which side is more visible
                                    use_left_side = left_vis > right_vis
                                    side_name = "left" if use_left_side else "right"

                                    # Visualize arm joints for better user feedback
                                    if use_left_side and left_arm_visible:
                                        shoulder = (
                                            landmark_list[11][1],
                                            landmark_list[11][2],
                                        )
                                        elbow = (
                                            landmark_list[13][1],
                                            landmark_list[13][2],
                                        )
                                        wrist = (
                                            landmark_list[15][1],
                                            landmark_list[15][2],
                                        )
                                    elif right_arm_visible:
                                        shoulder = (
                                            landmark_list[12][1],
                                            landmark_list[12][2],
                                        )
                                        elbow = (
                                            landmark_list[14][1],
                                            landmark_list[14][2],
                                        )
                                        wrist = (
                                            landmark_list[16][1],
                                            landmark_list[16][2],
                                        )
                                    else:
                                        # If no arm is fully visible but we have some landmarks,
                                        # use whatever landmarks we have from the more visible arm
                                        if use_left_side:
                                            # Try to use left arm with whatever landmarks are available
                                            if (
                                                detector.get_landmark_visibility(11)
                                                > 0.5
                                                and detector.get_landmark_visibility(13)
                                                > 0.5
                                            ):
                                                shoulder = (
                                                    landmark_list[11][1],
                                                    landmark_list[11][2],
                                                )
                                                elbow = (
                                                    landmark_list[13][1],
                                                    landmark_list[13][2],
                                                )
                                                # If wrist not visible, estimate its position
                                                if (
                                                    detector.get_landmark_visibility(15)
                                                    > 0.5
                                                ):
                                                    wrist = (
                                                        landmark_list[15][1],
                                                        landmark_list[15][2],
                                                    )
                                                else:
                                                    # Estimate wrist position based on elbow
                                                    dx = elbow[0] - shoulder[0]
                                                    dy = elbow[1] - shoulder[1]
                                                    wrist = (
                                                        int(elbow[0] + dx * 0.8),
                                                        int(elbow[1] + dy * 0.8),
                                                    )
                                            else:
                                                raise ValueError(
                                                    "Not enough landmarks for angle calculation"
                                                )
                                        else:
                                            # Try to use right arm with whatever landmarks are available
                                            if (
                                                detector.get_landmark_visibility(12)
                                                > 0.5
                                                and detector.get_landmark_visibility(14)
                                                > 0.5
                                            ):
                                                shoulder = (
                                                    landmark_list[12][1],
                                                    landmark_list[12][2],
                                                )
                                                elbow = (
                                                    landmark_list[14][1],
                                                    landmark_list[14][2],
                                                )
                                                # If wrist not visible, estimate its position
                                                if (
                                                    detector.get_landmark_visibility(16)
                                                    > 0.5
                                                ):
                                                    wrist = (
                                                        landmark_list[16][1],
                                                        landmark_list[16][2],
                                                    )
                                                else:
                                                    # Estimate wrist position based on elbow
                                                    dx = elbow[0] - shoulder[0]
                                                    dy = elbow[1] - shoulder[1]
                                                    wrist = (
                                                        int(elbow[0] + dx * 0.8),
                                                        int(elbow[1] + dy * 0.8),
                                                    )
                                            else:
                                                raise ValueError(
                                                    "Not enough landmarks for angle calculation"
                                                )

                                    # Draw circles at joints for better visibility
                                    elbow_color = (255, 200, 0)  # Cyan/teal color
                                    cv2.circle(img, elbow, 7, elbow_color, -1)

                                    # Draw lines connecting joints
                                    line_color = (0, 255, 255)  # Yellow color
                                    cv2.line(img, shoulder, elbow, line_color, 2)
                                    cv2.line(img, elbow, wrist, line_color, 2)

                                    # Calculate angle with explicit error handling
                                    try:
                                        # Instead of using find_angle directly, which requires all landmarks,
                                        # we'll calculate the angle using the points we have or estimated
                                        # Calculate vectors
                                        v1 = np.array(shoulder) - np.array(elbow)
                                        v2 = np.array(wrist) - np.array(elbow)

                                        # Calculate angle
                                        cosine_angle = np.dot(v1, v2) / (
                                            np.linalg.norm(v1) * np.linalg.norm(v2)
                                        )
                                        angle = np.degrees(
                                            np.arccos(np.clip(cosine_angle, -1.0, 1.0))
                                        )

                                        # Optional: Draw the angle on the image
                                        cv2.putText(
                                            img,
                                            f"{int(angle)}°",
                                            elbow,
                                            cv2.FONT_HERSHEY_SIMPLEX,
                                            0.5,
                                            (255, 255, 255),
                                            1,
                                        )

                                        print(
                                            f"Push-up Angle ({side_name}): {angle:.1f}°"
                                        )

                                        # Push-up angle ranges: ~160-170 at top, ~70-80 at bottom
                                        # 0% when arms straight (top position), 100% when fully bent (bottom position)
                                        per = np.interp(angle, (170, 70), (0, 100))
                                        bar = np.interp(angle, (170, 70), (650, 100))

                                        print(f"Push-up Percentage: {per:.1f}%")

                                        # Get current time for rep counting
                                        current_time = time.time()

                                        # Set color based on current push-up position
                                        color = utilities().get_performance_bar_color(
                                            per
                                        )

                                        # Count reps with minimum time between counts
                                        if (per >= 85 or per <= 15) and (
                                            current_time - last_count_update
                                        ) >= MIN_TIME_BETWEEN_COUNTS:
                                            color = (
                                                0,
                                                255,
                                                0,
                                            )  # Green at counting points

                                            # Show visual feedback at maximum depth
                                            if per >= 85:
                                                cv2.putText(
                                                    img,
                                                    "PUSH-UP DOWN!",
                                                    (img.shape[1] // 2 - 150, 200),
                                                    cv2.FONT_HERSHEY_SIMPLEX,
                                                    0.8,
                                                    (0, 255, 0),
                                                    2,
                                                )
                                                print(
                                                    "PUSH-UP BOTTOM POSITION DETECTED!"
                                                )
                                            elif per <= 15:
                                                cv2.putText(
                                                    img,
                                                    "PUSH-UP UP!",
                                                    (img.shape[1] // 2 - 150, 200),
                                                    cv2.FONT_HERSHEY_SIMPLEX,
                                                    0.8,
                                                    (0, 255, 0),
                                                    2,
                                                )
                                                print("PUSH-UP TOP POSITION DETECTED!")

                                            # Update count using the repitition counter
                                            result = utilities().repitition_counter(
                                                per, count, direction
                                            )
                                            if (
                                                result["count"] != count
                                            ):  # Only update timestamp if count changed
                                                last_count_update = current_time
                                            count = result["count"]
                                            direction = result["direction"]

                                        # Calculate overall performance based on rep completion
                                        completion_pct = min(
                                            100, (count / total_reps) * 100
                                        )

                                        # Draw performance bars and indicators
                                        utilities().draw_performance_bar(
                                            img,
                                            completion_pct,
                                            bar,
                                            color,
                                            count,
                                            is_left=use_left_side,
                                        )

                                        # Draw overall performance based on rep completion
                                        cv2.rectangle(
                                            img,
                                            (img.shape[1] // 2 - 150, 20),
                                            (img.shape[1] // 2 + 150, 40),
                                            (50, 50, 50),
                                            cv2.FILLED,
                                        )
                                        cv2.rectangle(
                                            img,
                                            (img.shape[1] // 2 - 150, 20),
                                            (
                                                int(
                                                    img.shape[1] // 2
                                                    - 150
                                                    + completion_pct * 3
                                                ),
                                                40,
                                            ),
                                            (0, 255, 0),
                                            cv2.FILLED,
                                        )
                                        cv2.putText(
                                            img,
                                            f"Performance: {int(completion_pct)}%",
                                            (img.shape[1] // 2 - 145, 35),
                                            cv2.FONT_HERSHEY_SIMPLEX,
                                            0.5,
                                            (255, 255, 255),
                                            1,
                                        )

                                        # Update metrics for web mode
                                        self.current_set = self.current_set
                                        self.reps_completed = count
                                        self.calories_burned = (
                                            count * 0.6
                                        )  # Simple calorie calculation
                                        self.feedback = "Good form! Keep going!"

                                        # Add form guidance based on angle
                                        if 30 <= per <= 70:  # Mid-range position
                                            cv2.putText(
                                                img,
                                                "Keep your back straight",
                                                (img.shape[1] // 2 - 150, 240),
                                                cv2.FONT_HERSHEY_SIMPLEX,
                                                0.7,
                                                (0, 200, 200),
                                                2,
                                            )
                                    except Exception as e:
                                        print(f"Error calculating angle: {e}")
                                except Exception as e:
                                    print(f"Error in push-up tracking: {e}")
                        else:
                            # Some required landmarks are not visible
                            if stable_detection_frames > 0:
                                stable_detection_frames = max(
                                    0, stable_detection_frames - 2
                                )

                            # If we were already counting but lost detection, reset detection status
                            if detection_ready:
                                if not face_visible:
                                    detection_ready = False
                                    print("Lost face tracking - pausing rep counting")
                                elif not left_arm_visible and not right_arm_visible:
                                    detection_ready = False
                                    print(
                                        "Lost both arms tracking - pausing rep counting"
                                    )
                                    # We only need one arm, but both are missing
                                    missing_parts = ["at least one arm"]

                            # Display missing body parts with clear instructions
                            if missing_parts:
                                # Remove duplicates and format nicely
                                missing_parts = list(set(missing_parts))
                                missing_text = f"Please position your {' and '.join(missing_parts)} in frame"
                                cv2.putText(
                                    img,
                                    missing_text,
                                    (img.shape[1] // 2 - 200, 70),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.7,
                                    (0, 0, 255),
                                    2,
                                )
                    else:
                        # Reset stable detection counter if we lose tracking
                        if stable_detection_frames > 0:
                            stable_detection_frames = max(
                                0, stable_detection_frames - 2
                            )
                        if detection_ready:
                            # If we were counting but completely lost detection, pause counting
                            detection_ready = False
                            print("Lost body tracking - pausing rep counting")

                        # Display guidance to get back in frame
                        cv2.putText(
                            img,
                            "Please position yourself in frame",
                            (img.shape[1] // 2 - 200, 70),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 0, 255),
                            2,
                        )

                    # Display set and rep counters with modern counters
                    draw_modern_counter(
                        img,
                        f"Set {self.current_set}/{self.sets}",
                        (10, 10),
                        text_color=(255, 255, 255),
                        bg_color=(90, 60, 40),
                    )
                    draw_modern_counter(
                        img,
                        f"Rep {int(count)}/{total_reps}",
                        (10, 55),
                        text_color=(255, 255, 255),
                        bg_color=(100, 170, 85),
                    )

                    # Display detection status message
                    if not detection_ready:
                        status_msg = f"Position your body in frame... ({stable_detection_frames}/{required_stable_frames})"
                        cv2.putText(
                            img,
                            status_msg,
                            (img.shape[1] // 2 - 200, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 0, 255),
                            2,
                        )

                    # Add text to inform user they can press 'q' to exit
                    cv2.putText(
                        img,
                        "Press 'q' to exit exercise",
                        (img.shape[1] - 230, img.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 255),
                        2,
                    )

                    # Now write the processed frame to the video recorder
                    if (
                        hasattr(self, "video_recorder")
                        and self.video_recorder is not None
                    ):
                        try:
                            # Add a frame counter to track recording progress
                            if not hasattr(self, "frames_sent_to_recorder"):
                                self.frames_sent_to_recorder = 0
                            self.frames_sent_to_recorder += 1

                            # Log every 100 frames (about 3-4 seconds at 30fps)
                            if self.frames_sent_to_recorder % 100 == 0:
                                print(
                                    f"[ExercisesModule] Sent {self.frames_sent_to_recorder} frames to video recorder"
                                )

                            # Make a copy of the frame to avoid modification issues
                            img_to_record = img.copy()
                            self.video_recorder.write_frame(img_to_record)
                        except Exception as e:
                            print(
                                f"[ExercisesModule] Error sending frame to video recorder: {e}"
                            )

                    # Store the processed frame for web streaming
                    with self.frame_lock:
                        self.last_processed_frame = img.copy()

                    # Display image in desktop mode
                    if not self.web_mode:
                        cv2.imshow(window_name, img)
                        if cv2.waitKey(1) & 0xFF == ord("q"):
                            print("Exercise exited by user")
                            exit_exercise = True
                            break
                    else:
                        time.sleep(0.01)  # Small delay in web mode

                # If user wants to exit, break the outer loop too
                if exit_exercise:
                    break

                # Increment set if we've completed the required reps
                if count >= total_reps:
                    self.current_set += 1

                # Mark workout as complete if all sets are finished
                if self.current_set > self.sets:
                    self.workout_complete = True

                # Calculate final metrics
                end_time = time.process_time()
                time_elapsed = end_time - start_time
                calories_burned = int((time_elapsed / 60) * 8.5)  # Approx calories/min

                # Stop recording if active
                if hasattr(self, "video_recorder") and self.video_recorder:
                    if (
                        hasattr(self.video_recorder, "recording")
                        and self.video_recorder.recording
                    ):
                        print("[ExercisesModule] Stopping push-ups recording")
                        self.video_recorder.stop_recording()

                return {
                    "calories": calories_burned,
                    "time_elapsed": time_elapsed,
                    "reps_completed": int(count),
                    "total_reps": total_reps * self.sets,
                    "exited_early": exit_exercise,
                    "workout_complete": self.workout_complete,
                }
        except Exception as e:
            print(f"Error in push-ups exercise: {str(e)}")
            # Ensure proper cleanup on error
            if hasattr(self, "cap") and self.cap is not None:
                self.cap.release()
                self.cap = None
            if (
                not self.web_mode
                and "window_name" in locals()
                and cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) >= 1
            ):
                cv2.destroyAllWindows()
            return {"calories": 0, "time_elapsed": 0, "error": str(e)}

    def bicep_curls(self):
        self.utils.illustrate_exercise(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "TrainerImages",
                "bicep_curls_illustration.jpeg",
            ),
            "BICEP CURLS",
            web_mode=self.web_mode,
        )
        detector = pm.posture_detector()
        # Use reps directly without difficulty_level multiplier
        total_reps = self.reps

        cap = cv2.VideoCapture(self.camera_index)
        self.cap = cap  # Store reference for external release
        if not cap.isOpened():
            print(f"[ERROR] Camera {self.camera_index} could not be opened.")
            print("Camera error. Please try another camera.")
            return {"calories": 0, "time_elapsed": 0}

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 980)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 550)
        start = time.process_time()

        # Initialize video recording if enabled
        if hasattr(self, "video_recorder") and self.video_recorder is not None:
            self.video_recorder.start_recording("Bicep Curls")

        # Create window once at the beginning and set it to be topmost
        window_name = "Bicep Curls"
        if not self.web_mode:
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

        # Variables to track detection quality
        stable_detection_frames = 0
        required_stable_frames = 30  # Need 30 frames of good detection before starting
        detection_ready = False
        min_landmarks_required = (
            20  # Minimum number of landmarks to consider a good detection
        )

        # Required landmarks for bicep curls (face and arms)
        required_landmarks = [0, 2, 5, 11, 12, 13, 14, 15, 16]

        # Body part groups for better feedback
        body_part_groups = {
            "face": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "arms": [11, 12, 13, 14, 15, 16],
            "legs": [23, 24, 25, 26, 27, 28],
            "torso": [11, 12, 23, 24],
        }

        # Flag to track if user wants to exit
        exit_exercise = False

        # Continue until all sets are complete or user exits
        while self.current_set <= self.sets and not exit_exercise and not self.stopped:
            # Display which set we're on
            print(f"Starting Set {self.current_set} of {self.sets}")

            # Initialize counts, directions and timestamps for both arms
            left_count = 0
            right_count = 0
            left_direction = 0
            right_direction = 0
            last_left_update = 0
            last_right_update = 0
            MIN_TIME_BETWEEN_COUNTS = 0.5  # Minimum seconds between counts

            # Initialize completion percentages
            left_completion_pct = 0
            right_completion_pct = 0

            # Reset detection tracking for each set
            detection_ready = False
            stable_detection_frames = 0

            while (
                (left_count < total_reps or right_count < total_reps)
                and not exit_exercise
                and not self.stopped
            ):
                # Initialize colors for this frame
                default_bar_color = (120, 120, 120)  # Default gray
                left_color = default_bar_color
                right_color = default_bar_color

                success, img = cap.read()
                if not success or img is None:
                    continue

                img = cv2.resize(img, (980, 550))
                # Mirror the image horizontally
                img = cv2.flip(img, 1)
                img = detector.find_person(img, draw=False)
                landmark_list = detector.find_landmarks(img, False)

                if landmark_list and len(landmark_list) >= min_landmarks_required:
                    # Check if specific required landmarks are visible
                    all_required_visible = True
                    face_visible = True  # We specifically check if face is visible
                    missing_parts = []

                    # First check if face is visible (most important)
                    for landmark_id in [0, 2, 5]:  # Core face landmarks
                        visibility = detector.get_landmark_visibility(landmark_id)
                        if visibility < 0.7:  # Require high visibility threshold
                            face_visible = False
                            missing_parts.append("face")
                            break  # Exit early if face not visible

                    # Check arms visibility (critical for bicep curls)
                    left_arm_visible = True
                    right_arm_visible = True

                    # Check left arm landmarks [12, 14, 16]
                    for landmark_id in [12, 14, 16]:
                        visibility = detector.get_landmark_visibility(landmark_id)
                        if visibility < 0.7:
                            left_arm_visible = False
                            missing_parts.append("left arm")
                            break

                    # Check right arm landmarks [11, 13, 15]
                    for landmark_id in [11, 13, 15]:
                        visibility = detector.get_landmark_visibility(landmark_id)
                        if visibility < 0.7:
                            right_arm_visible = False
                            missing_parts.append("right arm")
                            break

                    # All required landmarks are visible with good confidence
                    if face_visible and (left_arm_visible or right_arm_visible):
                        # If we have at least one arm and face visible, we can proceed
                        if not detection_ready:
                            stable_detection_frames += 1
                            if stable_detection_frames >= required_stable_frames:
                                detection_ready = True
                                print(
                                    "Body detection stable - starting to count bicep curls"
                                )

                        # Get angles for both arms (swap left/right due to mirroring)
                        left_angle = (
                            detector.find_angle(img, 12, 14, 16)
                            if left_arm_visible
                            else 0
                        )
                        right_angle = (
                            detector.find_angle(img, 11, 13, 15)
                            if right_arm_visible
                            else 0
                        )

                        # Calculate percentage for each arm with refined angle ranges based on anatomy
                        # For bicep curls: ~170 degrees is arm extended, ~40 degrees is arm fully curled
                        # Reversed for more intuitive feedback - 0% is extended, 100% is fully curled
                        left_per = (
                            np.interp(left_angle, (170, 40), (0, 100))
                            if left_arm_visible
                            else 0
                        )
                        # Updated right arm angle range to use 343.7° as 100% curl
                        right_per = (
                            np.interp(right_angle, (170, 343.7), (0, 100))
                            if right_arm_visible
                            else 0
                        )

                        # Add debug printing for right arm angles
                        if right_arm_visible:
                            print(f"Right Arm Angle: {right_angle:.1f}°")
                            print(f"Right Arm Percentage: {right_per:.1f}%")
                            if right_per >= 85:
                                print("RIGHT ARM: CURL DETECTED!")

                        # Visualize angle measurement points with colored markers
                        if detection_ready:
                            if left_arm_visible:
                                # Left arm joint visualization
                                wrist_left = (
                                    landmark_list[16][1],
                                    landmark_list[16][2],
                                )
                                elbow_left = (
                                    landmark_list[14][1],
                                    landmark_list[14][2],
                                )
                                shoulder_left = (
                                    landmark_list[12][1],
                                    landmark_list[12][2],
                                )

                                # Draw circles at joints
                                elbow_color = (255, 200, 0)  # Cyan/teal color
                                cv2.circle(img, elbow_left, 7, elbow_color, -1)

                                # Draw lines connecting joints
                                line_color = (0, 255, 255)  # Yellow color
                                cv2.line(img, shoulder_left, elbow_left, line_color, 2)
                                cv2.line(img, elbow_left, wrist_left, line_color, 2)

                            if right_arm_visible:
                                # Right arm joint visualization
                                wrist_right = (
                                    landmark_list[15][1],
                                    landmark_list[15][2],
                                )
                                elbow_right = (
                                    landmark_list[13][1],
                                    landmark_list[13][2],
                                )
                                shoulder_right = (
                                    landmark_list[11][1],
                                    landmark_list[11][2],
                                )

                                # Draw circles at joints
                                elbow_color = (255, 200, 0)  # Cyan/teal color
                                cv2.circle(img, elbow_right, 7, elbow_color, -1)

                                # Draw lines connecting joints
                                line_color = (0, 255, 255)  # Yellow color
                                cv2.line(
                                    img, shoulder_right, elbow_right, line_color, 2
                                )
                                cv2.line(img, elbow_right, wrist_right, line_color, 2)

                        # Calculate percentage for each arm with refined angle ranges based on anatomy
                        # For bicep curls: ~170 degrees is arm extended, ~40 degrees is arm fully curled
                        # Reversed for more intuitive feedback - 0% is extended, 100% is fully curled
                        left_per = (
                            np.interp(left_angle, (170, 40), (0, 100))
                            if left_arm_visible
                            else 0
                        )
                        right_per = (
                            np.interp(right_angle, (170, 343.7), (0, 100))
                            if right_arm_visible
                            else 0
                        )

                        # Calculate bar values with matching ranges (lower = higher bar value)
                        left_bar = (
                            np.interp(left_angle, (170, 40), (650, 100))
                            if left_arm_visible
                            else 650
                        )
                        right_bar = (
                            np.interp(right_angle, (170, 343.7), (650, 100))
                            if right_arm_visible
                            else 650
                        )

                        current_time = time.time()

                        # Track overall performance as percentage of completed reps
                        left_performance_pct = min(100, (left_count / total_reps) * 100)
                        right_performance_pct = min(
                            100, (right_count / total_reps) * 100
                        )
                        overall_performance_pct = min(
                            100, ((left_count + right_count) / (total_reps * 2)) * 100
                        )

                        # Only count reps if we have stable detection
                        if detection_ready:
                            # Update left arm if visible
                            if left_count < total_reps and left_arm_visible:
                                # Set color based on current curl position
                                left_color = utilities().get_performance_bar_color(
                                    left_per
                                )

                                # Only count at the maximum curl position (>= 85%) or minimum extend position (<= 15%)
                                if (left_per >= 85 or left_per <= 15) and (
                                    current_time - last_left_update
                                ) >= MIN_TIME_BETWEEN_COUNTS:
                                    left_color = (0, 255, 0)  # Green at counting points

                                    # Clear visual feedback at maximum curl
                                    if left_per >= 85:
                                        cv2.putText(
                                            img,
                                            "L: CURL!",
                                            (50, 100),
                                            cv2.FONT_HERSHEY_SIMPLEX,
                                            0.7,
                                            (0, 255, 0),
                                            2,
                                        )

                                    result = utilities().repitition_counter(
                                        left_per, left_count, left_direction, "left"
                                    )
                                    if (
                                        result["count"] != left_count
                                    ):  # Only update timestamp if count changed
                                        last_left_update = current_time
                                    left_count = result["count"]
                                    left_direction = result["direction"]

                                # Display percentage based on rep completion for left arm (not angle)
                                left_completion_pct = min(
                                    100, (left_count / total_reps) * 100
                                )

                                # Display arm angle percentage and performance bar
                                utilities().draw_performance_bar(
                                    img,
                                    left_completion_pct,
                                    left_bar,
                                    left_color,
                                    left_count,
                                    is_left=True,
                                )

                            # Update right arm if visible
                            if right_count < total_reps and right_arm_visible:
                                # Set color based on current curl position
                                right_color = utilities().get_performance_bar_color(
                                    right_per
                                )

                                # Only count at the maximum curl position (>= 85%) or minimum extend position (<= 15%)
                                if (right_per >= 85 or right_per <= 15) and (
                                    current_time - last_right_update
                                ) >= MIN_TIME_BETWEEN_COUNTS:
                                    right_color = (0, 255, 0)

                                    # Clear visual feedback at maximum curl
                                    if right_per >= 85:
                                        cv2.putText(
                                            img,
                                            "R: CURL!",
                                            (img.shape[1] - 150, 100),
                                            cv2.FONT_HERSHEY_SIMPLEX,
                                            0.7,
                                            (0, 255, 0),
                                            2,
                                        )

                                    result = utilities().repitition_counter(
                                        right_per, right_count, right_direction, "right"
                                    )
                                    if (
                                        result["count"] != right_count
                                    ):  # Only update timestamp if count changed
                                        last_right_update = current_time
                                    right_count = result["count"]
                                    right_direction = result["direction"]

                                # Display percentage based on rep completion for right arm (not angle)
                                right_completion_pct = min(
                                    100, (right_count / total_reps) * 100
                                )

                                utilities().draw_performance_bar(
                                    img,
                                    right_completion_pct,
                                    right_bar,
                                    right_color,
                                    right_count,
                                    is_left=False,
                                )

                            # Draw overall performance based on rep completion
                            cv2.rectangle(
                                img,
                                (img.shape[1] // 2 - 150, 20),
                                (img.shape[1] // 2 + 150, 40),
                                (50, 50, 50),
                                cv2.FILLED,
                            )
                            cv2.rectangle(
                                img,
                                (img.shape[1] // 2 - 150, 20),
                                (
                                    int(
                                        img.shape[1] // 2
                                        - 150
                                        + overall_performance_pct * 3
                                    ),
                                    40,
                                ),
                                (0, 255, 0),
                                cv2.FILLED,
                            )
                            cv2.putText(
                                img,
                                f"Performance: {int(overall_performance_pct)}%",
                                (img.shape[1] // 2 - 145, 35),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,
                                (255, 255, 255),
                                1,
                            )
                        else:
                            # Draw performance bars but don't count reps
                            if left_arm_visible:
                                left_color = utilities().get_performance_bar_color(
                                    left_per
                                )
                                utilities().draw_performance_bar(
                                    img,
                                    left_completion_pct,
                                    left_bar,
                                    left_color,
                                    left_count,
                                    is_left=True,
                                )
                            if right_arm_visible:
                                right_color = utilities().get_performance_bar_color(
                                    right_per
                                )
                                utilities().draw_performance_bar(
                                    img,
                                    right_completion_pct,
                                    right_bar,
                                    right_color,
                                    right_count,
                                    is_left=False,
                                )
                    else:
                        # Some required landmarks are not visible
                        if stable_detection_frames > 0:
                            stable_detection_frames = max(
                                0, stable_detection_frames - 2
                            )

                        # If we were already counting but lost detection, reset detection status
                        if detection_ready:
                            # If face is not visible, we must pause counting
                            if not face_visible:
                                detection_ready = False
                                print("Lost face tracking - pausing rep counting")
                            # If both arms are lost, also pause counting
                            elif not left_arm_visible and not right_arm_visible:
                                detection_ready = False
                                print("Lost both arms tracking - pausing rep counting")
                            else:
                                # If just one arm is temporarily missing, continue with the other
                                print(
                                    "One arm not fully visible - continuing with visible arm only"
                                )

                        # Display missing body parts with clear instructions
                        if missing_parts:
                            # Remove duplicates and format nicely
                            missing_parts = list(set(missing_parts))
                            missing_text = f"Please position your {' and '.join(missing_parts)} in frame"
                            cv2.putText(
                                img,
                                missing_text,
                                (img.shape[1] // 2 - 200, 70),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.7,
                                (0, 0, 255),
                                2,
                            )
                else:
                    # Reset stable detection counter if we lose tracking
                    if stable_detection_frames > 0 and not detection_ready:
                        stable_detection_frames = max(
                            0, stable_detection_frames - 2
                        )  # Decrease counter faster than it builds
                    elif detection_ready:
                        # If we were counting but completely lost detection, pause counting
                        detection_ready = False
                        print("Lost body tracking - pausing rep counting")

                    # Display guidance to get back in frame
                    cv2.putText(
                        img,
                        "Please position yourself in frame",
                        (img.shape[1] // 2 - 200, 70),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2,
                    )

                # Display set and counts for bicep curls with modern counters
                draw_modern_counter(
                    img,
                    f"Set {self.current_set}/{self.sets}",
                    (10, 10),
                    text_color=(255, 255, 255),
                    bg_color=(90, 60, 40),
                )
                draw_modern_counter(
                    img,
                    f"L:{int(left_count)}/{total_reps}",
                    (10, 55),
                    text_color=(255, 255, 255),
                    bg_color=(75, 80, 195),
                )
                draw_modern_counter(
                    img,
                    f"R:{int(right_count)}/{total_reps}",
                    (10, 100),
                    text_color=(255, 255, 255),
                    bg_color=(100, 170, 85),
                )

                # Display detection status message
                if not detection_ready:
                    status_msg = f"Position your body in frame... ({stable_detection_frames}/{required_stable_frames})"
                    cv2.putText(
                        img,
                        status_msg,
                        (img.shape[1] // 2 - 200, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2,
                    )

                # Add exit instruction only in desktop mode
                if not self.web_mode:
                    cv2.putText(
                        img,
                        "Press 'q' to exit exercise",
                        (img.shape[1] - 230, img.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 255),
                        2,
                    )

                # Now write the processed frame to the video recorder
                if hasattr(self, "video_recorder") and self.video_recorder is not None:
                    try:
                        # Add a frame counter to track recording progress
                        if not hasattr(self, "frames_sent_to_recorder"):
                            self.frames_sent_to_recorder = 0
                        self.frames_sent_to_recorder += 1

                        # Log every 100 frames (about 3-4 seconds at 30fps)
                        if self.frames_sent_to_recorder % 100 == 0:
                            print(
                                f"[ExercisesModule] Sent {self.frames_sent_to_recorder} frames to video recorder"
                            )

                        # Make a copy of the frame to avoid modification issues
                        img_to_record = img.copy()
                        self.video_recorder.write_frame(img_to_record)
                    except Exception as e:
                        print(
                            f"[ExercisesModule] Error sending frame to video recorder: {e}"
                        )

                    # Store the processed frame for web streaming
                    with self.frame_lock:
                        self.last_processed_frame = img.copy()

                # Display image and ensure window is topmost in desktop mode
                if not self.web_mode:
                    cv2.imshow(window_name, img)
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

                    # Check for 'q' key press to exit (only in desktop mode)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        print("Exercise exited by user.")
                        exit_exercise = True
                        break
                else:
                    # In web mode, add a small delay to reduce CPU usage
                    time.sleep(0.01)

                # Exit the loop when both arms have completed the required reps
                if left_count >= total_reps and right_count >= total_reps:
                    break

            # If user wants to exit, break the outer loop too
            if exit_exercise:
                break

            # Move to next set when one set is complete
            if left_count >= total_reps and right_count >= total_reps:
                self.current_set += 1
                if self.current_set <= self.sets:
                    print(f"Great job! Moving to set {self.current_set}")
                    # Give a brief rest between sets
                    time.sleep(3)

        # Cleanup
        end = time.process_time()
        time_elapsed = end - start
        calories_burned = int((time_elapsed / 60) * 8.5)  # Approx calories/min

        # Stop recording
        if hasattr(self, "video_recorder") and self.video_recorder is not None:
            if (
                hasattr(self.video_recorder, "recording")
                and self.video_recorder.recording
            ):
                print("[ExercisesModule] Stopping bicep curls recording")
                self.video_recorder.stop_recording()

        cap.release()
        self.cap = None
        if not self.web_mode:
            cv2.destroyAllWindows()

        # Include rep completion data
        total_possible_reps = total_reps * 2 * self.sets  # Both arms, all sets
        total_completed_reps = int(left_count) + int(right_count)

        if self.current_set > self.sets:
            self.workout_complete = True
            print("[ExercisesModule] Bicep curls workout completed")

        return {
            "calories": calories_burned,
            "time_elapsed": time_elapsed,
            "reps_completed": total_completed_reps,
            "total_reps": total_possible_reps,
            "exited_early": exit_exercise,  # Add flag indicating if user exited early
            "workout_complete": self.workout_complete,
        }

    def mountain_climbers(self):
        try:
            self.utils.illustrate_exercise(
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "TrainerImages",
                    "mountain_climber_illustraion.jpeg",
                ),
                "MOUNTAIN CLIMBERS",
                web_mode=self.web_mode,
            )
            detector = pm.posture_detector()
            # Use reps directly without difficulty_level multiplier
            total_reps = self.reps

            # Initialize camera with proper error handling
            cap = cv2.VideoCapture(self.camera_index)
            self.cap = cap  # Store reference for external release
            if not cap.isOpened():
                print(f"[ERROR] Camera {self.camera_index} could not be opened.")
                print("Camera error. Please try another camera.")
                return {"calories": 0, "time_elapsed": 0}

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 980)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 550)
            start_time = time.process_time()

            # Initialize video recording if enabled
            if hasattr(self, "video_recorder") and self.video_recorder is not None:
                self.video_recorder.start_recording("Mountain Climbers")

            window_name = "Mountain Climbers"
            if not self.web_mode:
                cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

            # IMPROVED: Variables to track detection quality - reduced for faster startup
            stable_detection_frames = 0
            required_stable_frames = 10  # REDUCED from 20 to 10 for faster startup
            detection_ready = False
            min_landmarks_required = (
                12  # REDUCED from 15 to 12 for more lenient detection
            )

            # Required landmarks for mountain climbers (face and legs)
            required_landmarks = [0, 2, 5, 23, 24, 25, 26, 27, 28]

            # Body part groups for better feedback
            body_part_groups = {
                "face": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "legs": [23, 24, 25, 26, 27, 28],
                "torso": [11, 12, 23, 24],
            }

            # Angle ranges for leg movement
            NEUTRAL_MIN = 150
            NEUTRAL_MAX = 190
            LEFT_TARGET = 280
            LEFT_TOLERANCE = 25
            RIGHT_TARGET = 280
            RIGHT_TOLERANCE = 25

            exit_exercise = False
            self.current_set = 1

            # Initialize state variables once outside the loops
            left_completion_pct = 0
            right_completion_pct = 0
            left_count = 0
            right_count = 0

            print("[DEBUG] Mountain Climbers exercise started")

            while (
                self.current_set <= self.sets and not exit_exercise and not self.stopped
            ):
                print(f"Starting Set {self.current_set} of {self.sets}")

                # Simple counters - no state tracking
                left_count = 0
                right_count = 0

                # Timestamps to prevent double counting
                last_left_count_time = 0
                last_right_count_time = 0

                # Minimum time between counts to prevent double counting
                MIN_TIME_BETWEEN_COUNTS = 1.0

                # Direct movement tracking
                left_prev_angle = -1
                right_prev_angle = -1

                # Reset detection tracking for each set
                detection_ready = False
                stable_detection_frames = 0

                # Loop for one set (until both legs reach total_reps)
                while (
                    (left_count < total_reps or right_count < total_reps)
                    and not exit_exercise
                    and not self.stopped
                ):
                    # Initialize colors for this frame
                    default_bar_color = (120, 120, 120)  # Default gray
                    left_color = default_bar_color
                    right_color = default_bar_color

                    success, img = cap.read()
                    if not success or img is None:
                        print("Failed to read from camera")
                        continue

                    img = cv2.resize(img, (980, 550))
                    img = cv2.flip(img, 1)
                    img = detector.find_person(img, draw=False)
                    landmark_list = detector.find_landmarks(img, False)

                    if landmark_list and len(landmark_list) >= min_landmarks_required:
                        # Check if required landmarks are visible
                        all_required_visible = True
                        face_visible = True
                        left_leg_visible = True
                        right_leg_visible = True
                        missing_parts = []

                        # Check face visibility (most important)
                        for landmark_id in [0, 2, 5]:  # Core face landmarks
                            visibility = detector.get_landmark_visibility(landmark_id)
                            if (
                                visibility < 0.6
                            ):  # IMPROVED: Reduced from 0.7 to 0.6 for more lenient detection
                                face_visible = False
                                missing_parts.append("face")
                                break

                        # Check legs visibility (critical for mountain climbers)
                        # Left leg landmarks: hip (24), knee (26), ankle (28)
                        for landmark_id in [24, 26, 28]:
                            visibility = detector.get_landmark_visibility(landmark_id)
                            if (
                                visibility < 0.5
                            ):  # IMPROVED: Reduced from 0.6 to 0.5 for more lenient detection
                                left_leg_visible = False
                                missing_parts.append("left leg")
                                break

                        # Right leg landmarks: hip (23), knee (25), ankle (27)
                        for landmark_id in [23, 25, 27]:
                            visibility = detector.get_landmark_visibility(landmark_id)
                            if (
                                visibility < 0.5
                            ):  # IMPROVED: Reduced from 0.6 to 0.5 for more lenient detection
                                right_leg_visible = False
                                missing_parts.append("right leg")
                                break

                        # We need face and at least one leg visible
                        all_required_visible = face_visible and (
                            left_leg_visible or right_leg_visible
                        )

                        # IMPROVED: Add debug prints to see what's happening
                        if not all_required_visible:
                            print(
                                f"[DEBUG] Not all landmarks visible - Face: {face_visible}, Left Leg: {left_leg_visible}, Right Leg: {right_leg_visible}"
                            )

                        if all_required_visible:
                            if not detection_ready:
                                stable_detection_frames += 1
                                # IMPROVED: Add debug prints to see progress towards stability
                                print(
                                    f"[DEBUG] Stable frames: {stable_detection_frames}/{required_stable_frames}"
                                )
                                if stable_detection_frames >= required_stable_frames:
                                    detection_ready = True
                                    print(
                                        "[DEBUG] Detection stable - counting Mountain Climbers begins!"
                                    )

                            # Only calculate angles if detection is ready
                            if detection_ready:
                                try:
                                    # Get angles for both legs if visible
                                    left_angle = -1
                                    right_angle = -1

                                    # Visualize leg joints for better user feedback
                                    if left_leg_visible:
                                        hip_left = (
                                            landmark_list[24][1],
                                            landmark_list[24][2],
                                        )
                                        knee_left = (
                                            landmark_list[26][1],
                                            landmark_list[26][2],
                                        )
                                        ankle_left = (
                                            landmark_list[28][1],
                                            landmark_list[28][2],
                                        )

                                        # Draw circles at joints for better visibility
                                        knee_color = (255, 200, 0)  # Cyan/teal color
                                        cv2.circle(img, knee_left, 7, knee_color, -1)

                                        # Draw lines connecting joints
                                        line_color = (0, 255, 255)  # Yellow color
                                        cv2.line(
                                            img, hip_left, knee_left, line_color, 2
                                        )
                                        cv2.line(
                                            img, knee_left, ankle_left, line_color, 2
                                        )

                                        # Calculate angle with explicit error handling
                                        try:
                                            left_angle = detector.find_angle(
                                                img, 24, 26, 28
                                            )
                                            print(f"Left Leg Angle: {left_angle:.1f}°")
                                        except Exception as e:
                                            print(
                                                f"Error calculating left leg angle: {e}"
                                            )

                                    if right_leg_visible:
                                        hip_right = (
                                            landmark_list[23][1],
                                            landmark_list[23][2],
                                        )
                                        knee_right = (
                                            landmark_list[25][1],
                                            landmark_list[25][2],
                                        )
                                        ankle_right = (
                                            landmark_list[27][1],
                                            landmark_list[27][2],
                                        )

                                        # Draw circles at joints for better visibility
                                        knee_color = (255, 200, 0)  # Cyan/teal color
                                        cv2.circle(img, knee_right, 7, knee_color, -1)

                                        # Draw lines connecting joints
                                        line_color = (0, 255, 255)  # Yellow color
                                        cv2.line(
                                            img, hip_right, knee_right, line_color, 2
                                        )
                                        cv2.line(
                                            img, knee_right, ankle_right, line_color, 2
                                        )

                                        # Calculate angle with explicit error handling
                                        try:
                                            right_angle = detector.find_angle(
                                                img, 23, 25, 27
                                            )
                                            print(
                                                f"Right Leg Angle: {right_angle:.1f}°"
                                            )
                                        except Exception as e:
                                            print(
                                                f"Error calculating right leg angle: {e}"
                                            )

                                    # Calculate percentages for progress bars - just for visualization
                                    left_per = (
                                        np.interp(left_angle, (170, 280), (0, 100))
                                        if left_angle != -1
                                        else -1
                                    )
                                    right_per = (
                                        np.interp(right_angle, (170, 280), (0, 100))
                                        if right_angle != -1
                                        else -1
                                    )

                                    # Calculate bar values for visualization
                                    left_bar = (
                                        np.interp(left_angle, (170, 280), (650, 100))
                                        if left_angle != -1
                                        else 650
                                    )
                                    right_bar = (
                                        np.interp(right_angle, (170, 280), (650, 100))
                                        if right_angle != -1
                                        else 650
                                    )

                                    # Calculate colors based on current percentage
                                    left_color = (
                                        utilities().get_performance_bar_color(left_per)
                                        if left_per != -1
                                        else default_bar_color
                                    )
                                    right_color = (
                                        utilities().get_performance_bar_color(right_per)
                                        if right_per != -1
                                        else default_bar_color
                                    )

                                    # Get current time for rep counting
                                    current_time = time.time()

                                    # Calculate completion percentages for progress bars
                                    left_completion_pct = min(
                                        100, (left_count / total_reps) * 100
                                    )
                                    right_completion_pct = min(
                                        100, (right_count / total_reps) * 100
                                    )

                                    # Calculate overall performance (average of both legs)
                                    overall_performance_pct = min(
                                        100,
                                        ((left_count + right_count) / (total_reps * 2))
                                        * 100,
                                    )

                                    # Count reps for left leg
                                    if (
                                        left_count < total_reps
                                        and left_leg_visible
                                        and left_angle != -1
                                    ):
                                        # Check if angle is near target
                                        is_at_target = (
                                            abs(left_angle - LEFT_TARGET)
                                            <= LEFT_TOLERANCE
                                        )

                                        # Only count if we haven't counted recently (avoid double counting)
                                        if (
                                            is_at_target
                                            and (current_time - last_left_count_time)
                                            >= MIN_TIME_BETWEEN_COUNTS
                                        ):
                                            left_count += 1
                                            print(
                                                f"LEFT LEG REP: {left_count} (angle: {left_angle:.1f}°)"
                                            )
                                            last_left_count_time = current_time

                                            # Flash green for visual feedback
                                            left_color = (0, 255, 0)

                                            # Show text feedback
                                            cv2.putText(
                                                img,
                                                "LEFT REP!",
                                                (img.shape[1] // 4, 120),
                                                cv2.FONT_HERSHEY_SIMPLEX,
                                                0.8,
                                                (0, 255, 0),
                                                2,
                                            )

                                        # Draw progress bar
                                        utilities().draw_performance_bar(
                                            img,
                                            left_completion_pct,
                                            left_bar,
                                            left_color,
                                            left_count,
                                            is_left=True,
                                        )

                                    # Count reps for right leg
                                    if (
                                        right_count < total_reps
                                        and right_leg_visible
                                        and right_angle != -1
                                    ):
                                        # Check if angle is near target
                                        is_at_target = (
                                            abs(right_angle - RIGHT_TARGET)
                                            <= RIGHT_TOLERANCE
                                        )

                                        # Only count if we haven't counted recently (avoid double counting)
                                        if (
                                            is_at_target
                                            and (current_time - last_right_count_time)
                                            >= MIN_TIME_BETWEEN_COUNTS
                                        ):
                                            right_count += 1
                                            print(
                                                f"RIGHT LEG REP: {right_count} (angle: {right_angle:.1f}°)"
                                            )
                                            last_right_count_time = current_time

                                            # Flash green for visual feedback
                                            right_color = (0, 255, 0)

                                            # Show text feedback
                                            cv2.putText(
                                                img,
                                                "RIGHT REP!",
                                                (
                                                    img.shape[1] // 2
                                                    + img.shape[1] // 8,
                                                    120,
                                                ),
                                                cv2.FONT_HERSHEY_SIMPLEX,
                                                0.8,
                                                (0, 255, 0),
                                                2,
                                            )

                                        # Draw progress bar
                                        utilities().draw_performance_bar(
                                            img,
                                            right_completion_pct,
                                            right_bar,
                                            right_color,
                                            right_count,
                                            is_left=False,
                                        )

                                    # Draw overall performance
                                    cv2.rectangle(
                                        img,
                                        (img.shape[1] // 2 - 150, 20),
                                        (img.shape[1] // 2 + 150, 40),
                                        (50, 50, 50),
                                        cv2.FILLED,
                                    )
                                    cv2.rectangle(
                                        img,
                                        (img.shape[1] // 2 - 150, 20),
                                        (
                                            int(
                                                img.shape[1] // 2
                                                - 150
                                                + overall_performance_pct * 3
                                            ),
                                            40,
                                        ),
                                        (0, 255, 0),
                                        cv2.FILLED,
                                    )
                                    cv2.putText(
                                        img,
                                        f"Performance: {int(overall_performance_pct)}%",
                                        (img.shape[1] // 2 - 145, 35),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        0.5,
                                        (255, 255, 255),
                                        1,
                                    )

                                    # Update metrics for web mode
                                    self.current_set = self.current_set
                                    self.reps_completed = left_count + right_count
                                    self.calories_burned = (
                                        left_count + right_count
                                    ) * 0.6  # Simple calorie calculation
                                    self.feedback = "Good form! Keep going!"

                                    # Add form guidance
                                    cv2.putText(
                                        img,
                                        "Keep your core tight!",
                                        (img.shape[1] // 2 - 150, 240),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        0.7,
                                        (0, 200, 200),
                                        2,
                                    )

                                    # Update previous angles
                                    left_prev_angle = left_angle
                                    right_prev_angle = right_angle
                                except Exception as e:
                                    print(f"Error in mountain climber tracking: {e}")
                            else:
                                # Draw bars even if not counting yet
                                if left_leg_visible:
                                    utilities().draw_performance_bar(
                                        img,
                                        left_completion_pct,
                                        650,
                                        left_color,
                                        left_count,
                                        is_left=True,
                                    )
                                if right_leg_visible:
                                    utilities().draw_performance_bar(
                                        img,
                                        right_completion_pct,
                                        650,
                                        right_color,
                                        right_count,
                                        is_left=False,
                                    )
                        else:
                            # Some required landmarks are not visible
                            if stable_detection_frames > 0:
                                stable_detection_frames = max(
                                    0, stable_detection_frames - 1
                                )
                                print(
                                    f"[DEBUG] Landmarks lost, reducing stable frames to: {stable_detection_frames}"
                                )

                            # If we were already counting but lost detection, reset detection status
                            if detection_ready:
                                if not face_visible:
                                    # IMPROVED: Keep detection ready if face reappears quickly
                                    # detection_ready = False  <- commented out to be more persistent
                                    print(
                                        "[DEBUG] Lost face tracking - but continuing rep counting"
                                    )
                                elif not left_leg_visible and not right_leg_visible:
                                    # IMPROVED: Keep detection ready if legs reappear quickly
                                    # detection_ready = False  <- commented out to be more persistent
                                    print(
                                        "[DEBUG] Lost both legs tracking - but continuing rep counting"
                                    )

                            # Display missing body parts with clear instructions
                            if missing_parts:
                                # Remove duplicates and format nicely
                                missing_parts = list(set(missing_parts))
                                missing_text = f"Please position your {' and '.join(missing_parts)} in frame"
                                cv2.putText(
                                    img,
                                    missing_text,
                                    (img.shape[1] // 2 - 200, 70),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.7,
                                    (0, 0, 255),
                                    2,
                                )
                    else:
                        # Reset stable detection counter if we lose tracking
                        if stable_detection_frames > 0:
                            stable_detection_frames = max(
                                0, stable_detection_frames - 1
                            )
                        if detection_ready:
                            # If we were counting but completely lost detection, pause counting
                            detection_ready = False
                            print("Lost body tracking - pausing rep counting")

                        # Display guidance to get back in frame
                        cv2.putText(
                            img,
                            "Please position yourself in frame",
                            (img.shape[1] // 2 - 200, 70),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 0, 255),
                            2,
                        )

                    # Display set and rep counters with modern counters
                    draw_modern_counter(
                        img,
                        f"Set {self.current_set}/{self.sets}",
                        (10, 10),
                        text_color=(255, 255, 255),
                        bg_color=(90, 60, 40),
                    )
                    draw_modern_counter(
                        img,
                        f"L:{int(left_count)}/{total_reps}",
                        (10, 55),
                        text_color=(255, 255, 255),
                        bg_color=(75, 80, 195),
                    )
                    draw_modern_counter(
                        img,
                        f"R:{int(right_count)}/{total_reps}",
                        (10, 100),
                        text_color=(255, 255, 255),
                        bg_color=(100, 170, 85),
                    )

                    # Display detection status message
                    if not detection_ready:
                        status_msg = f"Position your body in frame... ({stable_detection_frames}/{required_stable_frames})"
                        cv2.putText(
                            img,
                            status_msg,
                            (img.shape[1] // 2 - 200, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 0, 255),
                            2,
                        )
                    else:
                        # IMPROVED: Add status message when detection is ready
                        cv2.putText(
                            img,
                            "Detection ready! Start moving legs for Mountain Climbers",
                            (img.shape[1] // 2 - 250, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 0),
                            2,
                        )

                    # Add text to inform user they can press 'q' to exit
                    cv2.putText(
                        img,
                        "Press 'q' to exit exercise",
                        (img.shape[1] - 230, img.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 255),
                        2,
                    )

                    # Now write the processed frame to the video recorder
                    if (
                        hasattr(self, "video_recorder")
                        and self.video_recorder is not None
                    ):
                        try:
                            # Add a frame counter to track recording progress
                            if not hasattr(self, "frames_sent_to_recorder"):
                                self.frames_sent_to_recorder = 0
                            self.frames_sent_to_recorder += 1

                            # Log every 100 frames (about 3-4 seconds at 30fps)
                            if self.frames_sent_to_recorder % 100 == 0:
                                print(
                                    f"[ExercisesModule] Sent {self.frames_sent_to_recorder} frames to video recorder"
                                )

                            # Make a copy of the frame to avoid modification issues
                            img_to_record = img.copy()
                            self.video_recorder.write_frame(img_to_record)
                        except Exception as e:
                            print(
                                f"[ExercisesModule] Error sending frame to video recorder: {e}"
                            )

                    # Store the processed frame for web streaming
                    with self.frame_lock:
                        self.last_processed_frame = img.copy()

                    # Display image in desktop mode
                    if not self.web_mode:
                        cv2.imshow(window_name, img)
                        if cv2.waitKey(1) & 0xFF == ord("q"):
                            print("Exercise exited by user")
                            exit_exercise = True
                            break
                    else:
                        time.sleep(0.01)  # Small delay in web mode

                # If user wants to exit, break the outer loop too
                if exit_exercise:
                    break

                # Exit loop when both legs have completed required reps
                if left_count >= total_reps and right_count >= total_reps:
                    print(f"Completed Set {self.current_set}")
                    self.current_set += 1

                    # Give a short break between sets if not the last set
                    if self.current_set <= self.sets:
                        print(f"Take a short break before Set {self.current_set}")
                        break_timer = 10  # 10 second break
                        while (
                            break_timer > 0 and not exit_exercise and not self.stopped
                        ):
                            success, img = cap.read()
                            if success:
                                img = cv2.resize(img, (980, 550))
                                img = cv2.flip(img, 1)
                                # More appealing break timer display
                                draw_modern_counter(
                                    img,
                                    f"Break: {break_timer} sec",
                                    (img.shape[1] // 2 - 80, img.shape[0] // 2 - 20),
                                    text_color=(255, 255, 255),
                                    bg_color=(110, 190, 95),
                                    text_size=1.0,
                                )

                                # Add text to inform user they can press 'q' to exit
                                cv2.putText(
                                    img,
                                    "Press 'q' to exit exercise",
                                    (img.shape[1] - 230, img.shape[0] - 20),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.6,
                                    (255, 255, 255),
                                    2,
                                )

                                if not self.web_mode:
                                    cv2.imshow(window_name, img)
                                    if cv2.waitKey(1000) & 0xFF == ord("q"):
                                        print("Exercise exited by user during break.")
                                        exit_exercise = True
                                        break
                                else:
                                    # Store the frame for web streaming and add delay
                                    with self.frame_lock:
                                        self.last_processed_frame = img.copy()
                                    time.sleep(1.0)

                                break_timer -= 1
                            else:
                                break

            # Cleanup
            cap.release()
            self.cap = None
            if not self.web_mode:
                cv2.destroyAllWindows()

            # Stop recording if active
            if hasattr(self, "video_recorder") and self.video_recorder:
                if (
                    hasattr(self.video_recorder, "recording")
                    and self.video_recorder.recording
                ):
                    print("[ExercisesModule] Stopping mountain climbers recording")
                    self.video_recorder.stop_recording()

            # Calculate final metrics
            end_time = time.process_time()
            time_elapsed = end_time - start_time
            calories_burned = int(
                (time_elapsed / 60) * 10.5
            )  # Approx calories/min for mountain climbers (higher intensity)

            # Rep completion data
            total_possible_reps = total_reps * 2 * self.sets  # Both legs, all sets
            total_completed_reps = int(left_count) + int(right_count)

            if self.current_set > self.sets:
                self.workout_complete = True
                print("[ExercisesModule] Mountain climbers workout completed")

            return {
                "calories": calories_burned,
                "time_elapsed": time_elapsed,
                "reps_completed": total_completed_reps,
                "total_reps": total_possible_reps,
                "sets_completed": self.current_set - 1,
                "exited_early": exit_exercise,
                "workout_complete": self.workout_complete,
            }
        except Exception as e:
            print(f"Error in mountain climbers exercise: {str(e)}")
            # Ensure proper cleanup on error
            if hasattr(self, "cap") and self.cap is not None:
                self.cap.release()
                self.cap = None
            if (
                not self.web_mode
                and "window_name" in locals()
                and cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) >= 1
            ):
                cv2.destroyAllWindows()
            return {"calories": 0, "time_elapsed": 0, "error": str(e)}

    def squats(self):
        try:
            self.utils.illustrate_exercise(
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "TrainerImages",
                    "squats_illustration.jpeg",
                ),
                "SQUATS",
                web_mode=self.web_mode,
            )
            detector = pm.posture_detector()
            # Use reps directly without difficulty_level multiplier
            total_reps = self.reps

            # Initialize camera with proper error handling
            cap = cv2.VideoCapture(self.camera_index)
            self.cap = cap  # Store reference for external release
            if not cap.isOpened():
                print(f"[ERROR] Camera {self.camera_index} could not be opened.")
                print("Camera error. Please try another camera.")
                return {"calories": 0, "time_elapsed": 0}

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 980)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 550)
            start_time = time.process_time()

            # Initialize video recording if enabled
            if hasattr(self, "video_recorder") and self.video_recorder is not None:
                self.video_recorder.start_recording("Squats")

            window_name = "Squats"
            if not self.web_mode:
                cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

            # Variables to track detection quality
            stable_detection_frames = 0
            required_stable_frames = 20
            detection_ready = False
            min_landmarks_required = 15

            # Required landmarks for squats (face and legs)
            required_landmarks = [0, 2, 5, 23, 24, 25, 26, 27, 28]

            # Body part groups for better feedback
            body_part_groups = {
                "face": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "legs": [23, 24, 25, 26, 27, 28],
                "torso": [11, 12, 23, 24],
            }

            exit_exercise = False
            self.current_set = 1

            while (
                self.current_set <= self.sets and not exit_exercise and not self.stopped
            ):
                print(f"Starting Set {self.current_set} of {self.sets}")

                # Initialize counters
                count = 0
                direction = 0
                last_count_update = 0
                MIN_TIME_BETWEEN_COUNTS = 0.5  # Minimum seconds between counts

                # Initialize completion percentage
                completion_pct = 0

                # Loop for one set
                while count < total_reps and not exit_exercise and not self.stopped:
                    success, img = cap.read()
                    if not success or img is None:
                        print("Failed to read from camera")
                        continue

                    img = cv2.resize(img, (980, 550))
                    img = cv2.flip(img, 1)
                    img = detector.find_person(img, draw=False)
                    landmark_list = detector.find_landmarks(img, False)

                    if landmark_list and len(landmark_list) >= min_landmarks_required:
                        # Check if required landmarks are visible
                        all_required_visible = True
                        face_visible = True
                        legs_visible = True
                        missing_parts = []

                        # Check face visibility (most important)
                        for landmark_id in [0, 2, 5]:  # Core face landmarks
                            visibility = detector.get_landmark_visibility(landmark_id)
                            if visibility < 0.7:  # Require high visibility threshold
                                face_visible = False
                                missing_parts.append("face")
                                break

                        # Check legs visibility (critical for squats)
                        # Right leg landmarks: hip (24), knee (26), ankle (28)
                        for landmark_id in [24, 26, 28]:
                            visibility = detector.get_landmark_visibility(landmark_id)
                            if visibility < 0.6:  # Slightly lower threshold for legs
                                legs_visible = False
                                missing_parts.append("legs")
                                break

                        # We need both face and legs visible
                        all_required_visible = face_visible and legs_visible

                        if all_required_visible:
                            if not detection_ready:
                                stable_detection_frames += 1
                                if stable_detection_frames >= required_stable_frames:
                                    detection_ready = True
                                    print("Detection stable - counting Squats")

                            # Only calculate angles if detection is ready
                            if detection_ready:
                                try:
                                    # Visualize leg joints for better user feedback
                                    hip_right = (
                                        landmark_list[24][1],
                                        landmark_list[24][2],
                                    )
                                    knee_right = (
                                        landmark_list[26][1],
                                        landmark_list[26][2],
                                    )
                                    ankle_right = (
                                        landmark_list[28][1],
                                        landmark_list[28][2],
                                    )

                                    # Draw circles at joints for better visibility
                                    knee_color = (255, 200, 0)  # Cyan/teal color
                                    cv2.circle(img, knee_right, 7, knee_color, -1)

                                    # Draw lines connecting joints
                                    line_color = (0, 255, 255)  # Yellow color
                                    cv2.line(img, hip_right, knee_right, line_color, 2)
                                    cv2.line(
                                        img, knee_right, ankle_right, line_color, 2
                                    )

                                    # Calculate angle with explicit error handling
                                    try:
                                        angle = detector.find_angle(img, 24, 26, 28)
                                        print(f"Squat Angle: {angle:.1f}°")

                                        # Squat angle ranges: ~170-180 when standing, ~120-130 at bottom of squat
                                        # 0% when standing straight, 100% when in squat position
                                        per = np.interp(angle, (180, 125), (0, 100))
                                        bar = np.interp(angle, (180, 125), (650, 100))

                                        print(f"Squat Percentage: {per:.1f}%")

                                        # Get current time for rep counting
                                        current_time = time.time()

                                        # Set color based on current squat position
                                        color = utilities().get_performance_bar_color(
                                            per
                                        )

                                        # Count reps with minimum time between counts
                                        if (per >= 85 or per <= 15) and (
                                            current_time - last_count_update
                                        ) >= MIN_TIME_BETWEEN_COUNTS:
                                            color = (
                                                0,
                                                255,
                                                0,
                                            )  # Green at counting points

                                            # Show visual feedback at maximum squat depth
                                            if per >= 85:
                                                cv2.putText(
                                                    img,
                                                    "SQUAT POSITION!",
                                                    (img.shape[1] // 2 - 150, 200),
                                                    cv2.FONT_HERSHEY_SIMPLEX,
                                                    0.8,
                                                    (0, 255, 0),
                                                    2,
                                                )
                                                print("SQUAT POSITION DETECTED!")

                                            # Update count using the repitition counter
                                            result = utilities().repitition_counter(
                                                per, count, direction
                                            )
                                            if (
                                                result["count"] != count
                                            ):  # Only update timestamp if count changed
                                                last_count_update = current_time
                                            count = result["count"]
                                            direction = result["direction"]

                                        # Calculate overall performance based on rep completion
                                        completion_pct = min(
                                            100, (count / total_reps) * 100
                                        )

                                        # Draw performance bars and indicators
                                        utilities().draw_performance_bar(
                                            img, completion_pct, bar, color, count
                                        )

                                        # Draw overall performance based on rep completion
                                        cv2.rectangle(
                                            img,
                                            (img.shape[1] // 2 - 150, 20),
                                            (img.shape[1] // 2 + 150, 40),
                                            (50, 50, 50),
                                            cv2.FILLED,
                                        )
                                        cv2.rectangle(
                                            img,
                                            (img.shape[1] // 2 - 150, 20),
                                            (
                                                int(
                                                    img.shape[1] // 2
                                                    - 150
                                                    + completion_pct * 3
                                                ),
                                                40,
                                            ),
                                            (0, 255, 0),
                                            cv2.FILLED,
                                        )
                                        cv2.putText(
                                            img,
                                            f"Performance: {int(completion_pct)}%",
                                            (img.shape[1] // 2 - 145, 35),
                                            cv2.FONT_HERSHEY_SIMPLEX,
                                            0.5,
                                            (255, 255, 255),
                                            1,
                                        )

                                        # Update metrics for web mode
                                        self.current_set = self.current_set
                                        self.reps_completed = count
                                        self.calories_burned = (
                                            count * 0.5
                                        )  # Simple calorie calculation
                                        self.feedback = "Good form! Keep going!"
                                    except Exception as e:
                                        print(f"Error calculating angle: {e}")
                                except Exception as e:
                                    print(f"Error in squat tracking: {e}")
                        else:
                            # Some required landmarks are not visible
                            if stable_detection_frames > 0:
                                stable_detection_frames = max(
                                    0, stable_detection_frames - 2
                                )

                            # If we were already counting but lost detection, reset detection status
                            if detection_ready:
                                if not face_visible:
                                    detection_ready = False
                                    print("Lost face tracking - pausing rep counting")
                                elif not legs_visible:
                                    detection_ready = False
                                    print("Lost legs tracking - pausing rep counting")

                            # Display missing body parts with clear instructions
                            if missing_parts:
                                # Remove duplicates and format nicely
                                missing_parts = list(set(missing_parts))
                                missing_text = f"Please position your {' and '.join(missing_parts)} in frame"
                                cv2.putText(
                                    img,
                                    missing_text,
                                    (img.shape[1] // 2 - 200, 70),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.7,
                                    (0, 0, 255),
                                    2,
                                )
                    else:
                        # Reset stable detection counter if we lose tracking
                        if stable_detection_frames > 0:
                            stable_detection_frames = max(
                                0, stable_detection_frames - 2
                            )
                        if detection_ready:
                            # If we were counting but completely lost detection, pause counting
                            detection_ready = False
                            print("Lost body tracking - pausing rep counting")

                        # Display guidance to get back in frame
                        cv2.putText(
                            img,
                            "Please position yourself in frame",
                            (img.shape[1] // 2 - 200, 70),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 0, 255),
                            2,
                        )

                    # Display set and rep counters with modern counters
                    draw_modern_counter(
                        img,
                        f"Set {self.current_set}/{self.sets}",
                        (10, 10),
                        text_color=(255, 255, 255),
                        bg_color=(90, 60, 40),
                    )
                    draw_modern_counter(
                        img,
                        f"Rep {int(count)}/{total_reps}",
                        (10, 55),
                        text_color=(255, 255, 255),
                        bg_color=(100, 170, 85),
                    )

                    # Display detection status message
                    if not detection_ready:
                        status_msg = f"Position your body in frame... ({stable_detection_frames}/{required_stable_frames})"
                        cv2.putText(
                            img,
                            status_msg,
                            (img.shape[1] // 2 - 200, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 0, 255),
                            2,
                        )

                    # Add text to inform user they can press 'q' to exit
                    cv2.putText(
                        img,
                        "Press 'q' to exit exercise",
                        (img.shape[1] - 230, img.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 255),
                        2,
                    )

                    # Now write the processed frame to the video recorder
                    if (
                        hasattr(self, "video_recorder")
                        and self.video_recorder is not None
                    ):
                        try:
                            # Add a frame counter to track recording progress
                            if not hasattr(self, "frames_sent_to_recorder"):
                                self.frames_sent_to_recorder = 0
                            self.frames_sent_to_recorder += 1

                            # Log every 100 frames (about 3-4 seconds at 30fps)
                            if self.frames_sent_to_recorder % 100 == 0:
                                print(
                                    f"[ExercisesModule] Sent {self.frames_sent_to_recorder} frames to video recorder"
                                )

                            # Make a copy of the frame to avoid modification issues
                            img_to_record = img.copy()
                            self.video_recorder.write_frame(img_to_record)
                        except Exception as e:
                            print(
                                f"[ExercisesModule] Error sending frame to video recorder: {e}"
                            )

                    # Store the processed frame for web streaming
                    with self.frame_lock:
                        self.last_processed_frame = img.copy()

                    # Display image in desktop mode
                    if not self.web_mode:
                        cv2.imshow(window_name, img)
                        if cv2.waitKey(1) & 0xFF == ord("q"):
                            print("Exercise exited by user")
                            exit_exercise = True
                            break
                    else:
                        time.sleep(0.01)  # Small delay in web mode

                # If user wants to exit, break the outer loop too
                if exit_exercise:
                    break

                # Increment set counter after completing a set
                if count >= total_reps:
                    print(f"Completed Set {self.current_set}")
                    self.current_set += 1

                    # Give a short break between sets if not the last set
                    if self.current_set <= self.sets:
                        print(f"Take a short break before Set {self.current_set}")
                        break_timer = 10  # 10 second break
                        while (
                            break_timer > 0 and not exit_exercise and not self.stopped
                        ):
                            success, img = cap.read()
                            if success:
                                img = cv2.resize(img, (980, 550))
                                img = cv2.flip(img, 1)
                                # More appealing break timer display
                                draw_modern_counter(
                                    img,
                                    f"Break: {break_timer} sec",
                                    (img.shape[1] // 2 - 80, img.shape[0] // 2 - 20),
                                    text_color=(255, 255, 255),
                                    bg_color=(110, 190, 95),
                                    text_size=1.0,
                                )

                                # Add text to inform user they can press 'q' to exit
                                cv2.putText(
                                    img,
                                    "Press 'q' to exit exercise",
                                    (img.shape[1] - 230, img.shape[0] - 20),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.6,
                                    (255, 255, 255),
                                    2,
                                )

                                if not self.web_mode:
                                    cv2.imshow(window_name, img)
                                    if cv2.waitKey(1000) & 0xFF == ord("q"):
                                        print("Exercise exited by user during break.")
                                        exit_exercise = True
                                        break
                                else:
                                    # Store the frame for web streaming and add delay
                                    with self.frame_lock:
                                        self.last_processed_frame = img.copy()
                                    time.sleep(1.0)

                                break_timer -= 1
                            else:
                                break

            # Cleanup
            cap.release()
            self.cap = None
            if not self.web_mode:
                cv2.destroyAllWindows()

            # Stop recording if active
            if hasattr(self, "video_recorder") and self.video_recorder:
                if (
                    hasattr(self.video_recorder, "recording")
                    and self.video_recorder.recording
                ):
                    print("[ExercisesModule] Stopping squats recording")
                    self.video_recorder.stop_recording()

            # Calculate final metrics
            end_time = time.process_time()
            time_elapsed = end_time - start_time
            calories_burned = int(
                (time_elapsed / 60) * 8.5
            )  # Approx calories/min for squats

            if self.current_set > self.sets:
                self.workout_complete = True
                print("[ExercisesModule] Squats workout completed")

            return {
                "calories": calories_burned,
                "time_elapsed": time_elapsed,
                "reps_completed": int(count),
                "total_reps": total_reps * self.sets,
                "sets_completed": self.current_set - 1,
                "exited_early": exit_exercise,
                "workout_complete": self.workout_complete,
            }
        except Exception as e:
            print(f"Error in squats exercise: {str(e)}")
            # Ensure proper cleanup on error
            if hasattr(self, "cap") and self.cap is not None:
                self.cap.release()
                self.cap = None
            if (
                not self.web_mode
                and "window_name" in locals()
                and cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) >= 1
            ):
                cv2.destroyAllWindows()
            return {"calories": 0, "time_elapsed": 0, "error": str(e)}

    def release_camera(self):
        """Release the camera resource if open."""
        try:
            # Stop any active recording first
            if hasattr(self, "video_recorder") and self.video_recorder:
                if (
                    hasattr(self.video_recorder, "recording")
                    and self.video_recorder.recording
                ):
                    print(
                        "[ExercisesModule] Stopping recording before releasing camera"
                    )
                    self.video_recorder.stop_recording()
        except Exception as e:
            print(f"[ExercisesModule] Error stopping recording: {e}")

        # Now release the camera
        if hasattr(self, "cap") and self.cap is not None:
            try:
                self.cap.release()
                print(
                    "[ExercisesModule] Camera resource released via release_camera()."
                )
            except Exception as e:
                print(f"[ExercisesModule] Error releasing camera: {e}")
            self.cap = None
        if hasattr(self, "video_stream") and self.video_stream is not None:
            try:
                self.video_stream.stop()
                if (
                    hasattr(self.video_stream, "stream")
                    and self.video_stream.stream is not None
                ):
                    self.video_stream.stream.release()
                    print(
                        "[ExercisesModule] VideoStream resource released via release_camera()."
                    )
            except Exception as e:
                print(f"[ExercisesModule] Error releasing video_stream: {e}")
            self.video_stream = None

    def encode_frame(self, frame):
        """Encode a frame to base64 for web streaming."""
        try:
            if frame is None:
                return None
            _, buffer = cv2.imencode(".jpg", frame)
            return base64.b64encode(buffer).decode("utf-8")
        except Exception as e:
            print(f"[ExercisesModule] Error encoding frame: {e}")
            return None

    def start_new_exercise(self, exercise_type, sets, reps):
        """
        Start a new exercise in the same session.
        This allows continuing with a different exercise while preserving the session.

        Args:
            exercise_type: Type of exercise to perform
            sets: Number of sets
            reps: Number of reps per set

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print(
                f"[ExercisesModule] Starting new exercise: {exercise_type} in session {self.session_id}"
            )

            # Update session parameters
            self.exercise_type = exercise_type
            self.sets = sets
            self.reps = reps
            self.current_set = 1
            self.reps_completed = 0
            self.workout_complete = False
            self.feedback = f"Starting {exercise_type}"

            # If already recording, stop current recording
            if hasattr(self, "video_recorder") and self.video_recorder:
                if self.video_recorder.recording:
                    self.video_recorder.stop_recording()
                    print(f"[ExercisesModule] Stopped current recording")

                # Start new recording in the same session
                self.video_recorder.continue_recording_session(
                    exercise_type, self.session_id
                )
                print(
                    f"[ExercisesModule] Started recording for new exercise {exercise_type} in session {self.session_id}"
                )

            # Map common exercise names to method names
            exercise_method_map = {
                "bicep_curls": "bicep_curls",
                "push_ups": "push_ups",
                "squats": "squats",
                "mountain_climbers": "mountain_climbers",
                # Add any name variants here
            }

            # Look up in the map or use as is
            exercise_method = exercise_method_map.get(exercise_type, exercise_type)
            print(f"Using method: {exercise_method}")

            # Stop existing thread if running
            if hasattr(self, "exercise_thread") and self.exercise_thread:
                self.stopped = True
                if self.exercise_thread.is_alive():
                    self.exercise_thread.join(timeout=2)
                self.stopped = False

            # Start the new exercise in a thread
            if hasattr(self, exercise_method):
                try:
                    method = getattr(self, exercise_method)
                    if callable(method):
                        # Start in a thread so it doesn't block API responses
                        if self.web_mode:
                            self.exercise_thread = threading.Thread(
                                target=method, daemon=True
                            )
                            self.exercise_thread.start()
                            print(
                                f"[ExercisesModule] Started new exercise thread for {exercise_method}"
                            )
                        else:
                            method()
                        return True
                    else:
                        raise ValueError(
                            f"'{exercise_method}' is not a callable method"
                        )
                except Exception as e:
                    print(f"Error starting exercise {exercise_method}: {str(e)}")
                    print(
                        f"Available methods: {[m for m in dir(self) if not m.startswith('_') and callable(getattr(self, m))]}"
                    )
                    return False
            else:
                available_methods = [
                    m
                    for m in dir(self)
                    if not m.startswith("_") and callable(getattr(self, m))
                ]
                print(f"Available exercise methods: {available_methods}")
                return False
        except Exception as e:
            print(f"[ExercisesModule] Error starting new exercise: {e}")
            import traceback

            traceback.print_exc()
            return False


# Dictionary to store active workout sessions
_active_sessions: Dict[str, "start_workout_session"] = {}


def get_workout_session(session_id: str) -> Optional["start_workout_session"]:
    """Get an active workout session by ID"""
    return _active_sessions.get(session_id)


class start_workout_session:
    # Class variable to store active sessions
    _active_sessions = {}

    @classmethod
    def get_workout_session(cls, session_id):
        """Get an active workout session by ID"""
        return cls._active_sessions.get(session_id)

    def __init__(
        self,
        sets=1,
        reps=6,
        camera_index=0,
        enable_recording=True,
        user_profile=None,
        exercise_type=None,
    ):
        print(f"Creating workout session with exercise: {exercise_type}")
        self.id = str(uuid.uuid4())  # Add unique session ID
        self.sets = sets
        self.reps = reps
        self.camera_index = camera_index
        self.enable_recording = enable_recording
        self.user_profile = (
            user_profile  # Store user profile for enhanced form analysis
        )
        self.exercise_type = exercise_type
        self.video_recorder = None
        self.total_reps = 0
        self.calories_burned = 0
        self.workout_complete = False

        # Track the completed exercises for recording in user profile
        self.completed_exercises = []

        # Initialize video recorder if recording is enabled
        if self.enable_recording:
            try:
                import VideoRecorder as vr

                self.video_recorder = vr.VideoRecorder()
                print(f"Video recorder initialized for session {self.id}")
            except Exception as e:
                print(f"Error initializing video recorder: {e}")

        # Initialize target exercises with exercise type
        try:
            self.target_exercises = simulate_target_exercies(
                sets=self.sets,
                reps=self.reps,
                camera_index=self.camera_index,
                exercise_type=self.exercise_type,
            )
            # Ensure the workout_complete property is initialized
            if not hasattr(self.target_exercises, "workout_complete"):
                self.target_exercises.workout_complete = False
        except Exception as e:
            print(f"Error initializing target exercises: {str(e)}")
            raise

        if self.user_profile:
            self.target_exercises.user_profile = self.user_profile

        # Add session to active sessions
        self.__class__._active_sessions[self.id] = self
        print(f"Created new session with ID: {self.id}")

    def process_frame(self, frame_rgb, pose_landmarks):
        """Process a single frame and update workout metrics"""
        if not self.exercise_type:
            raise ValueError("No exercise type specified")

        try:
            # Process frame with the target exercises module
            results = self.target_exercises.process_frame(frame_rgb)

            # Update our metrics from the target exercises
            self.total_reps = (
                self.target_exercises.total_reps
                if hasattr(self.target_exercises, "total_reps")
                else 0
            )
            self.calories_burned = (
                self.target_exercises.calories_burned
                if hasattr(self.target_exercises, "calories_burned")
                else 0
            )

            # Ensure workout_complete is propagated correctly
            results["workout_complete"] = (
                self.target_exercises.workout_complete
                if hasattr(self.target_exercises, "workout_complete")
                else False
            )

            return results
        except Exception as e:
            print(f"Error processing frame: {str(e)}")
            raise

    def get_metrics(self):
        """Get current workout metrics"""
        return {
            "reps_completed": self.total_reps,
            "calories_burned": self.calories_burned,
            "completion_percentage": (self.total_reps / (self.sets * self.reps)) * 100,
            "feedback": "Keep going! Maintain proper form.",
        }

    def __del__(self):
        """Cleanup when session is destroyed"""
        if self.id in self.__class__._active_sessions:
            del self.__class__._active_sessions[self.id]
            print(f"Removed session: {self.id}")

    def handle_video_options(self, final_video_path, user_email, user_name):
        """Handle video options for saving and emailing workout videos"""
        try:
            print(
                f"[WorkoutSession] Handling video options for {user_name} ({user_email}), exercise: {self.exercise_type}"
            )
            print(f"[WorkoutSession] Video path: {final_video_path}")

            if not self.video_recorder:
                print(f"[WorkoutSession] Error: Video recorder not initialized")
                # Create VideoRecorder if it doesn't exist
                try:
                    from VideoRecorder import VideoRecorder

                    self.video_recorder = VideoRecorder()
                    print("[WorkoutSession] Created video recorder")
                except Exception as e:
                    print(f"[WorkoutSession] Failed to create video recorder: {e}")
                    return False

            # Validate the video path
            if not final_video_path:
                print(f"[WorkoutSession] Error: No video path provided")
                return False

            if not os.path.exists(final_video_path):
                print(
                    f"[WorkoutSession] Error: Video file does not exist: {final_video_path}"
                )
                return False

            if os.path.getsize(final_video_path) == 0:
                print(
                    f"[WorkoutSession] Error: Video file is empty: {final_video_path}"
                )
                return False

            # Send the email with video attachment
            print(
                f"[WorkoutSession] Sending video to {user_email} for exercise: {self.exercise_type}"
            )

            # Always use the save_and_email method regardless of exercise type
            result = self.video_recorder.save_and_email(
                user_email, user_name, final_video_path
            )

            # Set videos as processed so cleanup will actually run
            if result:
                self.video_recorder._videos_processed = True

            # Try regular cleanup first
            try:
                cleanup_result = self.video_recorder.cleanup_temp_files()
                print(f"[WorkoutSession] Temp video cleanup result: {cleanup_result}")
            except Exception as cleanup_err:
                print(
                    f"[WorkoutSession] Error during temp video cleanup: {cleanup_err}"
                )

            # Force cleanup to make sure all files are removed regardless of flags
            try:
                force_cleanup_result = self.video_recorder.force_cleanup_temp_videos()
                print(f"[WorkoutSession] Force cleanup result: {force_cleanup_result}")
            except Exception as force_err:
                print(f"[WorkoutSession] Error during force cleanup: {force_err}")

            if result:
                print(
                    f"[WorkoutSession] Successfully sent video for {self.exercise_type} exercise"
                )
                return result
            else:
                print(f"[WorkoutSession] Failed to save and email video")
                return False
        except Exception as e:
            print(f"[WorkoutSession] Error in handle_video_options: {e}")
            import traceback

            traceback.print_exc()
            return False
