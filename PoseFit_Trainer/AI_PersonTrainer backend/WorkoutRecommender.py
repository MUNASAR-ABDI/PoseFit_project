import json
import os
import numpy as np
import random
from datetime import datetime, timedelta
from UserProfile import UserProfileManager


class WorkoutRecommender:
    def __init__(self):
        self.user_profile_manager = UserProfileManager()

        # Exercise difficulty ratings (1-10 scale)
        self.exercise_difficulty = {
            "Warm Up": 1,
            "Squats": 5,
            "Mountain Climbers": 7,
            "Bicep Curls": 4,
            "Push Ups": 6,
        }

        # Exercise muscle groups
        self.exercise_muscle_groups = {
            "Warm Up": ["full body"],
            "Squats": ["quadriceps", "glutes", "hamstrings", "core"],
            "Mountain Climbers": ["core", "shoulders", "chest", "hip flexors"],
            "Bicep Curls": ["biceps", "forearms"],
            "Push Ups": ["chest", "shoulders", "triceps", "core"],
        }

        # Exercise progression patterns (sets and reps)
        self.progression_patterns = {
            "beginner": {
                "sets_range": (1, 3),
                "reps_range": (5, 10),
                "rest_between_sets": 60,  # seconds
                "workout_frequency": 3,  # per week
            },
            "intermediate": {
                "sets_range": (3, 4),
                "reps_range": (8, 15),
                "rest_between_sets": 45,  # seconds
                "workout_frequency": 4,  # per week
            },
            "advanced": {
                "sets_range": (4, 5),
                "reps_range": (12, 20),
                "rest_between_sets": 30,  # seconds
                "workout_frequency": 5,  # per week
            },
        }

        # Workout templates by goal
        self.workout_templates = {
            "strength": {
                "focus": ["Push Ups", "Squats", "Bicep Curls"],
                "sets_multiplier": 1.2,
                "reps_divisor": 1.2,  # fewer reps, more sets for strength
            },
            "endurance": {
                "focus": ["Mountain Climbers", "Squats", "Push Ups"],
                "sets_multiplier": 0.8,
                "reps_divisor": 0.8,  # more reps, fewer sets for endurance
            },
            "weight_loss": {
                "focus": ["Mountain Climbers", "Squats", "Push Ups"],
                "sets_multiplier": 1.0,
                "reps_divisor": 0.9,  # slightly more reps for calorie burn
            },
            "general_fitness": {
                "focus": ["Warm Up", "Squats", "Push Ups", "Bicep Curls"],
                "sets_multiplier": 1.0,
                "reps_divisor": 1.0,  # balanced approach
            },
        }

    def get_user_fitness_level(self, email):
        """Determine user's fitness level based on profile data and workout history"""
        profile = self.user_profile_manager.load_profile(email)
        if not profile:
            return "beginner"

        # Check if user has specified a fitness level
        if profile["body_metrics"]["fitness_level"]:
            return profile["body_metrics"]["fitness_level"]

        # Otherwise infer from workout history
        history = profile["workout_history"]
        if not history:
            return "beginner"

        total_workouts = len(history)
        avg_completion = sum(w.get("rep_completion", 0) for w in history) / max(
            1, total_workouts
        )

        if total_workouts >= 20 and avg_completion > 85:
            return "advanced"
        elif total_workouts >= 10 and avg_completion > 75:
            return "intermediate"
        else:
            return "beginner"

    def infer_user_goal(self, email):
        """Infer user's fitness goal based on workout patterns"""
        profile = self.user_profile_manager.load_profile(email)
        if not profile or not profile["workout_history"]:
            return "general_fitness"  # Default goal

        # Check preferences if they exist
        if "fitness_goal" in profile.get("preferences", {}):
            return profile["preferences"]["fitness_goal"]

        # Otherwise infer from history patterns
        history = profile["workout_history"]

        # Analyze exercise choices
        exercise_counts = {}
        for workout in history:
            for exercise in workout.get("exercises", []):
                name = exercise.get("name", "")
                if name:
                    exercise_counts[name] = exercise_counts.get(name, 0) + 1

        # If no exercises recorded yet
        if not exercise_counts:
            return "general_fitness"

        # Check for focus on strength exercises
        strength_focus = sum(
            exercise_counts.get(ex, 0) for ex in ["Push Ups", "Bicep Curls"]
        )
        endurance_focus = sum(
            exercise_counts.get(ex, 0) for ex in ["Mountain Climbers"]
        )

        # Calculate workout intensity metrics
        avg_reps = 0
        avg_sets = 0
        workout_count = 0

        for workout in history:
            if "exercises" in workout:
                workout_count += 1
                for exercise in workout["exercises"]:
                    if "sets" in exercise and "reps" in exercise:
                        avg_sets += exercise["sets"]
                        avg_reps += exercise["reps"]

        if workout_count > 0:
            avg_sets /= workout_count
            avg_reps /= workout_count

        # Determine goal based on metrics
        if strength_focus > endurance_focus and avg_reps < 10:
            return "strength"
        elif endurance_focus > strength_focus and avg_reps > 12:
            return "endurance"
        elif profile.get("body_metrics", {}).get("weight") and avg_reps > 10:
            return "weight_loss"
        else:
            return "general_fitness"

    def get_exercise_history(self, email, days=30):
        """Get exercise frequency in the past month"""
        profile = self.user_profile_manager.load_profile(email)
        if not profile:
            return {}

        history = profile.get("workout_history", [])

        # Calculate date threshold (30 days ago)
        threshold_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # Count occurrences of each exercise in recent history
        exercise_counts = {}
        for workout in history:
            workout_date = workout.get("date", "").split()[0]  # Get just the date part
            if workout_date >= threshold_date:
                for exercise in workout.get("exercises", []):
                    name = exercise.get("name", "")
                    if name:
                        exercise_counts[name] = exercise_counts.get(name, 0) + 1

        return exercise_counts

    def get_performance_metrics(self, email):
        """Get performance metrics for each exercise"""
        profile = self.user_profile_manager.load_profile(email)
        if not profile:
            return {}

        history = profile.get("workout_history", [])
        if not history:
            return {}

        # Track best and average performance by exercise
        performance_metrics = {}

        for workout in history:
            for exercise in workout.get("exercises", []):
                name = exercise.get("name", "")
                if not name:
                    continue

                if name not in performance_metrics:
                    performance_metrics[name] = {
                        "best_reps": 0,
                        "best_sets": 0,
                        "avg_reps": 0,
                        "avg_sets": 0,
                        "count": 0,
                        "completion_rate": 0,
                    }

                metrics = performance_metrics[name]
                metrics["count"] += 1

                # Update best performances
                if exercise.get("reps", 0) > metrics["best_reps"]:
                    metrics["best_reps"] = exercise.get("reps", 0)

                if exercise.get("sets", 0) > metrics["best_sets"]:
                    metrics["best_sets"] = exercise.get("sets", 0)

                # Update running average
                metrics["avg_reps"] = (
                    metrics["avg_reps"] * (metrics["count"] - 1)
                    + exercise.get("reps", 0)
                ) / metrics["count"]
                metrics["avg_sets"] = (
                    metrics["avg_sets"] * (metrics["count"] - 1)
                    + exercise.get("sets", 0)
                ) / metrics["count"]

                # Track completion rate
                if "rep_completion" in exercise:
                    metrics["completion_rate"] = (
                        metrics["completion_rate"] * (metrics["count"] - 1)
                        + exercise["rep_completion"]
                    ) / metrics["count"]

        return performance_metrics

    def identify_strengths_weaknesses(self, email):
        """Identify user's strengths and areas for improvement"""
        performance = self.get_performance_metrics(email)
        if not performance:
            return {"strengths": [], "weaknesses": []}

        # Calculate overall performance score for each exercise
        exercise_scores = {}
        for exercise, metrics in performance.items():
            if metrics["count"] < 2:  # Need at least two data points
                continue

            # Calculate performance score based on completion rate and progression
            completion_score = metrics["completion_rate"] / 100
            progression_score = (
                metrics["best_reps"] / max(1, metrics["avg_reps"])
            ) * 0.5

            # Weight by difficulty
            difficulty = self.exercise_difficulty.get(exercise, 5) / 10

            # Calculate overall score
            exercise_scores[exercise] = (
                completion_score + progression_score
            ) * difficulty

        if not exercise_scores:
            return {"strengths": [], "weaknesses": []}

        # Sort exercises by score
        sorted_exercises = sorted(
            exercise_scores.items(), key=lambda x: x[1], reverse=True
        )

        # Identify top 30% as strengths and bottom 30% as weaknesses
        cutoff = max(1, len(sorted_exercises) // 3)

        return {
            "strengths": [ex[0] for ex in sorted_exercises[:cutoff]],
            "weaknesses": [ex[0] for ex in sorted_exercises[-cutoff:]],
        }

    def analyze_muscle_balance(self, email):
        """Analyze muscle group balance from workout history"""
        profile = self.user_profile_manager.load_profile(email)
        if not profile:
            return {}

        history = profile.get("workout_history", [])

        # Count muscle group frequency
        muscle_counts = {}

        for workout in history:
            for exercise in workout.get("exercises", []):
                name = exercise.get("name", "")
                if not name or name not in self.exercise_muscle_groups:
                    continue

                for muscle in self.exercise_muscle_groups[name]:
                    muscle_counts[muscle] = muscle_counts.get(muscle, 0) + 1

        return muscle_counts

    def recommend_next_workout(self, email):
        """Generate a personalized workout recommendation"""
        profile = self.user_profile_manager.load_profile(email)
        if not profile:
            return self._generate_default_workout()

        # Get user's fitness level
        fitness_level = self.get_user_fitness_level(email)

        # Infer user's goal
        fitness_goal = self.infer_user_goal(email)

        # Get exercise history to avoid excessive repetition
        recent_exercises = self.get_exercise_history(email, days=7)

        # Get strengths and weaknesses
        assessment = self.identify_strengths_weaknesses(email)
        weaknesses = assessment["weaknesses"]

        # Analyze muscle balance
        muscle_balance = self.analyze_muscle_balance(email)

        # Find underworked muscle groups
        all_muscles = set()
        for muscles in self.exercise_muscle_groups.values():
            all_muscles.update(muscles)

        underworked_muscles = []
        for muscle in all_muscles:
            if muscle not in muscle_balance or muscle_balance[muscle] < 3:
                underworked_muscles.append(muscle)

        # Get body metrics for personalized adjustments
        body_metrics = profile.get("body_metrics", {})
        age = body_metrics.get("age")
        gender = body_metrics.get("gender", "").lower()
        weight = body_metrics.get("weight")
        height = body_metrics.get("height")

        # Adjust workout based on metrics if available
        age_adjusted_intensity = 1.0
        gender_adjusted_focus = None

        if age:
            try:
                age_int = int(age)
                # Reduce intensity for older users
                if age_int > 60:
                    age_adjusted_intensity = 0.7
                elif age_int > 50:
                    age_adjusted_intensity = 0.8
                elif age_int > 40:
                    age_adjusted_intensity = 0.9
                # Youth may need more guidance
                elif age_int < 18:
                    age_adjusted_intensity = 0.8
            except (ValueError, TypeError):
                pass

        if gender:
            # Adjust focus based on common gender-based goals
            # This is a simplified approach - individual goals always override this
            if gender in ["female", "f", "woman"]:
                gender_adjusted_focus = ["core", "glutes", "lower body"]
            elif gender in ["male", "m", "man"]:
                gender_adjusted_focus = ["chest", "upper body", "core"]

        # Find exercises that target underworked muscles or weaknesses
        priority_exercises = []
        if underworked_muscles:
            for exercise, muscles in self.exercise_muscle_groups.items():
                if any(muscle in underworked_muscles for muscle in muscles):
                    priority_exercises.append(exercise)

        # Include exercises from weaknesses
        priority_exercises.extend(weaknesses)

        # Include gender-focused exercises if applicable
        if gender_adjusted_focus:
            for exercise, muscles in self.exercise_muscle_groups.items():
                if any(focus in muscles for focus in gender_adjusted_focus):
                    if exercise not in priority_exercises:
                        priority_exercises.append(exercise)

        # Ensure some variety by including some exercises from the user's goal template
        goal_exercises = self.workout_templates[fitness_goal]["focus"]

        # Combine all exercise sources with priorities
        exercise_pool = list(
            set(
                priority_exercises
                + goal_exercises
                + list(self.exercise_difficulty.keys())
            )
        )

        # Deprioritize recently performed exercises
        exercise_pool.sort(key=lambda ex: recent_exercises.get(ex, 0))

        # Select 3-5 exercises for the workout
        num_exercises = random.randint(3, min(5, len(exercise_pool)))
        selected_exercises = exercise_pool[:num_exercises]

        # Always include Warm Up if it's not already selected
        if "Warm Up" not in selected_exercises:
            selected_exercises = ["Warm Up"] + selected_exercises[: num_exercises - 1]

        # Get progression pattern based on fitness level
        progression = self.progression_patterns[fitness_level]

        # Apply goal-specific modifiers
        goal_modifier = self.workout_templates[fitness_goal]
        sets_multiplier = goal_modifier["sets_multiplier"] * age_adjusted_intensity
        reps_divisor = goal_modifier["reps_divisor"]

        # Generate the workout plan
        workout_plan = []
        for exercise in selected_exercises:
            # For Warm Up, always use minimal sets/reps
            if exercise == "Warm Up":
                sets = 1
                reps = 5
            else:
                # Determine sets and reps based on fitness level and goal
                base_sets = random.randint(*progression["sets_range"])
                base_reps = random.randint(*progression["reps_range"])

                sets = max(1, int(base_sets * sets_multiplier))
                reps = max(5, int(base_reps / reps_divisor))

            workout_plan.append(
                {
                    "name": exercise,
                    "sets": sets,
                    "reps": reps,
                    "rest": progression["rest_between_sets"],
                }
            )

        return {
            "fitness_level": fitness_level,
            "fitness_goal": fitness_goal,
            "workout_plan": workout_plan,
            "focus_areas": weaknesses if weaknesses else ["general fitness"],
            "recommended_frequency": progression["workout_frequency"],
        }

    def _generate_default_workout(self):
        """Generate a default workout for new users"""
        progression = self.progression_patterns["beginner"]

        workout_plan = [
            {"name": "Warm Up", "sets": 1, "reps": 5, "rest": 30},
            {
                "name": "Squats",
                "sets": 2,
                "reps": 8,
                "rest": progression["rest_between_sets"],
            },
            {
                "name": "Push Ups",
                "sets": 2,
                "reps": 8,
                "rest": progression["rest_between_sets"],
            },
            {
                "name": "Mountain Climbers",
                "sets": 2,
                "reps": 10,
                "rest": progression["rest_between_sets"],
            },
        ]

        return {
            "fitness_level": "beginner",
            "fitness_goal": "general_fitness",
            "workout_plan": workout_plan,
            "focus_areas": ["general fitness"],
            "recommended_frequency": progression["workout_frequency"],
        }

    def generate_user_recommendation_message(self, email):
        """Generate a human-readable recommendation message"""
        recommendation = self.recommend_next_workout(email)

        profile = self.user_profile_manager.load_profile(email)
        name = profile["first_name"] if profile else "there"

        message = f"Hi {name}! Here's your personalized workout recommendation:\n\n"

        # Add fitness info
        message += f"Fitness Level: {recommendation['fitness_level'].capitalize()}\n"
        message += (
            f"Goal: {recommendation['fitness_goal'].replace('_', ' ').capitalize()}\n"
        )
        message += f"Recommended Frequency: {recommendation['recommended_frequency']} times per week\n\n"

        # Add workout plan
        message += "YOUR WORKOUT PLAN:\n"
        for i, exercise in enumerate(recommendation["workout_plan"], 1):
            message += f"{i}. {exercise['name']}: {exercise['sets']} sets of {exercise['reps']} reps "
            message += f"(Rest: {exercise['rest']} seconds between sets)\n"

        # Add focus areas
        if recommendation["focus_areas"]:
            message += "\nFocus Areas: " + ", ".join(
                area.capitalize() for area in recommendation["focus_areas"]
            )

        return message


# Usage example
if __name__ == "__main__":
    recommender = WorkoutRecommender()
    # Example email that would exist in your system
    email = "test@example.com"
    recommendation = recommender.recommend_next_workout(email)
    message = recommender.generate_user_recommendation_message(email)
    print(message)
