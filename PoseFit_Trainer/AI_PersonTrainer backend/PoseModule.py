import mediapipe as mp
import math
import cv2


class posture_detector():
    def __init__(self, mode=False, up_body=False, smooth=True,
                 detection_con=0.5, track_con=0.5):
        self.mode = mode
        self.up_body = up_body
        self.smooth = smooth
        self.detection_con = detection_con
        self.track_con = track_con

        self.mp_draw = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        # Minimal drawing specs for better performance
        self.drawing_spec = self.mp_draw.DrawingSpec(
            thickness=1,
            circle_radius=1
        )
        # Initialize pose with performance-optimized parameters
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,  # Always use video mode for better performance
            model_complexity=1,  # Use medium complexity model for balance of accuracy and speed
            smooth_landmarks=True,
            enable_segmentation=False,
            min_detection_confidence=detection_con,
            min_tracking_confidence=track_con
        )

    def find_person(self, img, draw: bool = True):
        # Process at a lower resolution for better performance
        h, w = img.shape[:2]
        if w > 640:  # Only resize if image is large
            scale = 640 / w
            new_w, new_h = int(w * scale), int(h * scale)
            small_img = cv2.resize(img, (new_w, new_h))
            img_rgb = cv2.cvtColor(small_img, cv2.COLOR_BGR2RGB)
        else:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
        self.results = self.pose.process(img_rgb)
        if self.results.pose_landmarks and draw:
            self.mp_draw.draw_landmarks(
                img,
                self.results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                self.drawing_spec,
                self.drawing_spec
            )
        return img

    def find_landmarks(self, img, draw: bool = True):
        self.landmark_list = []
        if self.results.pose_landmarks:
            h, w = img.shape[:2]
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.landmark_list.append([id, cx, cy, lm.visibility])
                if draw and lm.visibility > 0.5:  # Only draw highly visible landmarks
                    cv2.circle(img, (cx, cy), 2, (0, 255, 0), 1)
        return self.landmark_list

    def get_landmark_visibility(self, landmark_id):
        """Get the visibility score for a specific landmark"""
        if self.results.pose_landmarks and 0 <= landmark_id < len(self.results.pose_landmarks.landmark):
            return self.results.pose_landmarks.landmark[landmark_id].visibility
        return 0

    # Given any three points/co-ordinates, it gives us an angle(joint)
    def find_angle(self, img, p1, p2, p3, draw=True):
        x1, y1 = self.landmark_list[p1][1:3]
        x2, y2 = self.landmark_list[p2][1:3]
        x3, y3 = self.landmark_list[p3][1:3]
        
        # Calculate the Angle
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) -
                           math.atan2(y1 - y2, x1 - x2))
        if angle < 0:
            angle += 360

        # Minimal drawing for better performance
        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 1)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 1)
            cv2.circle(img, (x2, y2), 3, (0, 0, 255), 1)
        return angle


def main():
    cap = cv2.VideoCapture('PoseVideos/bicep_curls_1.mp4')
    detector = posture_detector()
    while True:
        success, img = cap.read()
        img = detector.find_person(img)
        landmark_list = detector.find_landmarks(img, draw=False)
        print(landmark_list)
        if len(landmark_list) != 0:
            print(landmark_list[14])
            cv2.circle(
                img, (landmark_list[14][1], landmark_list[14][2]), 15, (0, 0, 255), cv2.FILLED)

        cv2.imshow("Image", img)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break


if __name__ == "__main__":
    main()
