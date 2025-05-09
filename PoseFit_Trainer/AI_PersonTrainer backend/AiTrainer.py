import cv2
import numpy as np
import ExercisesModule as trainer
import EmailingSystem as email_sys
import DatabaseSys as db_sys
import AIWorkoutCoach as ai_coach
import os
from UserProfile import UserProfileManager
import webbrowser
import time
import getpass


def get_user_input_number(prompt, min_val, max_val, error_msg=None):
    """Helper function to get validated numerical input from user"""
    while True:
        try:
            user_input = input(prompt).strip()
            value = int(user_input)
            if value < min_val or value > max_val:
                raise ValueError(f"Value must be between {min_val} and {max_val}")
            return value
        except ValueError as e:
            if error_msg is None:
                error_msg = f"Invalid input: {e}"
            print(error_msg)
            print(f"Please enter a valid number between {min_val} and {max_val}")


def main():
    # Initialize UserProfileManager
    user_profile_manager = UserProfileManager()

    # User authentication/registration loop
    while True:
        print("\n===== AI PERSONAL TRAINER LOGIN =====")
        print("1. Login")
        print("2. Register")
        print("3. Reset Password")
        print("4. Exit")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":  # Login
            user_email = input("Email: ").strip()
            password = getpass.getpass("Password: ")

            try:
                user_data = db_sys.authenticate_user(user_email, password)

                # Check if the user is verified
                if not user_data.get("verified", False):
                    print(
                        "\nYour account is not verified. Please check your email for verification instructions."
                    )
                    print("Would you like to resend the verification code? (y/n)")
                    resend = input().strip().lower()

                    if resend in ("y", "yes"):
                        # Generate new verification code
                        verification_code = email_sys.generate_verification_code()

                        # Send verification email
                        email_sent = email_sys.send_verification_email(
                            user_email, verification_code
                        )

                        if email_sent:
                            print(f"\nVerification email sent to {user_email}.")
                            print(
                                "Please check your email and enter the verification code below."
                            )

                            # Verify the code
                            max_attempts = 3
                            for attempt in range(max_attempts):
                                user_code = input("Enter verification code: ").strip()

                                if user_code == verification_code:
                                    print("Email verified successfully!")

                                    # Update user verification status
                                    user_db = db_sys.load_user_database()
                                    if user_db and user_email in user_db:
                                        user_db[user_email]["verified"] = True
                                        user_db[user_email][
                                            "verification_time"
                                        ] = time.time()
                                        db_sys.save_user_database(user_db)
                                    break
                                else:
                                    remaining = max_attempts - attempt - 1
                                    if remaining > 0:
                                        print(
                                            f"Invalid code. You have {remaining} attempts remaining."
                                        )
                                    else:
                                        print(
                                            "Too many failed attempts. Please try again later."
                                        )
                                        continue
                        else:
                            print(
                                "Failed to send verification email. Please try again later."
                            )
                            continue
                    else:
                        print(
                            "Verification is required to use the application. Please verify your email."
                        )
                        continue

                first_name = user_data["first_name"]

                # Load or create user profile
                profile = user_profile_manager.load_profile(user_email)
                if not profile:
                    profile = user_profile_manager.create_user_profile(
                        user_email,
                        user_data["first_name"],
                        user_data["last_name"],
                        user_data.get("age"),
                        user_data.get("gender"),
                        user_data.get("weight"),
                        user_data.get("height"),
                    )
                break

            except Exception as e:
                print(f"\nError: {str(e)}")
                print("Login failed. Please try again.")

        elif choice == "2":  # Register
            print("\n===== REGISTRATION =====")
            try:
                # Get user registration data
                email = input("Email: ").strip()
                password = getpass.getpass("Password (min 8 characters): ")
                confirm_password = getpass.getpass("Confirm Password: ")

                if password != confirm_password:
                    print("Passwords do not match. Please try again.")
                    continue

                if len(password) < 8:
                    print("Password must be at least 8 characters long.")
                    continue

                first_name = input("First Name: ").strip()
                last_name = input("Last Name: ").strip()
                age = int(input("Age: ").strip())
                gender = input("Gender (M/F/Other): ").strip()
                weight = float(input("Weight (kg): ").strip())
                height = float(input("Height (cm): ").strip())

                # Register user
                user_data = {
                    "email": email,
                    "password": password,
                    "first_name": first_name,
                    "last_name": last_name,
                    "age": age,
                    "gender": gender,
                    "weight": weight,
                    "height": height,
                }

                user_reg = db_sys.register_user_api(user_data)

                if user_reg:
                    print("\nRegistration successful!")
                    print("Please check your email for verification instructions.")

                    # Generate verification code
                    verification_code = email_sys.generate_verification_code()

                    # Send verification email
                    email_sent = email_sys.send_verification_email(
                        email, verification_code
                    )

                    if email_sent:
                        print("\nVerification email sent!")
                        print("Would you like to verify your email now? (y/n)")
                        verify_now = input().strip().lower()

                        if verify_now in ("y", "yes"):
                            max_attempts = 3
                            for attempt in range(max_attempts):
                                user_code = input("Enter verification code: ").strip()

                                if user_code == verification_code:
                                    # Update user verification status
                                    user_db = db_sys.load_user_database()
                                    if user_db and email in user_db:
                                        user_db[email]["verified"] = True
                                        user_db[email][
                                            "verification_time"
                                        ] = time.time()
                                        db_sys.save_user_database(user_db)
                                        print("\nEmail verified successfully!")
                                        print(
                                            "You can now log in with your credentials."
                                        )
                                    break
                                else:
                                    remaining = max_attempts - attempt - 1
                                    if remaining > 0:
                                        print(
                                            f"Invalid code. You have {remaining} attempts remaining."
                                        )
                                    else:
                                        print(
                                            "Too many failed attempts. Please try again later."
                                        )
                    else:
                        print(
                            "Failed to send verification email. Please try logging in and requesting a new code."
                        )

                break

            except Exception as e:
                print(f"\nRegistration error: {str(e)}")
                print("Registration failed. Please try again.")

        elif choice == "3":  # Reset Password
            print("\n===== PASSWORD RESET =====")
            email = input("Enter your email: ").strip()

            try:
                # Generate verification code
                verification_code = email_sys.generate_verification_code()

                # Send verification email
                email_sent = email_sys.send_verification_email(email, verification_code)

                if email_sent:
                    print("\nPassword reset code sent to your email.")

                    # Verify the code
                    max_attempts = 3
                    for attempt in range(max_attempts):
                        user_code = input("Enter verification code: ").strip()

                        if user_code == verification_code:
                            # Get new password
                            while True:
                                new_password = getpass.getpass(
                                    "New Password (min 8 characters): "
                                )
                                confirm_password = getpass.getpass(
                                    "Confirm New Password: "
                                )

                                if new_password != confirm_password:
                                    print("Passwords do not match. Please try again.")
                                    continue

                                if len(new_password) < 8:
                                    print(
                                        "Password must be at least 8 characters long."
                                    )
                                    continue

                                # Update password in database
                                user_db = db_sys.load_user_database()
                                if user_db and email in user_db:
                                    user_db[email]["hashed_password"] = (
                                        db_sys.get_password_hash(new_password)
                                    )
                                    db_sys.save_user_database(user_db)
                                    print("\nPassword reset successful!")
                                    print("You can now log in with your new password.")
                                break
                            break
                        else:
                            remaining = max_attempts - attempt - 1
                            if remaining > 0:
                                print(
                                    f"Invalid code. You have {remaining} attempts remaining."
                                )
                            else:
                                print(
                                    "Too many failed attempts. Please try again later."
                                )
                else:
                    print("Failed to send reset email. Please try again later.")

            except Exception as e:
                print(f"\nError: {str(e)}")
                print("Password reset failed. Please try again.")

        elif choice == "4":  # Exit
            print("\nThank you for using AI Personal Trainer!")
            exit(0)

        else:
            print("\nInvalid choice. Please select 1-4.")
            continue

    # Initialize AI coach and display welcome
    coach = ai_coach.AIWorkoutCoach()
    print("\n===== AI PERSONAL TRAINER =====")
    print(f"Welcome back, {first_name}!")

    # Display user profile information if available
    display_user_profile(profile)

    # Option to view progress dashboard if they have workout history
    if profile and profile.get("workout_history"):
        print("Would you like to view your fitness progress dashboard? (y/n)")
        view_dashboard = input().strip().lower()
        if view_dashboard in ["y", "yes"]:
            open_dashboard(user_profile_manager, user_email)

    # Get workout settings (sets and reps)
    sets, reps = get_workout_settings(coach, user_email)

    # Camera selection
    selected_cam_index = select_camera()
    if selected_cam_index is None:
        print("No camera selected. Using default camera.")
        selected_cam_index = 0

    # Wait for user to start
    print("When you are ready to start, press Enter.")
    input("Press Enter to begin your workout: ")

    # Start the workout session
    try:
        # Pass user profile to workout session for enhanced feedback
        session = trainer.start_workout_session(
            sets=sets,
            reps=reps,
            camera_index=selected_cam_index,
            user_profile=profile,
            exercise_type="push_ups",
        )

        performance = session.complete_path()

        # Use a more reliable image path that exists in the repo
        congratulations_img = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "TrainerImages",
            "congratulations.jpg",
        )
        # Try alternate images if the main one doesn't exist
        if not os.path.exists(congratulations_img):
            congratulations_img = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "TrainerImages",
                "you_rock.jpeg",
            )
        if not os.path.exists(congratulations_img):
            congratulations_img = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "TrainerImages",
                "great_job2.jpeg",
            )
        if not os.path.exists(congratulations_img):
            congratulations_img = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "TrainerImages",
                "end_screen.jpeg",
            )

        final_video_path = session.completion_screen(congratulations_img)

        # Record the workout in the user's profile
        if performance:
            record_workout_in_profile(
                user_profile_manager, user_email, session, performance
            )

        # Handle video and email operations
        handle_workout_completion(
            final_video_path, session, performance, user_email, first_name
        )

        # Show next workout recommendation for next time
        show_next_workout_recommendation(coach, user_email, user_profile_manager)

    except Exception as e:
        print(f"Workout error: {str(e)}")
        print("An error occurred during the workout. Please try again later.")


