import cv2
import numpy as np
import random
import time
import mediapipe as mp
from WorkoutRecommender import WorkoutRecommender

# Initialize MediaPipe Pose globally for reuse
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)


class AIWorkoutCoach:
    def __init__(self):
        # Initialize MediaPipe components
        self.mp_pose = mp_pose
        self.pose = pose

        # Common mistakes database for different exercises
        self.exercise_mistakes = {
            "pushups": [
                {
                    "observation": "shoulders rising too high",
                    "advice": "Keep your shoulders down and away from your ears. Focus on maintaining a straight line from head to heels.",
                },
                {
                    "observation": "sagging lower back",
                    "advice": "Engage your core to maintain a straight body line. Don't let your hips sag toward the floor.",
                },
                {
                    "observation": "elbows flaring out",
                    "advice": "Keep your elbows closer to your body at about a 45-degree angle to reduce shoulder strain.",
                },
                {
                    "observation": "incomplete range of motion",
                    "advice": "Lower your chest all the way to just above the floor for a complete rep.",
                },
                {
                    "observation": "neck not neutral",
                    "advice": "Keep your gaze slightly forward and maintain a neutral neck position throughout the movement.",
                },
            ],
            "squats": [
                {
                    "observation": "knees caving inward",
                    "advice": "Focus on pushing your knees outward in line with your toes.",
                },
                {
                    "observation": "rising on toes",
                    "advice": "Keep your weight in your heels and midfoot. Don't let your heels come off the floor.",
                },
                {
                    "observation": "insufficient depth",
                    "advice": "Try to lower until your thighs are at least parallel to the floor for a full range of motion.",
                },
                {
                    "observation": "leaning too far forward",
                    "advice": "Keep your chest up and back straight. Imagine you're sliding down a wall.",
                },
                {
                    "observation": "knees extending past toes",
                    "advice": "Push your hips back as you descend to keep your knees behind or aligned with your toes.",
                },
            ],
            "bicep_curls": [
                {
                    "observation": "using momentum",
                    "advice": "Slow down and control the movement. Avoid swinging your body to lift the weight.",
                },
                {
                    "observation": "incomplete range of motion",
                    "advice": "Fully extend your arms at the bottom and fully contract at the top of each rep.",
                },
                {
                    "observation": "moving elbows",
                    "advice": "Keep your elbows fixed at your sides throughout the entire movement.",
                },
                {
                    "observation": "wrists bending",
                    "advice": "Keep your wrists straight and stable throughout the exercise.",
                },
                {
                    "observation": "shoulders rising",
                    "advice": "Relax your shoulders and keep them down away from your ears.",
                },
            ],
            "lunges": [
                {
                    "observation": "knee extending past toes",
                    "advice": "Take a longer step forward so your knee stays aligned with your ankle.",
                },
                {
                    "observation": "torso leaning forward",
                    "advice": "Keep your torso upright and core engaged throughout the movement.",
                },
                {
                    "observation": "back knee not low enough",
                    "advice": "Lower your back knee toward the floor for a full range of motion.",
                },
                {
                    "observation": "unstable balance",
                    "advice": "Focus on a spot ahead of you and engage your core for better balance.",
                },
                {
                    "observation": "hips not square",
                    "advice": "Keep your hips facing forward throughout the entire lunge.",
                },
            ],
            "mountain_climbers": [
                {
                    "observation": "hips rising too high",
                    "advice": "Maintain a straight line from head to heels as in a plank position.",
                },
                {
                    "observation": "uneven pace",
                    "advice": "Try to maintain a steady, controlled rhythm without pausing.",
                },
                {
                    "observation": "not bringing knees far enough",
                    "advice": "Bring your knees closer to your chest for a more effective exercise.",
                },
                {
                    "observation": "sagging lower back",
                    "advice": "Keep your core tight to prevent your lower back from sagging.",
                },
                {
                    "observation": "bouncing on toes",
                    "advice": "Keep a stable base with your hands and maintain control throughout.",
                },
            ],
        }

        # General encouragement phrases
        self.encouragement_phrases = [
            "Great work! Keep pushing!",
            "You're doing amazing! Keep it up!",
            "Stay strong, you've got this!",
            "Fantastic form! Keep going!",
            "You're making progress with every rep!",
            "Don't give up now, you're doing great!",
            "Push through the burn, it's worth it!",
            "Almost there! Finish strong!",
            "Your dedication is inspiring!",
            "Remember why you started! Keep going!",
            "Each rep brings you closer to your goals!",
            "That's it! Perfect form!",
            "You're stronger than you think!",
            "Keep up the awesome work!",
            "You're crushing this workout!",
        ]

        # Rest period recommendations based on exercise intensity
        self.rest_recommendations = {
            "high_intensity": {
                "between_sets": "Take 60-90 seconds rest between sets for optimal recovery.",
                "between_exercises": "Rest 2-3 minutes before moving to the next exercise.",
            },
            "moderate_intensity": {
                "between_sets": "Rest 30-60 seconds between sets to maintain good form.",
                "between_exercises": "Take 1-2 minutes before starting the next exercise.",
            },
            "low_intensity": {
                "between_sets": "A quick 15-30 second rest between sets is sufficient.",
                "between_exercises": "30-60 seconds rest before your next exercise should be enough.",
            },
        }

        # Tracking variables
        self.last_tip_time = 0
        self.tip_cooldown = 10  # seconds between tips
        self.last_encouragement_time = 0
        self.encouragement_cooldown = 15  # seconds between encouragement
        self.current_exercise = None
        self.current_intensity = "moderate_intensity"
        self.last_rest_recommendation_time = 0
        self.used_tips = set()  # Track used tips to avoid repetition

        # Initialize workout recommender
        self.workout_recommender = WorkoutRecommender()

    def set_exercise(self, exercise_name):
        """Set the current exercise being performed"""
        self.current_exercise = exercise_name.lower().replace(" ", "_")
        self.used_tips = set()  # Reset used tips for new exercise
        return True

    def set_intensity(self, intensity):
        """Set the current workout intensity"""
        if intensity in ["high_intensity", "moderate_intensity", "low_intensity"]:
            self.current_intensity = intensity
            return True
        return False

    def get_rest_recommendation(self, recommendation_type="between_sets"):
        """Get rest period recommendation based on current intensity"""
        current_time = time.time()

        # Only provide rest recommendations every 30 seconds
        if current_time - self.last_rest_recommendation_time < 30:
            return None

        self.last_rest_recommendation_time = current_time

        if recommendation_type in ["between_sets", "between_exercises"]:
            return self.rest_recommendations[self.current_intensity][
                recommendation_type
            ]
        return None

    def get_random_encouragement(self, progress_percentage=None):
        """Get random encouragement phrase, potentially based on progress"""
        current_time = time.time()

        # Limit frequency of encouragement
        if current_time - self.last_encouragement_time < self.encouragement_cooldown:
            return None

        self.last_encouragement_time = current_time

        # Special encouragement for different stages of the workout
        if progress_percentage is not None:
            if progress_percentage < 30:
                return "Great start! You're building momentum!"
            elif progress_percentage < 50:
                return "You're in the zone now! Keep pushing!"
            elif progress_percentage < 75:
                return "Over halfway there! You're doing amazing!"
            elif progress_percentage < 90:
                return "The finish line is in sight! Dig deep!"
            else:
                return "Final push! Give it everything you've got!"

        # Otherwise return random encouragement
        return random.choice(self.encouragement_phrases)

    def add_age_specific_form_advice(self, exercise_name, age, tip):
        """Add age-specific form advice for a particular exercise"""
        if exercise_name not in self.exercise_mistakes:
            return False

        # Convert age to int
        age_int = 0
        try:
            age_int = int(age)
        except (ValueError, TypeError):
            return False

        # Create age ranges
        if age_int < 18:
            age_group = "youth"
        elif age_int < 35:
            age_group = "young_adult"
        elif age_int < 50:
            age_group = "middle_age"
        elif age_int < 65:
            age_group = "senior"
        else:
            age_group = "elderly"

        # Append special tip to the exercise's advice
        if "age_specific_tips" not in self.exercise_mistakes[exercise_name]:
            self.exercise_mistakes[exercise_name]["age_specific_tips"] = {}

        if age_group not in self.exercise_mistakes[exercise_name]["age_specific_tips"]:
            self.exercise_mistakes[exercise_name]["age_specific_tips"][age_group] = []

        self.exercise_mistakes[exercise_name]["age_specific_tips"][age_group].append(
            tip
        )
        return True

    def add_body_type_advice(self, exercise_name, height, weight, tip):
        """Add body type-specific form advice for a particular exercise"""
        if exercise_name not in self.exercise_mistakes:
            return False

        # Calculate BMI
        try:
            height_m = float(height) / 100  # cm to m
            weight_kg = float(weight)
            bmi = weight_kg / (height_m * height_m)

            # Determine body type based on BMI (simplified approach)
            if bmi < 18.5:
                body_type = "slim"
            elif bmi < 25:
                body_type = "medium"
            elif bmi < 30:
                body_type = "heavy"
            else:
                body_type = "very_heavy"

            # Add body type-specific tip
            if "body_type_tips" not in self.exercise_mistakes[exercise_name]:
                self.exercise_mistakes[exercise_name]["body_type_tips"] = {}

            if body_type not in self.exercise_mistakes[exercise_name]["body_type_tips"]:
                self.exercise_mistakes[exercise_name]["body_type_tips"][body_type] = []

            self.exercise_mistakes[exercise_name]["body_type_tips"][body_type].append(
                tip
            )
            return True

        except (ValueError, TypeError, ZeroDivisionError):
            return False

    def analyze_form(self, pose_landmarks, exercise_name, user_profile=None):
        """Analyze exercise form based on pose landmarks and return detected issues
        Takes into account user's profile data for more personalized analysis"""
        if not pose_landmarks or not exercise_name:
            return []

        detected_issues = []

        # Get user metrics if available
        age = None
        height = None
        weight = None
        gender = None

        if user_profile:
            metrics = user_profile.get("body_metrics", {})
            age = metrics.get("age")
            height = metrics.get("height")
            weight = metrics.get("weight")
            gender = metrics.get("gender")

        # Simple example checks for squats
        if exercise_name.lower() == "squats":
            # Check if knees are caving inward (simplified example)
            if (
                random.random() < 0.2
            ):  # 20% chance to detect this issue for demo purposes
                detected_issues.append("knees caving inward")

            # Check if not going deep enough
            if random.random() < 0.3:
                detected_issues.append("insufficient depth")

            # Age-specific form checks for squats
            if age:
                try:
                    age_int = int(age)
                    if age_int > 60:
                        # Older adults may need modified squat depth
                        if (
                            random.random() < 0.4
                        ):  # Higher chance to detect in older adults
                            detected_issues.append(
                                "squat depth too low for senior users"
                            )
                except (ValueError, TypeError):
                    pass

            # Body type specific checks
            if height and weight:
                try:
                    height_m = float(height) / 100
                    weight_kg = float(weight)
                    bmi = weight_kg / (height_m * height_m)

                    if bmi > 30:
                        # Higher BMI individuals may have different optimal stance
                        if random.random() < 0.3:
                            detected_issues.append("stance too narrow for body type")
                except (ValueError, TypeError, ZeroDivisionError):
                    pass

        # Example checks for push-ups
        elif exercise_name.lower() == "push ups" or exercise_name.lower() == "pushups":
            if random.random() < 0.25:
                detected_issues.append("elbows flaring out")

            if random.random() < 0.2:
                detected_issues.append("sagging lower back")

            # Add age-specific checks
            if age:
                try:
                    age_int = int(age)
                    if age_int > 50:
                        # Modified pushup form may be needed for older adults
                        if random.random() < 0.3:
                            detected_issues.append(
                                "wrist position needs adjustment for comfort"
                            )
                except (ValueError, TypeError):
                    pass

            # Add gender-specific checks (simplified)
            if gender:
                if gender.lower() in ["female", "f", "woman"]:
                    # Women often have different upper body strength distribution
                    if random.random() < 0.2:
                        detected_issues.append("hand position too wide")
                elif gender.lower() in ["male", "m", "man"]:
                    if random.random() < 0.2:
                        detected_issues.append("not engaging chest muscles fully")

        # Example checks for bicep curls
        elif exercise_name.lower() == "bicep curls":
            if random.random() < 0.3:
                detected_issues.append("using momentum")

            if random.random() < 0.2:
                detected_issues.append("moving elbows")

            # Add body type specific check
            if height and weight:
                try:
                    height_m = float(height) / 100
                    weight_kg = float(weight)
                    bmi = weight_kg / (height_m * height_m)

                    if bmi < 18.5:
                        # Underweight individuals may need different form cues
                        if random.random() < 0.2:
                            detected_issues.append(
                                "consider using lighter weights with perfect form"
                            )
                except (ValueError, TypeError, ZeroDivisionError):
                    pass

        # Example checks for mountain climbers
        elif exercise_name.lower() == "mountain climbers":
            if random.random() < 0.3:
                detected_issues.append("hips rising too high")

            if random.random() < 0.25:
                detected_issues.append("uneven pace")

            # Add age-specific checks
            if age:
                try:
                    age_int = int(age)
                    if age_int > 55:
                        # High impact exercise cautions for older adults
                        if random.random() < 0.4:
                            detected_issues.append(
                                "consider lower impact version for joint health"
                            )
                except (ValueError, TypeError):
                    pass

        return detected_issues

    def get_difficulty_progression(
        self, exercise_name, current_performance, user_experience_level
    ):
        """Suggest progression for an exercise based on current performance"""
        if current_performance >= 90:  # Excellent performance
            if user_experience_level == "beginner":
                return f"You're doing great with {exercise_name}! Try adding 2-3 more reps next time."
            elif user_experience_level == "intermediate":
                return f"Excellent form! Consider adding another set or using a more challenging variation of {exercise_name}."
            else:  # advanced
                return f"Perfect execution! Try slowing down the eccentric (lowering) phase of each {exercise_name} rep for more intensity."

        elif current_performance >= 70:  # Good performance
            if user_experience_level == "beginner":
                return f"Good job! Focus on maintaining this quality for all reps of {exercise_name}."
            elif user_experience_level == "intermediate":
                return f"Solid work! Try increasing your rep count by 1-2 for each set of {exercise_name}."
            else:  # advanced
                return f"Strong performance! Consider adding a short pause at the most challenging point of each {exercise_name} rep."

        else:  # Needs improvement
            if user_experience_level == "beginner":
                return f"Focus on quality over quantity with {exercise_name}. Reduce reps if needed to maintain good form."
            elif user_experience_level == "intermediate":
                return f"Let's refine your {exercise_name} technique. Consider dropping back on weight/intensity to perfect your form."
            else:  # advanced
                return f"Everyone has off days. For your next {exercise_name} session, focus on rebuilding your foundation with perfect technique."

    def get_next_workout_recommendation(self, email):
        """Get personalized workout recommendation for user"""
        try:
            user_recommendation = (
                self.workout_recommender.generate_user_recommendation_message(email)
            )

            # Load user profile to include personal metrics in the recommendation
            profile = self.workout_recommender.user_profile_manager.load_profile(email)
            if profile and "body_metrics" in profile:
                metrics = profile["body_metrics"]
                age = metrics.get("age")
                gender = metrics.get("gender")
                weight = metrics.get("weight")
                height = metrics.get("height")

                # Add personalized tips based on metrics
                additional_tips = []

                if all([age, gender, weight, height]):
                    # Create more personalized tips based on the user's metrics
                    try:
                        age_int = int(age)
                        weight_float = float(weight)
                        height_float = float(height)

                        # For older users
                        if age_int > 50:
                            additional_tips.append(
                                "As you're over 50, make sure to warm up properly and focus on mobility exercises."
                            )

                        # BMI-based recommendations (simplified)
                        if height_float > 0:
                            bmi = weight_float / ((height_float / 100) ** 2)
                            if bmi > 25:
                                additional_tips.append(
                                    "Including more cardiovascular exercise could help with weight management."
                                )
                            elif bmi < 18.5:
                                additional_tips.append(
                                    "Consider adding strength training to build muscle mass."
                                )

                        # Gender-specific tips
                        if gender.lower() in ["female", "f", "woman"]:
                            additional_tips.append(
                                "Women typically benefit from resistance training to improve bone density."
                            )
                        elif gender.lower() in ["male", "m", "man"]:
                            additional_tips.append(
                                "Men often benefit from including flexibility work in their routine."
                            )

                    except (ValueError, TypeError):
                        # Handle conversion errors silently
                        pass

                # Add the personalized tips to the recommendation
                if additional_tips:
                    user_recommendation += "\n\n===== PERSONALIZED TIPS =====\n"
                    for tip in additional_tips:
                        user_recommendation += f"• {tip}\n"

            return user_recommendation
        except Exception as e:
            # Fallback recommendation if there's an error
            return "I recommend a balanced workout including Warm Up, Squats, Push Ups, and Mountain Climbers. Aim for 2-3 sets of 8-12 reps for each exercise, with 60 seconds rest between sets."

    def get_exercise_tip(self, detected_issues=None, user_profile=None):
        """Get personalized tip based on the current exercise or detected issues and user profile"""
        current_time = time.time()

        # Limit frequency of tips
        if current_time - self.last_tip_time < self.tip_cooldown:
            return None

        self.last_tip_time = current_time

        if self.current_exercise not in self.exercise_mistakes:
            return None

        # Get user metrics if available
        age = None
        height = None
        weight = None
        gender = None

        if user_profile:
            metrics = user_profile.get("body_metrics", {})
            age = metrics.get("age")
            height = metrics.get("height")
            weight = metrics.get("weight")
            gender = metrics.get("gender")

        # If specific issues were detected, prioritize those
        if detected_issues and self.current_exercise:
            for issue in detected_issues:
                for mistake in self.exercise_mistakes[self.current_exercise]:
                    if isinstance(mistake, dict) and "observation" in mistake:
                        if issue.lower() in mistake["observation"].lower():
                            if mistake["observation"] not in self.used_tips:
                                self.used_tips.add(mistake["observation"])
                                return f"Tip: I noticed {mistake['observation']}. {mistake['advice']}"

        # Check for age-specific tips
        if age and self.current_exercise:
            try:
                age_int = int(age)

                # Determine age group
                if age_int < 18:
                    age_group = "youth"
                elif age_int < 35:
                    age_group = "young_adult"
                elif age_int < 50:
                    age_group = "middle_age"
                elif age_int < 65:
                    age_group = "senior"
                else:
                    age_group = "elderly"

                # Look for age-specific tips
                age_tips = (
                    self.exercise_mistakes.get(self.current_exercise, {})
                    .get("age_specific_tips", {})
                    .get(age_group, [])
                )

                if age_tips:
                    tip = random.choice(age_tips)
                    return f"Age-Specific Tip: {tip}"

            except (ValueError, TypeError):
                pass

        # Check for body type-specific tips
        if height and weight and self.current_exercise:
            try:
                height_m = float(height) / 100
                weight_kg = float(weight)
                bmi = weight_kg / (height_m * height_m)

                # Determine body type
                if bmi < 18.5:
                    body_type = "slim"
                elif bmi < 25:
                    body_type = "medium"
                elif bmi < 30:
                    body_type = "heavy"
                else:
                    body_type = "very_heavy"

                # Look for body type-specific tips
                body_tips = (
                    self.exercise_mistakes.get(self.current_exercise, {})
                    .get("body_type_tips", {})
                    .get(body_type, [])
                )

                if body_tips:
                    tip = random.choice(body_tips)
                    return f"Body Type Tip: {tip}"

            except (ValueError, TypeError, ZeroDivisionError):
                pass

        # Otherwise give a random tip that hasn't been used yet
        available_tips = [
            tip
            for tip in self.exercise_mistakes[self.current_exercise]
            if isinstance(tip, dict)
            and "observation" in tip
            and tip["observation"] not in self.used_tips
        ]

        if not available_tips:  # If all tips have been used, reset
            self.used_tips = set()
            available_tips = [
                tip
                for tip in self.exercise_mistakes[self.current_exercise]
                if isinstance(tip, dict) and "observation" in tip
            ]

        if available_tips:
            tip = random.choice(available_tips)
            self.used_tips.add(tip["observation"])
            return f"Tip: Watch out for {tip['observation']}. {tip['advice']}"

        return None

    def overlay_coach_feedback(
        self, frame, feedback_text, position=(50, 50), color=(255, 255, 255)
    ):
        """Overlay coach feedback on the video frame"""
        if not feedback_text:
            return frame

        # Create a semi-transparent background for the text
        text_size, _ = cv2.getTextSize(feedback_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        text_w, text_h = text_size

        # Position the text at the bottom of the frame with padding
        if position == "auto":
            position = (int((frame.shape[1] - text_w) / 2), frame.shape[0] - 30)

        # Create overlay background
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (position[0] - 10, position[1] - text_h - 10),
            (position[0] + text_w + 10, position[1] + 10),
            (0, 0, 0),
            -1,
        )

        # Apply the overlay with transparency
        alpha = 0.7
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # Add the text
        cv2.putText(
            frame, feedback_text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2
        )

        return frame
