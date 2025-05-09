import json
import os
import datetime
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import shutil


class UserProfileManager:
    def __init__(self):
        self.profiles_folder = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "user_profiles"
        )
        if not os.path.exists(self.profiles_folder):
            os.makedirs(self.profiles_folder)

        # Create charts and dashboards directories
        self.charts_dir = os.path.join(self.profiles_folder, "charts")
        self.dashboards_dir = os.path.join(self.profiles_folder, "dashboards")
        if not os.path.exists(self.charts_dir):
            os.makedirs(self.charts_dir)
        if not os.path.exists(self.dashboards_dir):
            os.makedirs(self.dashboards_dir)

    def ensure_profiles_directory(self):
        """Ensure the profiles directory exists"""
        if not os.path.exists(self.profiles_folder):
            os.makedirs(self.profiles_folder)
            print(f"Created profiles directory: {self.profiles_folder}")

    def create_user_profile(
        self,
        email,
        first_name,
        last_name,
        age=None,
        gender=None,
        weight=None,
        height=None,
    ):
        """Create a new user profile or return existing one"""
        user_id = email.lower().replace("@", "_at_").replace(".", "_dot_")
        profile_path = os.path.join(self.profiles_folder, f"{user_id}.json")

        if os.path.exists(profile_path):
            print(f"Profile already exists for {email}")
            return self.load_profile(email)

        # Calculate BMI if weight and height are provided
        bmi = None
        bmi_category = None
        if weight and height:
            try:
                bmi = self.calculate_bmi(float(weight), float(height))
                bmi_category = self.get_bmi_category(bmi)
            except (ValueError, TypeError):
                pass

        # Create new profile with default values
        profile = {
            "user_id": user_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "goals": {
                "weekly_workouts": 3,
                "calories_per_workout": 200,
                "minutes_per_workout": 30,
                "target_weight": None,
                "fitness_goal_type": "general_fitness",  # general_fitness, weight_loss, muscle_gain, endurance
            },
            "preferences": {
                "preferred_exercises": [],
                "rest_time_between_sets": 30,  # seconds
                "difficulty_level": "beginner",  # beginner, intermediate, advanced
            },
            "workout_history": [],
            "stats": {
                "total_workouts": 0,
                "total_calories": 0,
                "total_time": 0,
                "total_reps": 0,
                "favorite_exercise": None,
            },
            "body_metrics": {
                "weight": weight,  # kg
                "height": height,  # cm
                "age": age,
                "gender": gender,
                "bmi": bmi,
                "bmi_category": bmi_category,
                "fitness_level": "beginner",  # beginner, intermediate, advanced
            },
        }

        # Save the profile
        with open(profile_path, "w") as f:
            json.dump(profile, f, indent=2)

        print(f"Created new profile for {email}")
        return profile

    def calculate_bmi(self, weight, height):
        """Calculate BMI (Body Mass Index) from weight (kg) and height (cm)"""
        if not weight or not height or height <= 0:
            return None

        # Convert height from cm to meters
        height_m = height / 100

        # BMI formula: weight(kg) / height(m)²
        bmi = weight / (height_m * height_m)

        # Round to 1 decimal place
        return round(bmi, 1)

    def get_bmi_category(self, bmi):
        """Get BMI category and health assessment"""
        if bmi is None:
            return None

        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal weight"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"

    def get_health_assessment(self, bmi):
        """Get detailed health assessment based on BMI"""
        if bmi is None:
            return "No health assessment available without weight and height data."

        if bmi < 18.5:
            return (
                "Your BMI indicates you are underweight. This may suggest insufficient calorie intake or other health issues. "
                "Consider focusing on nutrient-dense foods and strength training to build muscle mass."
            )

        elif bmi < 25:
            return (
                "Your BMI is in the healthy range. Maintain your current habits with a balanced diet and regular exercise. "
                "Focus on a mix of cardio and strength training for overall fitness."
            )

        elif bmi < 30:
            return (
                "Your BMI indicates you are overweight. Consider increasing physical activity and adjusting your diet. "
                "Aim for a moderate calorie deficit and include both cardio and strength training in your routine."
            )

        else:
            return (
                "Your BMI indicates obesity, which increases risk for several health conditions. "
                "Consider consulting a healthcare professional. Focus on sustainable lifestyle changes including regular physical activity and balanced nutrition."
            )

    def update_bmi(self, profile):
        """Update BMI when weight or height changes"""
        if not profile:
            return profile

        metrics = profile.get("body_metrics", {})
        weight = metrics.get("weight")
        height = metrics.get("height")

        if weight and height:
            try:
                # Convert to float in case they're stored as strings
                weight_float = float(weight)
                height_float = float(height)

                # Update BMI and category
                metrics["bmi"] = self.calculate_bmi(weight_float, height_float)
                metrics["bmi_category"] = self.get_bmi_category(metrics["bmi"])

                # Update profile with new metrics
                profile["body_metrics"] = metrics
            except (ValueError, TypeError):
                pass

        return profile

    def load_profile(self, email):
        """Load a user profile from file"""
        try:
            # Convert email to safe filename
            user_id = email.replace("@", "_at_").replace(".", "_dot_")
            profile_path = os.path.join(self.profiles_folder, f"{user_id}.json")

            # If profile doesn't exist, try to create it from user_data.json
            if not os.path.exists(profile_path):
                user_data_path = os.path.join(
                    os.path.dirname(self.profiles_folder), "user_data.json"
                )
                if os.path.exists(user_data_path):
                    with open(user_data_path, "r") as f:
                        user_data = json.load(f)
                    if email in user_data:
                        # Create basic profile
                        profile = {
                            "user_id": user_id,
                            "email": email,
                            "first_name": user_data[email]["first_name"],
                            "last_name": user_data[email]["last_name"],
                            "body_metrics": {
                                "weight": float(user_data[email]["weight"]),
                                "height": float(user_data[email]["height"]),
                                "age": int(user_data[email]["age"]),
                                "gender": user_data[email]["gender"],
                            },
                            "workout_history": [],
                            "goals": {
                                "weekly_workouts": 3,
                                "calories_per_workout": 200,
                                "minutes_per_workout": 30,
                            },
                        }

                        # Calculate BMI
                        height_m = float(user_data[email]["height"]) / 100
                        weight_kg = float(user_data[email]["weight"])
                        bmi = weight_kg / (height_m * height_m)
                        profile["body_metrics"]["bmi"] = round(bmi, 1)

                        # Determine BMI category
                        if bmi < 18.5:
                            profile["body_metrics"]["bmi_category"] = "Underweight"
                        elif bmi < 25:
                            profile["body_metrics"]["bmi_category"] = "Normal weight"
                        elif bmi < 30:
                            profile["body_metrics"]["bmi_category"] = "Overweight"
                        else:
                            profile["body_metrics"]["bmi_category"] = "Obese"

                        # Save the new profile
                        with open(profile_path, "w") as f:
                            json.dump(profile, f, indent=4)
                        return profile

            # Load existing profile
            if os.path.exists(profile_path):
                with open(profile_path, "r") as f:
                    return json.load(f)

        except Exception as e:
            print(f"Error loading profile: {e}")
        return None

    def save_profile(self, profile):
        """Save profile data to file"""
        user_id = profile["user_id"]
        profile_path = os.path.join(self.profiles_folder, f"{user_id}.json")

        with open(profile_path, "w") as f:
            json.dump(profile, f, indent=2)

        return True

    def record_workout(self, email, workout_data):
        """Record a workout in the user's profile"""
        profile = self.load_profile(email)
        if not profile:
            print(f"Cannot record workout. Profile not found for {email}")
            return False

        # Create workout record
        workout = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "exercises": workout_data.get("exercises", []),
            "calories": workout_data.get("calories", 0),
            "time_elapsed": workout_data.get("time_elapsed", 0),
            "reps_completed": workout_data.get("reps_completed", 0),
            "total_reps": workout_data.get("total_reps", 0),
            "rep_completion": workout_data.get("rep_completion", 0),
        }

        # Add workout to history
        profile["workout_history"].append(workout)

        # Update stats
        profile["stats"]["total_workouts"] += 1
        profile["stats"]["total_calories"] += workout.get("calories", 0)
        profile["stats"]["total_time"] += workout.get("time_elapsed", 0)
        profile["stats"]["total_reps"] += workout.get("reps_completed", 0)

        # Update favorite exercise
        exercise_counts = {}
        for w in profile["workout_history"]:
            for exercise in w.get("exercises", []):
                exercise_name = exercise.get("name", "")
                if exercise_name:
                    exercise_counts[exercise_name] = (
                        exercise_counts.get(exercise_name, 0) + 1
                    )

        if exercise_counts:
            profile["stats"]["favorite_exercise"] = max(
                exercise_counts, key=exercise_counts.get
            )

        # Save updated profile
        self.save_profile(profile)

        return True

    def get_workout_history(self, email, limit=10):
        """Get user's workout history"""
        profile = self.load_profile(email)
        if not profile:
            return []

        history = profile.get("workout_history", [])
        # Return most recent workouts first
        return sorted(history, key=lambda x: x.get("date", ""), reverse=True)[:limit]

    def set_user_goals(self, email, goals):
        """Update user goals"""
        profile = self.load_profile(email)
        if not profile:
            return False

        profile["goals"].update(goals)
        self.save_profile(profile)
        return True

    def update_user_preferences(self, email, preferences):
        """Update user preferences"""
        profile = self.load_profile(email)
        if not profile:
            return False

        profile["preferences"].update(preferences)
        self.save_profile(profile)
        return True

    def update_body_metrics(self, email, metrics):
        """Update user body metrics"""
        profile = self.load_profile(email)
        if not profile:
            return False

        profile["body_metrics"].update(metrics)
        self.save_profile(profile)
        return True

    def generate_progress_chart(self, email, metric="calories", last_n_workouts=10):
        """Generate a progress chart for the specified metric"""
        profile = self.load_profile(email)
        if not profile or not profile.get("workout_history"):
            return None

        history = sorted(
            profile.get("workout_history", []), key=lambda x: x.get("date", "")
        )[-last_n_workouts:]

        if not history:  # If no workout history
            return None

        dates = [
            h.get("date", "").split()[0] for h in history
        ]  # Just get the date part

        if metric == "calories":
            values = [h.get("calories", 0) for h in history]
            title = "Calories Burned per Workout"
            ylabel = "Calories"
        elif metric == "time":
            values = [
                h.get("time_elapsed", 0) / 60 for h in history
            ]  # Convert to minutes
            title = "Workout Duration"
            ylabel = "Minutes"
        elif metric == "reps":
            values = [h.get("reps_completed", 0) for h in history]
            title = "Repetitions Completed"
            ylabel = "Reps"
        elif metric == "completion":
            values = [h.get("rep_completion", 0) for h in history]
            title = "Workout Completion Percentage"
            ylabel = "Completion %"
        else:
            return None

        # Create the chart
        plt.figure(figsize=(10, 6))
        plt.plot(dates, values, marker="o", linestyle="-", linewidth=2)
        plt.title(title)
        plt.xlabel("Date")
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save chart to file
        user_id = email.replace("@", "_at_").replace(".", "_dot_")
        chart_filename = f"{user_id}_{metric}_chart.png"
        chart_path = os.path.join(self.charts_dir, chart_filename)

        try:
            plt.savefig(chart_path)
            plt.close()

            # Convert path to relative path for HTML
            relative_path = os.path.join("charts", chart_filename).replace("\\", "/")
            return relative_path
        except Exception as e:
            print(f"Error saving chart: {e}")
            plt.close()
            return None

    def calculate_progress(self, email):
        """Calculate user's progress towards goals"""
        profile = self.load_profile(email)
        if not profile:
            return None

        # Get goals
        weekly_workout_goal = profile["goals"]["weekly_workouts"]
        calories_goal = profile["goals"]["calories_per_workout"]
        minutes_goal = profile["goals"]["minutes_per_workout"]

        # Get current week's workouts
        now = datetime.datetime.now()
        start_of_week = now - datetime.timedelta(days=now.weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0)

        this_week_workouts = [
            w
            for w in profile["workout_history"]
            if datetime.datetime.strptime(w["date"], "%Y-%m-%d %H:%M:%S")
            >= start_of_week
        ]

        # Calculate progress
        workouts_this_week = len(this_week_workouts)

        avg_calories = 0
        avg_minutes = 0

        if this_week_workouts:
            avg_calories = sum(w["calories"] for w in this_week_workouts) / len(
                this_week_workouts
            )
            avg_minutes = (
                sum(w["time_elapsed"] for w in this_week_workouts)
                / len(this_week_workouts)
                / 60
            )

        progress = {
            "workouts": {
                "current": workouts_this_week,
                "goal": weekly_workout_goal,
                "percentage": (
                    min(100, int((workouts_this_week / weekly_workout_goal) * 100))
                    if weekly_workout_goal > 0
                    else 0
                ),
            },
            "calories": {
                "current": avg_calories,
                "goal": calories_goal,
                "percentage": (
                    min(100, int((avg_calories / calories_goal) * 100))
                    if calories_goal > 0
                    else 0
                ),
            },
            "time": {
                "current": avg_minutes,
                "goal": minutes_goal,
                "percentage": (
                    min(100, int((avg_minutes / minutes_goal) * 100))
                    if minutes_goal > 0
                    else 0
                ),
            },
        }

        return progress

    def generate_progress_charts(self, email):
        """Generate a set of progress charts for the user"""
        try:
            profile = self.load_profile(email)
            if not profile or not profile.get("workout_history"):
                print("No workout history found")
                return []

            charts = []
            metrics = ["calories", "time", "reps", "completion"]

            # Ensure charts directory exists
            if not os.path.exists(self.charts_dir):
                os.makedirs(self.charts_dir)

            for metric in metrics:
                try:
                    # Get data for chart
                    history = sorted(
                        profile.get("workout_history", []),
                        key=lambda x: x.get("date", ""),
                    )[
                        -10:
                    ]  # Last 10 workouts

                    dates = [h.get("date", "").split()[0] for h in history]

                    if metric == "calories":
                        values = [h.get("calories", 0) for h in history]
                        title = "Calories Burned per Workout"
                        ylabel = "Calories"
                    elif metric == "time":
                        values = [h.get("time_elapsed", 0) / 60 for h in history]
                        title = "Workout Duration"
                        ylabel = "Minutes"
                    elif metric == "reps":
                        values = [h.get("reps_completed", 0) for h in history]
                        title = "Repetitions Completed"
                        ylabel = "Reps"
                    else:  # completion
                        values = [h.get("rep_completion", 0) for h in history]
                        title = "Workout Completion Percentage"
                        ylabel = "Completion %"

                    # Create and save chart
                    plt.figure(figsize=(10, 6))
                    plt.plot(dates, values, marker="o", linestyle="-", linewidth=2)
                    plt.title(title)
                    plt.xlabel("Date")
                    plt.ylabel(ylabel)
                    plt.grid(True)
                    plt.xticks(rotation=45)
                    plt.tight_layout()

                    # Save chart
                    user_id = email.replace("@", "_at_").replace(".", "_dot_")
                    chart_filename = f"{user_id}_{metric}_chart.png"
                    chart_path = os.path.join(self.charts_dir, chart_filename)

                    plt.savefig(chart_path)
                    plt.close()

                    # Add to charts list
                    charts.append(
                        {
                            "metric": metric,
                            "path": os.path.join("charts", chart_filename).replace(
                                "\\", "/"
                            ),
                        }
                    )
                    print(f"Generated chart for {metric}")

                except Exception as e:
                    print(f"Error generating {metric} chart: {e}")
                    plt.close()
                    continue

            return charts
        except Exception as e:
            print(f"Error in generate_progress_charts: {e}")
            return []

    def generate_progress_dashboard(self, email):
        """Generate a comprehensive progress dashboard as HTML"""
        profile = self.load_profile(email)
        if not profile:
            return None

        # Get basic profile info
        first_name = profile.get("first_name", "User")
        last_name = profile.get("last_name", "")

        # Get body metrics
        metrics = profile.get("body_metrics", {})
        weight = metrics.get("weight", "N/A")
        height = metrics.get("height", "N/A")
        bmi = metrics.get("bmi", "N/A")
        bmi_category = metrics.get("bmi_category", "N/A")

        # Generate charts first
        charts = self.generate_progress_charts(email)

        # Get workout history
        history = profile.get("workout_history", [])

        # Calculate progress metrics
        total_workouts = len(history)
        if total_workouts == 0:
            return f"<h1>Progress Dashboard for {first_name} {last_name}</h1><p>No workout data available yet.</p>"

        # Recent workouts (last 5)
        recent_workouts = sorted(
            history, key=lambda x: x.get("date", ""), reverse=True
        )[:5]

        # Total stats
        total_calories = sum(w.get("calories", 0) for w in history)
        total_time = (
            sum(w.get("time_elapsed", 0) for w in history) / 60
        )  # Convert to minutes
        total_reps = sum(w.get("reps_completed", 0) for w in history)

        # Weekly averages (last 4 weeks)
        now = datetime.datetime.now()
        four_weeks_ago = now - datetime.timedelta(days=28)
        recent_date = four_weeks_ago.strftime("%Y-%m-%d")

        recent_workouts_4wk = [
            w for w in history if w.get("date", "").split()[0] >= recent_date
        ]

        if recent_workouts_4wk:
            avg_calories = sum(w.get("calories", 0) for w in recent_workouts_4wk) / len(
                recent_workouts_4wk
            )
            avg_time = (
                sum(w.get("time_elapsed", 0) for w in recent_workouts_4wk)
                / len(recent_workouts_4wk)
                / 60
            )
            avg_completion = sum(
                w.get("rep_completion", 0) for w in recent_workouts_4wk
            ) / len(recent_workouts_4wk)
        else:
            avg_calories = avg_time = avg_completion = 0

        # Save dashboard to file
        user_id = email.replace("@", "_at_").replace(".", "_dot_")
        dashboard_path = os.path.join(self.dashboards_dir, f"{user_id}_dashboard.html")

        with open(dashboard_path, "w") as f:
            f.write(
                f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Fitness Progress Dashboard - {first_name} {last_name}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #333; }}
                    h1, h2 {{ color: #0066cc; }}
                    .dashboard {{ display: flex; flex-wrap: wrap; }}
                    .card {{ background: #f9f9f9; border-radius: 8px; padding: 15px; margin: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .profile-card {{ width: 300px; }}
                    .stats-card {{ width: 300px; }}
                    .chart-container {{ margin-top: 20px; }}
                    .metric {{ font-size: 24px; font-weight: bold; color: #0066cc; }}
                    .label {{ font-size: 14px; color: #666; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                    th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                    th {{ background-color: #f2f2f2; }}
                    .bmi-underweight {{ color: #ff9900; }}
                    .bmi-normal {{ color: #33cc33; }}
                    .bmi-overweight {{ color: #ff6600; }}
                    .bmi-obese {{ color: #cc0000; }}
                </style>
            </head>
            <body>
                <h1>Fitness Progress Dashboard</h1>
                <div class="dashboard">
                    <div class="card profile-card">
                        <h2>Profile</h2>
                        <p><strong>Name:</strong> {first_name} {last_name}</p>
                        <p><strong>Weight:</strong> {weight} kg</p>
                        <p><strong>Height:</strong> {height} cm</p>
                        <p><strong>BMI:</strong> {bmi}</p>
                        <p><strong>Category:</strong> <span class="bmi-normal">{bmi_category}</span></p>
                    </div>
                    
                    <div class="card stats-card">
                        <h2>Workout Statistics</h2>
                        <div>
                            <div class="metric">{total_workouts}</div>
                            <div class="label">Total Workouts</div>
                        </div>
                        <div>
                            <div class="metric">{total_calories:.1f}</div>
                            <div class="label">Total Calories Burned</div>
                        </div>
                        <div>
                            <div class="metric">{total_time:.1f}</div>
                            <div class="label">Total Minutes</div>
                        </div>
                        <div>
                            <div class="metric">{total_reps}</div>
                            <div class="label">Total Reps</div>
                        </div>
                    </div>
                    
                    <div class="card stats-card">
                        <h2>Recent Averages (4 weeks)</h2>
                        <div>
                            <div class="metric">{avg_calories:.1f}</div>
                            <div class="label">Avg. Calories per Workout</div>
                        </div>
                        <div>
                            <div class="metric">{avg_time:.1f}</div>
                            <div class="label">Avg. Minutes per Workout</div>
                        </div>
                        <div>
                            <div class="metric">{avg_completion:.1f}%</div>
                            <div class="label">Avg. Completion Rate</div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h2>Recent Workouts</h2>
                    <table>
                        <tr>
                            <th>Date</th>
                            <th>Exercises</th>
                            <th>Calories</th>
                            <th>Duration</th>
                            <th>Completion</th>
                        </tr>
            """
            )

            # Add recent workouts
            for workout in recent_workouts:
                date = workout.get("date", "").split()[0]
                exercises = ", ".join(
                    [ex.get("name", "") for ex in workout.get("exercises", [])]
                )
                calories = workout.get("calories", 0)
                duration = workout.get("time_elapsed", 0) / 60  # Minutes
                completion = workout.get("rep_completion", 0)

                f.write(
                    f"""
                    <tr>
                        <td>{date}</td>
                        <td>{exercises}</td>
                        <td>{calories}</td>
                        <td>{duration:.1f} min</td>
                        <td>{completion:.1f}%</td>
                    </tr>
                """
                )

            f.write(
                """
                    </table>
                </div>
                
                <div class="chart-container">
                    <h2>Progress Charts</h2>
                    <div class="dashboard">
            """
            )

            # Add charts
            for chart in charts:
                metric = chart["metric"].capitalize()
                path = chart["path"]
                f.write(
                    f"""
                    <div class="card">
                        <h3>{metric} Progress</h3>
                        <img src="../{path}" alt="{metric} progress chart" style="max-width: 100%;">
                    </div>
                """
                )

            f.write(
                """
                    </div>
                </div>
            </body>
            </html>
            """
            )

        return dashboard_path

    def save_workout(self, email, workout_data):
        """Save workout data to user profile"""
        profile = self.load_profile(email)
        if not profile:
            return False

        # Add timestamp to workout data
        workout_data["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Initialize workout_history if it doesn't exist
        if "workout_history" not in profile:
            profile["workout_history"] = []

        # Add workout to history
        profile["workout_history"].append(workout_data)

        # Save updated profile
        try:
            user_id = email.replace("@", "_at_").replace(".", "_dot_")
            profile_path = os.path.join(self.profiles_folder, f"{user_id}.json")
            with open(profile_path, "w") as f:
                json.dump(profile, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving workout: {e}")
            return False