def display_user_profile(profile):
    """Display user profile information"""
    if profile and "body_metrics" in profile:
        metrics = profile["body_metrics"]
        print("\n===== YOUR PROFILE =====")

        # Display basic metrics
        for metric in ["age", "gender", "weight", "height"]:
            if metrics.get(metric):
                label = metric.capitalize()
                value = metrics[metric]
                unit = (
                    " kg" if metric == "weight" else " cm" if metric == "height" else ""
                )
                print(f"{label}: {value}{unit}")

        # Display BMI and health assessment
        if metrics.get("bmi"):
            print(f"BMI: {metrics['bmi']}")
            if metrics.get("bmi_category"):
                print(f"BMI Category: {metrics['bmi_category']}")

            from UserProfile import UserProfileManager

            health_assessment = UserProfileManager().get_health_assessment(
                metrics["bmi"]
            )
            print(f"\nHealth Assessment: {health_assessment}")

        print("==========================\n")


def open_dashboard(user_profile_manager, user_email):
    """Generate and open the user's fitness dashboard"""
    dashboard_path = user_profile_manager.generate_progress_dashboard(user_email)
    if dashboard_path:
        print(f"Progress dashboard generated at {dashboard_path}")
        try:
            webbrowser.open("file://" + os.path.abspath(dashboard_path))
            print("Opening dashboard in your browser...")
        except Exception as e:
            print(f"Could not open browser automatically: {e}")
            print(f"Please open {dashboard_path} in your browser manually.")


def get_workout_settings(coach, user_email):
    """Get workout settings (sets and reps) from user"""
    try:
        recommendation = coach.get_next_workout_recommendation(user_email)
        print("\n===== YOUR PERSONALIZED WORKOUT RECOMMENDATION =====")
        print(recommendation)
        print(
            "\nWould you like to follow this recommendation or create a custom workout?"
        )
        choice = (
            input("Enter 'r' for recommended workout or 'c' for custom: ")
            .strip()
            .lower()
        )

        # Default values if user follows recommendation
        sets = 1
        reps = 6

        if choice == "r":
            print("Great! You'll follow the recommended workout.")
            # Using default values
        else:
            print("You've chosen to create a custom workout.")
            # Get sets and reps from user
            sets = get_user_input_number(
                "Enter number of sets (1-20): ", 1, 20, "Sets must be between 1 and 20"
            )

            reps = get_user_input_number(
                "Enter number of repetitions per set (1-50): ",
                1,
                50,
                "Repetitions must be between 1 and 50",
            )

            print(f"You selected: {sets} set(s) of {reps} repetition(s)")

    except Exception as e:
        print(f"Error loading recommendations: {str(e)}")
        print("We'll proceed with a custom workout instead.")

        # Get sets and reps as fallback
        sets = get_user_input_number(
            "Enter number of sets (1-20): ", 1, 20, "Sets must be between 1 and 20"
        )

        reps = get_user_input_number(
            "Enter number of repetitions per set (1-50): ",
            1,
            50,
            "Repetitions must be between 1 and 50",
        )

        print(f"You selected: {sets} set(s) of {reps} repetition(s)")

    return sets, reps


def select_camera():
    """Select a camera from available options"""
    print("Checking webcams. Click feed to select.")
    available_cameras_indices = []
    camera_feeds = []
    selected_camera_index = None
    window_name = "Camera Selection"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    break_loop = False  # Flag to signal loop termination

    def mouse_callback(event, x, y, flags, param):
        nonlocal selected_camera_index, break_loop
        if event == cv2.EVENT_LBUTTONDOWN:
            camera_width = 320
            clicked_camera_index_pos = x // camera_width
            if 0 <= clicked_camera_index_pos < len(available_cameras_indices):
                selected_camera_index = available_cameras_indices[
                    clicked_camera_index_pos
                ]
                print(f"Camera {selected_camera_index} selected.")
                break_loop = True  # Signal the loop to break

    cv2.setMouseCallback(window_name, mouse_callback)

    # Check available cameras
    for camera_index in range(4):  # Check first 4 camera indices
        cap_check = cv2.VideoCapture(camera_index)
        if cap_check.isOpened():
            available_cameras_indices.append(camera_index)
            camera_feeds.append(cap_check)
        else:
            camera_feeds.append(None)

    live_camera_feeds = [feed for feed in camera_feeds if feed is not None]
    available_camera_count = len(live_camera_feeds)

    if available_camera_count == 0:
        print("No cameras detected. Using default camera index 0.")
        cv2.destroyAllWindows()
        return 0

    # Display camera selection interface
    while not break_loop:
        frames = []
        for i, cap in enumerate(live_camera_feeds):
            success, frame = cap.read()
            if success:
                cv2.rectangle(frame, (0, 0), (320, 30), (0, 255, 0), -1)
                cv2.putText(
                    frame,
                    f"Click to Select Cam {available_cameras_indices[i]}",
                    (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 0),
                    1,
                )
                resized_frame = cv2.resize(frame, (320, 240))
                frames.append(resized_frame)
            else:
                frames.append(np.zeros((240, 320, 3), dtype=np.uint8))

        if frames:
            horizontal_frame = np.hstack(frames)
            cv2.imshow(window_name, horizontal_frame)
            cv2.resizeWindow(window_name, available_camera_count * 320, 240)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break_loop = True  # Allow quitting with 'q'
        if selected_camera_index is not None:  # Check if selected via callback
            break_loop = True

    # Cleanup
    cv2.destroyAllWindows()
    for cap in live_camera_feeds:
        cap.release()

    return selected_camera_index


def record_workout_in_profile(user_profile_manager, user_email, session, performance):
    """Record the workout in the user's profile"""
    workout_data = {
        "exercises": session.get_completed_exercises(),
        "calories": performance.get("calories", 0),
        "time_elapsed": performance.get("time_elapsed", 0),
        "reps_completed": performance.get("reps_completed", 0),
        "total_reps": performance.get("total_reps", 0),
        "rep_completion": performance.get("rep_completion", 0),
    }
    user_profile_manager.record_workout(user_email, workout_data)


def handle_workout_completion(
    final_video_path, session, performance, user_email, first_name
):
    """Handle video options and email sending after workout completion"""
    if final_video_path:
        if not os.path.exists(final_video_path):
            print(f"Warning: Video file '{final_video_path}' not found")
            print(
                "There was an issue with the video recording. Sending stats email instead."
            )

            # Send stats email only
            send_workout_summary_email(user_email, first_name, performance)
        else:
            print(f"Video created successfully: {final_video_path}")
            print("\n===== WORKOUT COMPLETE =====")
            print(f"Calories burned: {performance.get('calories', 0)}")
            print(f"Time elapsed: {performance.get('time_elapsed', 0)} seconds")

            # Handle video options
            result = session.handle_video_options(
                final_video_path, user_email, first_name
            )
            print(f"Video handling option result: {result}")

            # Always send workout summary email regardless of video email status
            send_workout_summary_email(user_email, first_name, performance)
    else:
        # No video recording, just send the stats email
        send_workout_summary_email(user_email, first_name, performance)


def send_workout_summary_email(user_email, first_name, performance):
    """Send workout summary email to user"""
    email_result = email_sys.email_user(
        user_email,
        first_name,
        str(performance.get("calories", 0)),
        performance.get("time_elapsed", 0),
        performance.get("rep_completion", 0),
    )

    if email_result:
        print("Workout summary has been sent to your email!")
    else:
        print(
            "There was an issue sending the email. Please check your internet connection."
        )


def show_next_workout_recommendation(coach, user_email, user_profile_manager):
    """Show next workout recommendation and offer to view dashboard"""
    try:
        next_recommendation = coach.get_next_workout_recommendation(user_email)
        print("\n===== YOUR NEXT WORKOUT RECOMMENDATION =====")
        print(
            "Based on today's performance, here's what I recommend for your next session:"
        )
        print(next_recommendation)

        # Offer to view updated progress dashboard
        print("\nWould you like to view your updated fitness progress dashboard? (y/n)")
        view_dashboard = input().strip().lower()
        if view_dashboard in ["y", "yes"]:
            open_dashboard(user_profile_manager, user_email)

    except Exception as e:
        print(f"Error generating next recommendation: {e}")


if __name__ == "__main__":
    main()
