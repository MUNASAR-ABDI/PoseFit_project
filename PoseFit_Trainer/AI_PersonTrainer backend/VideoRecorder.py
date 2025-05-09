import cv2
import os
import time
import datetime
import numpy as np
import traceback
from pathlib import Path
from EmailingSystem import email_user_with_video
import threading
import queue
import sys
import requests


class VideoRecorder:
    def __init__(self, temp_folder="temp_videos", output_folder="saved_workouts"):
        """
        Initialize the video recorder

        Args:
            temp_folder: Folder for temporary video segments
            output_folder: Folder for saved workout videos
        """
        # Use absolute paths
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.temp_folder = os.path.join(self.current_dir, temp_folder)
        self.output_folder = os.path.join(self.current_dir, output_folder)

        self.exercise_videos = []
        self.session_videos = (
            {}
        )  # Store videos by session ID to ensure we can combine all exercises from a session
        self.current_video_path = None
        self.video_writer = None
        self.recording = False
        self.is_recording = False  # Additional flag for clarity
        self.current_session_id = None  # Store the current session ID
        self.is_paused = False  # Track if recording is paused
        self.last_exercise_name = None  # Track last exercise name for resuming
        self.workout_active = False  # Track if we're in an active workout session

        # Global class-level tracking of session videos to ensure persistence between instances
        if not hasattr(VideoRecorder, "_all_session_videos"):
            VideoRecorder._all_session_videos = {}
            print("[VideoRecorder] Created global session video tracker")

        # Optimized video dimensions for balance between quality and performance
        self.frame_width = 1280
        self.frame_height = 720
        self.fps = 24  # Reduced from 30 for more stability

        # Significantly improved quality settings
        self.quality = 95  # JPEG quality for frames (0-100)
        self.bitrate = 8000000  # 8Mbps bitrate (reduced from 15Mbps for stability)

        # Use a thread-safe queue instead of a simple list for frame buffer
        self.frame_queue = queue.Queue(
            maxsize=120
        )  # Store up to 120 frames (5 seconds at 24fps)
        self.buffer_enabled = True
        self.frame_counter = 0  # For debugging frame rate
        self.last_time = time.time()
        self.last_frame_time = 0  # For tracking frame timing
        self.frame_timestamps = []  # For tracking timestamps

        # Add a frame drop counter to help diagnose issues
        self.frames_dropped = 0

        print(
            f"[VideoRecorder] Initialized with frame size: {self.frame_width}x{self.frame_height} @ {self.fps}fps, bitrate: {self.bitrate/1000000}Mbps"
        )

        # Create necessary directories with explicit error handling
        try:
            print(f"Creating directory: {self.temp_folder}")
            os.makedirs(self.temp_folder, exist_ok=True)

            print(f"Creating directory: {self.output_folder}")
            os.makedirs(self.output_folder, exist_ok=True)

            # Verify directories exist
            if not os.path.isdir(self.temp_folder):
                print(f"Failed to create directory: {self.temp_folder}")
            else:
                print(f"Successfully created/verified: {self.temp_folder}")

            if not os.path.isdir(self.output_folder):
                print(f"Failed to create directory: {self.output_folder}")
            else:
                print(f"Successfully created/verified: {self.output_folder}")

        except Exception as e:
            print(f"Error creating directories: {e}")
            # Create directories in current working directory as fallback
            self.temp_folder = os.path.abspath(temp_folder)
            self.output_folder = os.path.abspath(output_folder)
            try:
                os.makedirs(self.temp_folder, exist_ok=True)
                os.makedirs(self.output_folder, exist_ok=True)
            except Exception as fallback_error:
                print(f"Error creating fallback directories: {fallback_error}")

    def start_recording(self, exercise_name, session_id=None):
        """Start recording a video for an exercise"""
        if self.recording:
            self.stop_recording()

        # Store session ID if provided
        if session_id:
            self.current_session_id = session_id
            print(f"[VideoRecorder] Set current session ID: {session_id}")

            # Initialize session videos list if not already present
            if session_id not in self.session_videos:
                self.session_videos[session_id] = []
                print(
                    f"[VideoRecorder] Created new session videos list for session {session_id}"
                )

            # Also update global session tracking
            if not hasattr(VideoRecorder, "_all_session_videos"):
                VideoRecorder._all_session_videos = {}

            if session_id not in VideoRecorder._all_session_videos:
                VideoRecorder._all_session_videos[session_id] = []
                print(
                    f"[VideoRecorder] Created global session videos list for session {session_id}"
                )

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{exercise_name}_{timestamp}.avi"  # Always use AVI first as it's more reliable
        self.current_video_path = os.path.join(self.temp_folder, filename)
        self.final_format = "mp4"  # Always track the desired final format

        # Try multiple codecs in order of preference
        success = False

        # For Mac systems, try MJPG first as it's often more stable
        try:
            print(f"[VideoRecorder] Trying MJPG codec first (more stable on macOS)...")
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")

            self.video_writer = cv2.VideoWriter(
                self.current_video_path,
                fourcc,
                self.fps,
                (self.frame_width, self.frame_height),
            )

            if self.video_writer.isOpened():
                print(f"[VideoRecorder] Created video writer using MJPG codec")
                success = True
                # Mark that we need to convert from AVI to MP4 later
                self.needs_conversion = True
            else:
                print(f"[VideoRecorder] Failed to create video writer with MJPG codec")
        except Exception as e:
            print(f"[VideoRecorder] Error trying MJPG codec: {e}")

        # If MJPG failed, try mp4v codec
        if not success:
            try:
                print(f"[VideoRecorder] Trying mp4v codec...")
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")

                self.video_writer = cv2.VideoWriter(
                    self.current_video_path,
                    fourcc,
                    self.fps,
                    (self.frame_width, self.frame_height),
                )

                if self.video_writer.isOpened():
                    print(f"[VideoRecorder] Created video writer using mp4v codec")
                    success = True
                else:
                    print(
                        f"[VideoRecorder] Failed to create video writer with mp4v codec"
                    )
            except Exception as e:
                print(f"[VideoRecorder] Error trying mp4v codec: {e}")

        # If mp4v failed, try XVID
        if not success:
            try:
                print(
                    f"[VideoRecorder] Trying XVID codec (will convert to MP4 later)..."
                )
                fourcc = cv2.VideoWriter_fourcc(*"XVID")
                temp_avi_path = self.current_video_path.replace(".avi", ".avi")

                self.video_writer = cv2.VideoWriter(
                    temp_avi_path,
                    fourcc,
                    self.fps,
                    (self.frame_width, self.frame_height),
                )

                if self.video_writer.isOpened():
                    print(f"[VideoRecorder] Created video writer using XVID codec")
                    self.current_video_path = temp_avi_path  # Temporarily use AVI
                    success = True
                    # Mark that we need to convert from AVI to MP4 later
                    self.needs_conversion = True
                else:
                    print(
                        f"[VideoRecorder] Failed to create video writer with XVID codec"
                    )
            except Exception as e:
                print(f"[VideoRecorder] Error trying XVID codec: {e}")

        # Last resort, try H264 only if other codecs failed
        if not success:
            try:
                print(f"[VideoRecorder] Trying H264 codec as last resort...")
                fourcc = cv2.VideoWriter_fourcc(*"H264")

                # Set codec parameters for better quality
                try:
                    video_params = {
                        cv2.VIDEOWRITER_PROP_QUALITY: self.quality,
                        cv2.VIDEOWRITER_PROP_BITRATE: self.bitrate,
                    }
                    self.video_writer = cv2.VideoWriter(
                        self.current_video_path,
                        fourcc,
                        self.fps,
                        (self.frame_width, self.frame_height),
                        params=video_params,
                    )
                except Exception:
                    # If params are not supported, try without them
                    self.video_writer = cv2.VideoWriter(
                        self.current_video_path,
                        fourcc,
                        self.fps,
                        (self.frame_width, self.frame_height),
                    )

                # Verify it opened successfully
                if self.video_writer.isOpened():
                    print(f"[VideoRecorder] Created video writer using H264 codec")
                    success = True
                else:
                    print(
                        f"[VideoRecorder] Failed to create video writer with H264 codec"
                    )
            except Exception as e:
                print(f"[VideoRecorder] Error trying H264 codec: {e}")

        if success:
            self.recording = True
            self.is_recording = True
            print(
                f"[VideoRecorder] Started recording {exercise_name} at {self.current_video_path}"
            )

            # Clear frame queue
            while not self.frame_queue.empty():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    break

            # Reset counters
            self.recording_start_time = time.time()
            self.frames_written = 0
            self.frame_counter = 0
            self.frames_dropped = 0
            self.last_time = time.time()
            self.last_frame_time = time.time()
            self.frame_timestamps = []

            # Start a background thread for writing frames to reduce main thread lag
            if not hasattr(self, "writer_thread") or not self.writer_thread.is_alive():
                self.writer_thread_active = True
                self.writer_thread = threading.Thread(
                    target=self._process_frame_queue, daemon=True
                )
                self.writer_thread.start()
                print(f"[VideoRecorder] Started background writer thread")
        else:
            print(f"[VideoRecorder] Failed to create video writer with any codec")
            self.recording = False
            self.is_recording = False

    def _process_frame_queue(self):
        """Background thread to process and write frames from the queue"""
        while self.writer_thread_active:
            if self.buffer_enabled and not self.frame_queue.empty():
                try:
                    # Get the oldest frame from the queue with a timeout
                    frame_data = self.frame_queue.get(timeout=0.1)
                    frame = frame_data["frame"]
                    timestamp = frame_data["timestamp"]

                    # Check if we need to drop frames to maintain timing
                    current_time = time.time()
                    time_since_start = current_time - self.recording_start_time
                    expected_frames = time_since_start * self.fps

                    # If we're falling behind, skip some frames
                    if (
                        self.frames_written > 0
                        and self.frames_written > expected_frames + 10
                    ):
                        # Skip this frame to catch up
                        self.frames_dropped += 1
                        if self.frames_dropped % 10 == 0:  # Log every 10 dropped frames
                            print(
                                f"[VideoRecorder] Dropping frames to maintain timing: {self.frames_dropped} dropped so far"
                            )
                        self.frame_queue.task_done()
                        continue

                    # Write it to the video file
                    if self.video_writer and self.video_writer.isOpened():
                        self.video_writer.write(frame)
                        self.frames_written += 1
                    else:
                        # Video writer got closed, exit thread
                        print(
                            "[VideoRecorder] Video writer is closed, exiting writer thread"
                        )
                        self.writer_thread_active = False
                        break
                except queue.Empty:
                    # No frames available, just continue
                    pass
                except Exception as e:
                    print(f"[VideoRecorder] Error in writer thread: {e}")
            else:
                # Sleep a bit if no frames to process
                time.sleep(0.005)  # 5ms sleep to prevent CPU hogging

    def write_frame(self, frame):
        """Write the exact frame from the workout stream to the video file, no extra processing."""
        if not self.recording or self.video_writer is None:
            return
        try:
            # Skip empty frames
            if frame is None or frame.size == 0:
                print("[VideoRecorder] Warning: Skipping empty frame")
                return
            # Ensure frame is the right size
            if (
                frame.shape[1] != self.frame_width
                or frame.shape[0] != self.frame_height
            ):
                frame = cv2.resize(frame, (self.frame_width, self.frame_height))
            # Write the frame exactly as received
            if self.buffer_enabled:
                try:
                    self.frame_queue.put(
                        {"frame": frame, "timestamp": time.time()}, timeout=0.1
                    )
                except queue.Full:
                    self.frames_dropped += 1
                    if self.frames_dropped % 10 == 0:
                        print(
                            f"[VideoRecorder] Frame queue full, dropped {self.frames_dropped} frames"
                        )
            else:
                if self.video_writer and self.video_writer.isOpened():
                    self.video_writer.write(frame)
                    self.frames_written += 1
        except Exception as e:
            print(f"[VideoRecorder] Error writing frame: {e}")

    def stop_recording(self):
        """Stop the current recording if active"""
        try:
            if self.recording and self.video_writer is not None:
                print("[VideoRecorder] Stopping recording and releasing writer")

                # Stop accepting new frames
                self.recording = False
                self.is_recording = False

                # Wait for the queue to empty
                queue_size = self.frame_queue.qsize()
                if queue_size > 0:
                    print(
                        f"[VideoRecorder] Waiting for {queue_size} frames to be processed from queue..."
                    )
                    wait_start = time.time()
                    patience_time = 30  # Maximum wait time in seconds

                    # Wait with a timeout
                    while (
                        not self.frame_queue.empty()
                        and time.time() - wait_start < patience_time
                    ):
                        time.sleep(0.1)

                    if not self.frame_queue.empty():
                        remaining = self.frame_queue.qsize()
                        print(
                            f"[VideoRecorder] Queue still has {remaining} frames after waiting {patience_time}s. Clearing queue."
                        )
                        # Clear the queue
                        while not self.frame_queue.empty():
                            try:
                                self.frame_queue.get_nowait()
                                self.frame_queue.task_done()
                            except:
                                pass

                # Stop the background writer thread
                if hasattr(self, "writer_thread_active"):
                    self.writer_thread_active = False
                    if hasattr(self, "writer_thread") and self.writer_thread.is_alive():
                        print(f"[VideoRecorder] Waiting for writer thread to finish...")
                        self.writer_thread.join(
                            timeout=5.0
                        )  # Wait up to 5 seconds for thread to finish
                        if self.writer_thread.is_alive():
                            print(
                                f"[VideoRecorder] Warning: Writer thread did not exit cleanly"
                            )

                # Release video writer
                if self.video_writer and self.video_writer.isOpened():
                    self.video_writer.release()
                    print("[VideoRecorder] VideoWriter released")
                    self.video_writer = None

                # Check if the video file exists and has content
                if os.path.exists(self.current_video_path):
                    file_size = os.path.getsize(self.current_video_path)

                    if file_size > 0:
                        print(
                            f"[VideoRecorder] Video recorded successfully: {self.current_video_path} ({file_size} bytes)"
                        )

                        # Verify the video has frames
                        try:
                            cap = cv2.VideoCapture(self.current_video_path)
                            if cap.isOpened():
                                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                                fps = cap.get(cv2.CAP_PROP_FPS)
                                duration = frame_count / fps if fps > 0 else 0

                                print(
                                    f"[VideoRecorder] Video contains {frame_count} frames, {duration:.1f} seconds at {fps} FPS"
                                )

                                # Read 10 random frames to verify video integrity
                                valid_frames = 0
                                if frame_count > 0:
                                    for _ in range(min(10, frame_count)):
                                        random_pos = np.random.randint(0, frame_count)
                                        cap.set(cv2.CAP_PROP_POS_FRAMES, random_pos)
                                        ret, _ = cap.read()
                                        if ret:
                                            valid_frames += 1

                                cap.release()
                                print(
                                    f"[VideoRecorder] Verified {valid_frames} valid frames"
                                )

                                if valid_frames > 0 or frame_count > 0:
                                    # Add to list of exercise videos
                                    self.exercise_videos.append(self.current_video_path)
                                    print(
                                        f"[VideoRecorder] Added to exercise videos list (total: {len(self.exercise_videos)})"
                                    )

                                    # Also add to session videos if we have a session ID
                                    if (
                                        hasattr(self, "current_session_id")
                                        and self.current_session_id
                                    ):
                                        if (
                                            self.current_session_id
                                            not in self.session_videos
                                        ):
                                            self.session_videos[
                                                self.current_session_id
                                            ] = []

                                        self.session_videos[
                                            self.current_session_id
                                        ].append(self.current_video_path)
                                        print(
                                            f"[VideoRecorder] Added to session {self.current_session_id} videos (total: {len(self.session_videos[self.current_session_id])})"
                                        )

                                    # Update global session videos tracking
                                    if hasattr(VideoRecorder, "_all_session_videos"):
                                        if (
                                            self.current_session_id
                                            not in VideoRecorder._all_session_videos
                                        ):
                                            VideoRecorder._all_session_videos[
                                                self.current_session_id
                                            ] = []

                                        VideoRecorder._all_session_videos[
                                            self.current_session_id
                                        ].append(self.current_video_path)
                                        print(
                                            f"[VideoRecorder] Added to global session {self.current_session_id} videos (total: {len(VideoRecorder._all_session_videos[self.current_session_id])})"
                                        )
                                else:
                                    print(
                                        f"[VideoRecorder] Warning: No valid frames could be read from video"
                                    )
                        except Exception as verify_err:
                            print(
                                f"[VideoRecorder] Warning: Could not open video file to verify frame count"
                            )
                            print(
                                f"[VideoRecorder] Error verifying video: {verify_err}"
                            )
                    else:
                        print(
                            f"[VideoRecorder] Warning: Video file is empty (0 bytes): {self.current_video_path}"
                        )
                else:
                    print(
                        f"[VideoRecorder] Warning: Video file was not created: {self.current_video_path}"
                    )

                # Log the frame rate achieved
                if hasattr(self, "recording_start_time") and self.recording_start_time:
                    elapsed = time.time() - self.recording_start_time
                    if elapsed > 0 and self.frames_written > 0:
                        actual_fps = self.frames_written / elapsed
                        print(
                            f"[VideoRecorder] Total frames written in this recording: {self.frames_written} at {actual_fps:.1f} FPS"
                        )
                        print(f"[VideoRecorder] Frames dropped: {self.frames_dropped}")

                return self.current_video_path
        except Exception as e:
            print(f"[VideoRecorder] Error stopping recording: {e}")
            self.recording = False
            self.is_recording = False
            return None

    def _convert_to_mp4(self, input_path, output_path):
        """Convert video to MP4 format with good quality"""
        try:
            print(
                f"[VideoRecorder] Converting {input_path} to {output_path} using ffmpeg..."
            )

            # Try to use ffmpeg first (more efficient conversion)
            try:
                import subprocess
                import platform

                # Detect operating system for platform-specific optimizations
                system = platform.system()

                # Base command with common parameters
                command = [
                    "ffmpeg",
                    "-i",
                    input_path,
                    "-y",  # Overwrite if exists
                ]

                if system == "Darwin":  # macOS
                    # For macOS, use videotoolbox hardware acceleration if available
                    try:
                        # First check if h264_videotoolbox is available
                        check_cmd = ["ffmpeg", "-encoders"]
                        result = subprocess.run(
                            check_cmd, capture_output=True, text=True
                        )
                        if "h264_videotoolbox" in result.stdout:
                            # Use hardware acceleration for macOS
                            command.extend(
                                [
                                    "-c:v",
                                    "h264_videotoolbox",
                                    "-b:v",
                                    "8M",  # 8Mbps bitrate
                                    "-pix_fmt",
                                    "yuv420p",  # For compatibility
                                    "-profile:v",
                                    "high",  # High profile for better quality
                                    "-movflags",
                                    "+faststart",  # Optimize for web streaming
                                ]
                            )
                        else:
                            # Fall back to software encoding
                            command.extend(
                                [
                                    "-c:v",
                                    "libx264",  # H.264 codec
                                    "-preset",
                                    "fast",  # Faster encoding, still good quality
                                    "-crf",
                                    "22",  # Quality level (lower = better quality but larger file)
                                    "-maxrate",
                                    "8M",  # Maximum bitrate
                                    "-bufsize",
                                    "16M",  # Buffer size
                                    "-pix_fmt",
                                    "yuv420p",  # Pixel format for compatibility
                                    "-movflags",
                                    "+faststart",  # Optimize for web streaming
                                ]
                            )
                    except Exception:
                        # Fallback if checking encoders fails
                        command.extend(
                            [
                                "-c:v",
                                "libx264",  # H.264 codec
                                "-preset",
                                "fast",  # Faster encoding, still good quality
                                "-crf",
                                "22",  # Quality level (lower = better quality but larger file)
                                "-maxrate",
                                "8M",  # Maximum bitrate
                                "-bufsize",
                                "16M",  # Buffer size
                                "-pix_fmt",
                                "yuv420p",  # Pixel format for compatibility
                                "-movflags",
                                "+faststart",  # Optimize for web streaming
                            ]
                        )
                else:
                    # Standard settings for other platforms
                    command.extend(
                        [
                            "-c:v",
                            "libx264",  # H.264 codec
                            "-preset",
                            "fast",  # Faster encoding, still good quality
                            "-crf",
                            "22",  # Quality level (lower = better quality but larger file)
                            "-maxrate",
                            "8M",  # Maximum bitrate
                            "-bufsize",
                            "16M",  # Buffer size
                            "-pix_fmt",
                            "yuv420p",  # Pixel format for compatibility
                            "-movflags",
                            "+faststart",  # Optimize for web streaming
                        ]
                    )

                # Add output path to command
                command.append(output_path)

                print(
                    f"[VideoRecorder] Running conversion command: {' '.join(command)}"
                )

                # Run the process with timeout
                process = subprocess.Popen(
                    command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )

                # Wait for process to complete (max 5 minutes)
                try:
                    stdout, stderr = process.communicate(timeout=300)
                    if process.returncode != 0:
                        stderr_output = stderr.decode("utf-8", errors="ignore")
                        print(f"[VideoRecorder] ffmpeg error: {stderr_output}")
                        # Check if this is a codec error
                        if (
                            "No such file or directory" in stderr_output
                            or "Unknown encoder" in stderr_output
                        ):
                            # Try again with basic settings
                            print(
                                "[VideoRecorder] Retrying with basic encoder settings..."
                            )
                            basic_command = [
                                "ffmpeg",
                                "-i",
                                input_path,
                                "-c:v",
                                "libx264",
                                "-preset",
                                "medium",
                                "-crf",
                                "23",
                                "-pix_fmt",
                                "yuv420p",
                                "-y",
                                output_path,
                            ]
                            retry_process = subprocess.run(
                                basic_command, capture_output=True, check=False
                            )
                            if (
                                retry_process.returncode == 0
                                and os.path.exists(output_path)
                                and os.path.getsize(output_path) > 0
                            ):
                                print(
                                    f"[VideoRecorder] Retry succeeded with basic settings"
                                )
                                return True
                            else:
                                return False
                        return False
                except subprocess.TimeoutExpired:
                    process.kill()
                    print("[VideoRecorder] ffmpeg conversion timed out after 5 minutes")
                    return False

                # Verify the output file exists and has content
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    print(
                        f"[VideoRecorder] ffmpeg conversion successful: {output_path} ({os.path.getsize(output_path)} bytes)"
                    )
                    return True
                else:
                    print(
                        f"[VideoRecorder] ffmpeg conversion failed - output file missing or empty"
                    )
                    return False
            except Exception as e:
                print(f"[VideoRecorder] ffmpeg conversion failed: {e}")
            print(f"[VideoRecorder] Falling back to OpenCV for conversion...")

            # If ffmpeg failed, use OpenCV as a fallback
            cap = cv2.VideoCapture(input_path)
            if not cap.isOpened():
                print(f"[VideoRecorder] Could not open input video file: {input_path}")
                return False

            # Get video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            print(
                f"[VideoRecorder] Converting video: {width}x{height} @ {fps}fps, {frame_count} frames"
            )

            # Try mp4v codec first (more compatible than H264 with OpenCV)
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")

            # Create output video writer
            try:
                out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

                if not out.isOpened():
                    raise Exception("Could not open output video writer")
            except Exception as e:
                print(
                    f"[VideoRecorder] Failed to create output video writer for {output_path}"
                )

                # Try alternate codec
                try:
                    fourcc = cv2.VideoWriter_fourcc(*"XVID")
                    temp_path = output_path.replace(".mp4", ".avi")
                    out = cv2.VideoWriter(temp_path, fourcc, fps, (width, height))
                    if not out.isOpened():
                        return False
                    output_path = temp_path  # Update path for later handling
                except Exception:
                    return False

            # Process all frames
            frames_processed = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Apply a very light sharpening to improve quality but prevent artifacts
                kernel = np.array(
                    [[-0.3, -0.3, -0.3], [-0.3, 3.4, -0.3], [-0.3, -0.3, -0.3]]
                )
                frame = cv2.filter2D(frame, -1, kernel)

                # Write frame to output
                out.write(frame)
                frames_processed += 1

                # Log progress periodically
                if frames_processed % 100 == 0 or frames_processed == frame_count:
                    print(
                        f"[VideoRecorder] Conversion progress: {frames_processed}/{frame_count} frames"
                    )

            # Release resources
            cap.release()
            out.release()

            # If we created an AVI file, convert it to MP4
            if output_path.endswith(".avi"):
                final_mp4_path = output_path.replace(".avi", ".mp4")
                # Try to convert using ffmpeg (simplified command)
                try:
                    simple_cmd = [
                        "ffmpeg",
                        "-i",
                        output_path,
                        "-c:v",
                        "libx264",
                        "-preset",
                        "fast",
                        "-y",
                        final_mp4_path,
                    ]
                    subprocess.run(simple_cmd, check=False, capture_output=True)

                    if (
                        os.path.exists(final_mp4_path)
                        and os.path.getsize(final_mp4_path) > 0
                    ):
                        print(f"[VideoRecorder] Converted AVI to MP4: {final_mp4_path}")
                        # Remove the temporary AVI file
                        try:
                            os.remove(output_path)
                        except:
                            pass
                        return True
                except:
                    print(
                        f"[VideoRecorder] Failed to convert AVI to MP4, keeping AVI file"
                    )

            # Verify output exists and has content
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(
                    f"[VideoRecorder] OpenCV conversion successful: {output_path} ({os.path.getsize(output_path)} bytes)"
                )
                return True
            else:
                print(
                    f"[VideoRecorder] OpenCV conversion failed - output file missing or empty"
                )
                return False

        except Exception as e:
            print(f"[VideoRecorder] Error converting video to MP4: {e}")
            import traceback

            traceback.print_exc()
            return False

    def combine_videos_for_session(self, session_id):
        """Combine all videos specifically for a given session - improved reliable method"""
        if not session_id:
            print(
                "[VideoRecorder] No session ID provided for combine_videos_for_session"
            )
            return None

        print(
            f"[VideoRecorder] Combining videos for session {session_id} (ENHANCED METHOD)"
        )

        # If there's a recording in progress with this session, stop it first
        if (
            self.recording
            and hasattr(self, "current_session_id")
            and self.current_session_id == session_id
        ):
            print(
                f"[VideoRecorder] Found active recording for session {session_id}, stopping it"
            )
            self.stop_recording()

        # Now gather all videos for this session from all possible sources:
        videos_to_combine = []

        # 1. First check our local session tracking
        if session_id in self.session_videos and self.session_videos[session_id]:
            print(
                f"[VideoRecorder] Found {len(self.session_videos[session_id])} videos in local session_videos"
            )
            videos_to_combine.extend(self.session_videos[session_id])

        # 2. Next check global session tracking
        if (
            hasattr(VideoRecorder, "_all_session_videos")
            and session_id in VideoRecorder._all_session_videos
        ):
            global_session_videos = [
                v
                for v in VideoRecorder._all_session_videos[session_id]
                if v not in videos_to_combine
            ]
            if global_session_videos:
                print(
                    f"[VideoRecorder] Found {len(global_session_videos)} additional videos in global session tracking"
                )
                videos_to_combine.extend(global_session_videos)

        # 3. Look for all AVI and MP4 files in the temp folder containing the session ID
        if os.path.isdir(self.temp_folder):
            for filename in os.listdir(self.temp_folder):
                if (
                    filename.lower().endswith(".avi")
                    or filename.lower().endswith(".mp4")
                ) and session_id in filename:
                    file_path = os.path.join(self.temp_folder, filename)
                    if (
                        os.path.isfile(file_path)
                        and os.path.getsize(file_path) > 0
                        and file_path not in videos_to_combine
                    ):
                        videos_to_combine.append(file_path)
                        print(
                            f"[VideoRecorder] Found session video by name matching: {filename}"
                        )

        # 4. If still no videos, look for all recent videos in the temp folder
        if not videos_to_combine:
            recent_videos = self._find_recent_videos(minutes=30)
            if recent_videos:
                print(
                    f"[VideoRecorder] Adding {len(recent_videos)} recent videos as fallback"
                )
                videos_to_combine = recent_videos

        if not videos_to_combine:
            print(f"[VideoRecorder] No videos found for session {session_id}")
            return None

        print(
            f"[VideoRecorder] Found total of {len(videos_to_combine)} videos for session {session_id}"
        )
        for i, video in enumerate(videos_to_combine, 1):
            if os.path.exists(video):
                print(
                    f"[VideoRecorder] Session video {i}: {video} ({os.path.getsize(video)} bytes)"
                )
            else:
                print(f"[VideoRecorder] Session video {i}: {video} - MISSING")

        # Filter to just valid videos
        valid_videos = []
        for video_path in videos_to_combine:
            if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
                try:
                    cap = cv2.VideoCapture(video_path)
                    if cap.isOpened() and int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) > 0:
                        valid_videos.append(video_path)
                        print(
                            f"[VideoRecorder] Valid video for combining: {video_path} ({int(cap.get(cv2.CAP_PROP_FRAME_COUNT))} frames)"
                        )
                    else:
                        print(f"[VideoRecorder] Invalid video, skipping: {video_path}")
                    cap.release()
                except Exception as e:
                    print(f"[VideoRecorder] Error checking video {video_path}: {e}")
            else:
                print(f"[VideoRecorder] Video not found or empty: {video_path}")

        if not valid_videos:
            print(
                f"[VideoRecorder] No valid videos to combine for session {session_id}"
            )
            return None

        # Create the output file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        final_output_file = os.path.join(
            self.temp_folder, f"workout_session_{session_id}_{timestamp}.mp4"
        )

        # If we have only one valid video, handle it directly
        if len(valid_videos) == 1:
            video_path = valid_videos[0]
            print(
                f"[VideoRecorder] Only one valid video, using it directly: {video_path}"
            )

            # Convert to MP4 if needed
            if not video_path.lower().endswith(".mp4"):
                print(f"[VideoRecorder] Converting single video to MP4 format...")
                if self._convert_to_mp4(video_path, final_output_file):
                    return final_output_file
                else:
                    print(
                        f"[VideoRecorder] Conversion failed, using original format: {video_path}"
                    )
                    return video_path
            else:
                # Just copy the file to the final output location
                import shutil

                try:
                    shutil.copy2(video_path, final_output_file)
                    print(f"[VideoRecorder] Copied video to {final_output_file}")
                    return final_output_file
                except Exception as e:
                    print(f"[VideoRecorder] Error copying file: {e}")
                    return video_path

        # Handle multiple videos
        print(
            f"[VideoRecorder] Combining {len(valid_videos)} videos into a single file"
        )

        # Try to use ffmpeg for combining videos (better quality and faster)
        try:
            import subprocess

            # Create a temporary file listing all videos
            file_list_path = os.path.join(
                self.temp_folder, f"file_list_{timestamp}.txt"
            )
            with open(file_list_path, "w") as f:
                for video in valid_videos:
                    f.write(f"file '{os.path.abspath(video)}'\n")

            # Use ffmpeg to concatenate videos - modified to prevent looping
            ffmpeg_cmd = [
                "ffmpeg",
                "-y",  # Overwrite output if exists
                "-f",
                "concat",  # Use concat demuxer
                "-safe",
                "0",  # Don't require safe file paths
                "-i",
                file_list_path,  # Input file list
                "-c:v",
                "libx264",  # Re-encode with H.264 to ensure compatibility
                "-preset",
                "fast",  # Fast encoding
                "-crf",
                "22",  # Quality level
                "-pix_fmt",
                "yuv420p",  # Ensure compatibility
                "-movflags",
                "+faststart",  # Optimize for web playback
                final_output_file,  # Output file
            ]

            print(f"[VideoRecorder] Running ffmpeg command: {' '.join(ffmpeg_cmd)}")
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

            # If the above command fails, try an alternative approach using the segment muxer
            if result.returncode != 0:
                print(
                    f"[VideoRecorder] First ffmpeg approach failed, trying alternative method..."
                )

                # Create an intermediate file for each video
                temp_files = []
                for i, video in enumerate(valid_videos):
                    temp_file = os.path.join(
                        self.temp_folder, f"temp_{timestamp}_{i}.mp4"
                    )
                    temp_cmd = [
                        "ffmpeg",
                        "-y",
                        "-i",
                        video,
                        "-c:v",
                        "libx264",
                        "-preset",
                        "fast",
                        "-crf",
                        "22",
                        "-pix_fmt",
                        "yuv420p",
                        temp_file,
                    ]
                    subprocess.run(temp_cmd, capture_output=True, check=False)
                    if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                        temp_files.append(temp_file)

                # Create a new list file with the temp files
                if temp_files:
                    with open(file_list_path, "w") as f:
                        for temp_file in temp_files:
                            f.write(f"file '{os.path.abspath(temp_file)}'\n")

                    # Try the concat again with the normalized files
                    alt_cmd = [
                        "ffmpeg",
                        "-y",
                        "-f",
                        "concat",
                        "-safe",
                        "0",
                        "-i",
                        file_list_path,
                        "-c",
                        "copy",  # Now we can use copy because the files are normalized
                        final_output_file,
                    ]
                    print(
                        f"[VideoRecorder] Running alternative ffmpeg command: {' '.join(alt_cmd)}"
                    )
                    result = subprocess.run(alt_cmd, capture_output=True, text=True)

                    # Clean up temp files
                    for temp_file in temp_files:
                        try:
                            os.remove(temp_file)
                        except:
                            pass

            # Check if command succeeded
            if (
                result.returncode == 0
                and os.path.exists(final_output_file)
                and os.path.getsize(final_output_file) > 0
            ):
                # Verify the video doesn't have looping issues
                try:
                    verify_cmd = ["ffmpeg", "-i", final_output_file, "-f", "null", "-"]
                    verify_result = subprocess.run(
                        verify_cmd, capture_output=True, text=True
                    )
                    if verify_result.returncode == 0:
                        print(f"[VideoRecorder] Verified video integrity using ffmpeg")
                    else:
                        print(
                            f"[VideoRecorder] Warning: Video may have issues: {verify_result.stderr}"
                        )
                except Exception as e:
                    print(f"[VideoRecorder] Error verifying video: {e}")

                print(
                    f"[VideoRecorder] Successfully combined videos using ffmpeg: {final_output_file}"
                )

                # Delete the temporary file list
                try:
                    os.remove(file_list_path)
                except:
                    pass

                return final_output_file
            else:
                print(f"[VideoRecorder] ffmpeg error: {result.stderr}")
                # Fall back to OpenCV method
        except Exception as e:
            print(f"[VideoRecorder] Error using ffmpeg for combining: {e}")
            # Fall back to OpenCV method

        # OpenCV method for combining videos
        print("[VideoRecorder] Falling back to OpenCV for combining videos")

        # Determine video properties from the first valid video
        first_video = valid_videos[0]
        cap = cv2.VideoCapture(first_video)
        if not cap.isOpened():
            print(f"[VideoRecorder] Could not open first video: {first_video}")
            return None

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()

        # Create output video writer
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(final_output_file, fourcc, fps, (width, height))

        if not out.isOpened():
            print(f"[VideoRecorder] Could not create output video writer")
            return None

        # Process each video only once, with clear start and end markers
        total_frames = 0
        for video_path in valid_videos:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"[VideoRecorder] Could not open video: {video_path}")
                continue

            video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            print(
                f"[VideoRecorder] Processing video: {video_path} ({video_frames} frames)"
            )

            # Add a visual separator between videos (optional)
            if total_frames > 0:  # Only add separator after the first video
                # Create a blank frame as separator
                separator = np.zeros((height, width, 3), dtype=np.uint8)
                # Add text to show it's moving to next exercise
                cv2.putText(
                    separator,
                    "Next Exercise",
                    (width // 2 - 150, height // 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.5,
                    (255, 255, 255),
                    2,
                )
                # Write the separator for half a second
                for _ in range(int(fps / 2)):
                    out.write(separator)
                    total_frames += 1

            # Reset position to start of video
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            # Read and write all frames
            frames_processed = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Resize frame if needed to match output dimensions
                if frame.shape[1] != width or frame.shape[0] != height:
                    frame = cv2.resize(frame, (width, height))

                out.write(frame)
                frames_processed += 1
                total_frames += 1

                # Log progress periodically
                if frames_processed % 100 == 0:
                    print(
                        f"[VideoRecorder] Processed {frames_processed}/{video_frames} frames from {os.path.basename(video_path)}"
                    )

            cap.release()
            print(
                f"[VideoRecorder] Completed processing video: {video_path} ({frames_processed} frames)"
            )

        # Release output video writer
        out.release()

        # Verify the final video file
        if os.path.exists(final_output_file) and os.path.getsize(final_output_file) > 0:
            try:
                final_cap = cv2.VideoCapture(final_output_file)
                if final_cap.isOpened():
                    final_frames = int(final_cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    final_cap.release()
                    print(
                        f"[VideoRecorder] Successfully combined {len(valid_videos)} videos with {total_frames} total frames (final video: {final_frames} frames)"
                    )

                    if (
                        abs(final_frames - total_frames) > fps
                    ):  # Allow small difference due to container metadata
                        print(
                            f"[VideoRecorder] Warning: Final frame count ({final_frames}) differs from processed frames ({total_frames})"
                        )
                        # This could indicate a looping issue, but we'll still return the file

                    return final_output_file
                else:
                    print(
                        f"[VideoRecorder] Error: Could not verify the final video file"
                    )
            except Exception as e:
                print(f"[VideoRecorder] Error verifying final video: {e}")

        print(f"[VideoRecorder] Failed to create combined video")
        return None

    def combine_videos(self, session_id=None):
        """
        Combine all recorded exercise videos into a single workout video.
        This is an enhanced wrapper around combine_videos_for_session for backward compatibility.
        """
        # If a session ID is provided, use the enhanced session-specific method
        if session_id:
            print(
                f"[VideoRecorder] Using enhanced session-specific video combining for session: {session_id}"
            )
            return self.combine_videos_for_session(session_id)

        # Otherwise fall back to the original method
        print("[VideoRecorder] No session ID provided, using general video combining")

        # If there's a recording in progress, stop it first
        if self.recording:
            print("[VideoRecorder] Found active recording, stopping it first")
            self.stop_recording()

        videos_to_combine = []

        # Use exercise_videos list if available
        if self.exercise_videos:
            print(
                f"[VideoRecorder] Using exercise_videos list with {len(self.exercise_videos)} videos"
            )
            videos_to_combine = self.exercise_videos

        # If no videos, look for recent videos
        if not videos_to_combine:
            recent_videos = self._find_recent_videos(minutes=30)
            if recent_videos:
                print(f"[VideoRecorder] Found {len(recent_videos)} recent videos")
                videos_to_combine = recent_videos

        # If still no videos, return None
        if not videos_to_combine:
            print("[VideoRecorder] No videos found to combine")
            return None

        # Rest of the combining logic - using the same code as in combine_videos_for_session
        # Note: This could be refactored to avoid duplication, but keeping separate for clarity
        # ...

    def continue_recording_session(self, exercise_name, session_id):
        """
        Continue recording in the same session for a new exercise.
        This allows multiple exercises to be recorded in sequence within the same session.

        Args:
            exercise_name: Name of the new exercise being recorded
            session_id: The session ID to continue recording with

        Returns:
            bool: True if successfully started recording, False otherwise
        """
        try:
            print(
                f"[VideoRecorder] Continuing recording session {session_id} with exercise: {exercise_name}"
            )

            # Check if we're already recording and have the same session ID
            if (
                self.recording
                and hasattr(self, "current_session_id")
                and self.current_session_id == session_id
            ):
                # Stop the current recording first to save it
                self.stop_recording()
                print(
                    f"[VideoRecorder] Stopped current recording for continuation in the same session"
                )

            # Important: Don't clear exercise_videos list here, as we need to keep all videos
            # from the same session. The stop_recording method already adds the current video
            # to the exercise_videos list.

            # Set the session ID
            self.current_session_id = session_id

            # Initialize session videos tracking if needed
            if session_id not in self.session_videos:
                self.session_videos[session_id] = []
                print(f"[VideoRecorder] Created tracking for session {session_id}")

            # Check if we have any existing videos that might belong to this session
            recent_videos = self._find_recent_videos(minutes=5)
            if recent_videos:
                for video in recent_videos:
                    if video not in self.session_videos[session_id]:
                        self.session_videos[session_id].append(video)
                print(
                    f"[VideoRecorder] Added {len(recent_videos)} recent videos to session {session_id}"
                )

            # Start recording the new exercise
            self.start_recording(exercise_name, session_id)

            return True
        except Exception as e:
            print(f"[VideoRecorder] Error continuing recording session: {e}")
            import traceback

            traceback.print_exc()
            return False

    def _find_recent_videos(self, minutes=30):
        """Find recent videos in the temp folder"""
        recent_videos = []

        if not os.path.isdir(self.temp_folder):
            return recent_videos

        try:
            now = time.time()
            for filename in os.listdir(self.temp_folder):
                file_path = os.path.join(self.temp_folder, filename)
                if os.path.isfile(file_path) and file_path.lower().endswith(
                    (".mp4", ".avi")
                ):
                    # Check if file was created in the last X minutes
                    file_age = now - os.path.getctime(file_path)
                    if file_age < (minutes * 60) and os.path.getsize(file_path) > 0:
                        recent_videos.append(file_path)

            if recent_videos:
                print(
                    f"[VideoRecorder] Found {len(recent_videos)} recent videos in the last {minutes} minutes"
                )

            return recent_videos
        except Exception as e:
            print(f"[VideoRecorder] Error finding recent videos: {e}")
            return []

    def display_options(self, email, name, final_video_path):
        """Display options for what to do with the final video"""
        if not final_video_path or not os.path.exists(final_video_path):
            print("Error: No video to process")
            return

        print("\n===== VIDEO OPTIONS =====")
        print("What would you like to do with your workout video?")
        print("1. Save & Email")
        print("2. Save Only")
        print("3. Delete")

        choice = None
        while choice not in [1, 2, 3]:
            try:
                choice_input = input("Enter your choice (1, 2, or 3): ").strip()
                choice = int(choice_input)
                if choice not in [1, 2, 3]:
                    print("Invalid choice. Please enter 1, 2, or 3.")
            except ValueError:
                print("Please enter a valid number (1, 2, or 3).")

        print(f"Selected option: {choice}")

        if choice == 1:  # Save & Email
            return self.save_and_email(email, name, final_video_path)
        elif choice == 2:  # Save Only
            return self.save_locally(final_video_path)
        elif choice == 3:  # Delete
            return self.delete_video(final_video_path)

        return None

    def save_locally(self, video_path):
        """Save the video to the local output folder"""
        if not os.path.exists(video_path):
            print(f"[VideoRecorder] Error: Video file not found: {video_path}")
            return False

        output_path = os.path.join(self.output_folder, os.path.basename(video_path))

        # Copy the file
        import shutil

        try:
            # Make sure output directory exists
            os.makedirs(self.output_folder, exist_ok=True)

            # Copy the file
            shutil.copy2(video_path, output_path)
            print(f"[VideoRecorder] Video saved to {output_path}")

            # Verify the file was copied correctly
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                print(f"[VideoRecorder] Error: Failed to copy video to {output_path}")
                return False

            # Check if the video is playable
            try:
                cap = cv2.VideoCapture(output_path)
                if cap.isOpened():
                    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    print(f"[VideoRecorder] Saved video has {frame_count} frames")
                    cap.release()

                    # Mark that videos have been processed so we can clean up
                    self._videos_processed = True

                    return output_path
                else:
                    print(f"[VideoRecorder] Error: Saved video cannot be opened")
                    return False
            except Exception as e:
                print(f"[VideoRecorder] Error verifying saved video: {e}")
                return False
        except Exception as e:
            print(f"[VideoRecorder] Error saving video: {e}")
            import traceback

            traceback.print_exc()
            return False

    def cleanup_temp_files(self):
        """Clean up all temporary video files"""
        print("[VideoRecorder] Starting cleanup of temporary files...")
        try:
            # Create a copy of exercise_videos list to avoid modification during iteration
            videos_to_remove = (
                self.exercise_videos.copy() if hasattr(self, "exercise_videos") else []
            )

            # Don't remove videos that haven't been processed yet
            if not hasattr(self, "_videos_processed") or not self._videos_processed:
                print("[VideoRecorder] Preserving video files for future processing")
                return False

            # Clean up the video files
            removed_count = 0
            for video in videos_to_remove:
                if os.path.exists(video):
                    try:
                        # Check if file is still being accessed
                        try:
                            with open(video, "rb") as f:
                                f.read(1)
                        except IOError:
                            print(
                                f"[VideoRecorder] File {video} is still being accessed, skipping"
                            )
                            continue

                        os.remove(video)
                        removed_count += 1
                        print(f"[VideoRecorder] Removed temporary video: {video}")
                    except Exception as e:
                        print(f"[VideoRecorder] Error removing video {video}: {e}")
                else:
                    print(f"[VideoRecorder] Video not found: {video}")

            # Clear the list
            self.exercise_videos.clear()
            print(f"[VideoRecorder] Removed {removed_count} temporary video files")

            # Clean up temp directory
            temp_dir = os.path.join(self.current_dir, "temp_videos")
            if os.path.exists(temp_dir):
                try:
                    files_removed = 0
                    current_time = time.time()

                    for filename in os.listdir(temp_dir):
                        file_path = os.path.join(temp_dir, filename)
                        if os.path.isfile(file_path):
                            try:
                                # Check if file is still being accessed
                                with open(file_path, "rb") as f:
                                    f.read(1)
                            except IOError:
                                print(
                                    f"[VideoRecorder] File {filename} is still being accessed, skipping"
                                )
                                continue

                            file_age = current_time - os.path.getmtime(file_path)
                            if (
                                file_age > 1200 or file_path in videos_to_remove
                            ):  # 20 minutes or session file
                                try:
                                    os.remove(file_path)
                                    files_removed += 1
                                    print(
                                        f"[VideoRecorder] Removed temp file: {filename}"
                                    )
                                except Exception as e:
                                    print(
                                        f"[VideoRecorder] Error removing temp file {filename}: {e}"
                                    )

                    print(
                        f"[VideoRecorder] Removed {files_removed} additional files from temp directory"
                    )

                    # Create cleanup marker
                    marker_path = os.path.join(
                        temp_dir, f"cleanup_marker_{int(time.time())}.txt"
                    )
                    try:
                        with open(marker_path, "w") as f:
                            f.write(
                                f"Cleanup performed at {datetime.datetime.now().isoformat()}"
                            )
                    except:
                        pass
                except Exception as e:
                    print(f"[VideoRecorder] Error cleaning up temp directory: {e}")

            self._videos_processed = True
            return True
        except Exception as e:
            print(f"[VideoRecorder] Error in cleanup: {e}")
            import traceback

            traceback.print_exc()
            return False

    def save_and_email(self, email, name, video_path):
        """Save the video locally and email it to the user"""
        try:
            # Validate inputs
            if not email or not name:
                print(
                    f"[VideoRecorder] Error: Missing email ({email}) or name ({name})"
                )
                return False

            if not video_path:
                print(f"[VideoRecorder] Error: No video path provided")
                return False

            if not os.path.exists(video_path):
                print(f"[VideoRecorder] Error: Video file does not exist: {video_path}")
                return False

            file_size = os.path.getsize(video_path)
            if file_size == 0:
                print(f"[VideoRecorder] Error: Video file is empty (0 bytes)")
                return False

            print(f"[VideoRecorder] Processing video: {video_path} ({file_size} bytes)")

            # Save the video locally first
            saved_path = self.save_locally(video_path)
            if not saved_path:
                print(
                    f"[VideoRecorder] Warning: Could not save video locally, using original path"
                )
                saved_path = video_path

            # Send the email to the user
            print(f"[VideoRecorder] Sending email to {email} with video attachment")

            try:
                import EmailingSystem

                success = EmailingSystem.email_user_with_video(
                    email, name, 0, 0, saved_path
                )
                if success:
                    print(
                        f"[VideoRecorder] Successfully sent email with video to {email}"
                    )
                    return saved_path
                else:
                    print(f"[VideoRecorder] Failed to send email via EmailingSystem")
                    return False
            except Exception as email_err:
                print(f"[VideoRecorder] Error in email_user_with_video: {email_err}")
                import traceback

                traceback.print_exc()
                return False
        except Exception as e:
            print(f"[VideoRecorder] Error in save_and_email: {e}")
            import traceback

            traceback.print_exc()
            return False

    def _compress_video(self, video_path):
        """Compress a video to a smaller size using ffmpeg if available"""
        try:
            import subprocess

            # Always ensure output is MP4
            if video_path.lower().endswith(".mp4"):
                output_path = video_path.replace(".mp4", "_compressed.mp4")
            else:
                # For any other format, convert to MP4
                output_path = os.path.splitext(video_path)[0] + "_compressed.mp4"

            # Use ffmpeg to compress the video
            ffmpeg_cmd = [
                "ffmpeg",
                "-y",  # Overwrite output file if it exists
                "-i",
                video_path,
                "-vcodec",
                "libx264",
                "-crf",
                "28",  # Higher CRF means more compression
                "-preset",
                "fast",  # Fast encoding
                "-movflags",
                "+faststart",  # Optimize for web playback
                output_path,
            ]

            print(f"[VideoRecorder] Running ffmpeg compression: {' '.join(ffmpeg_cmd)}")
            result = subprocess.run(ffmpeg_cmd, check=True, capture_output=True)

            # Check if output file was created successfully
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(
                    f"[VideoRecorder] Video compressed successfully: {output_path} ({os.path.getsize(output_path)} bytes)"
                )
                return output_path
            else:
                print(
                    f"[VideoRecorder] ffmpeg compression failed to produce a valid output file"
                )

                # Fall back to OpenCV compression if ffmpeg fails
                print(f"[VideoRecorder] Trying OpenCV compression as fallback...")
                return self._compress_with_opencv(video_path, output_path)
        except Exception as e:
            print(f"[VideoRecorder] Error using ffmpeg for compression: {e}")

            # Fall back to OpenCV compression
            print(f"[VideoRecorder] Falling back to OpenCV compression...")
            if video_path.lower().endswith(".mp4"):
                output_path = video_path.replace(".mp4", "_compressed.mp4")
            else:
                output_path = os.path.splitext(video_path)[0] + "_compressed.mp4"

            return self._compress_with_opencv(video_path, output_path)

    def _compress_with_opencv(self, input_path, output_path):
        """Compress video using OpenCV as a fallback method"""
        try:
            # Read input video
            cap = cv2.VideoCapture(input_path)
            if not cap.isOpened():
                print(f"[VideoRecorder] Could not open input video file: {input_path}")
                return None

            # Get video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # Use lower resolution for compression (half the original size)
            comp_width = max(640, width // 2)  # At least 640px wide
            comp_height = int(height * (comp_width / width))  # Keep aspect ratio

            print(
                f"[VideoRecorder] Compressing video from {width}x{height} to {comp_width}x{comp_height}"
            )

            # Create output video writer with mp4v codec
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(output_path, fourcc, fps, (comp_width, comp_height))

            if not out.isOpened():
                print(
                    f"[VideoRecorder] Failed to create output video writer for compression"
                )
                cap.release()
                return None

            # Process frames
            frames_processed = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Resize frame to smaller dimensions
                frame_resized = cv2.resize(frame, (comp_width, comp_height))

                # Optionally reduce quality further
                # (OpenCV doesn't have direct quality control, so we're using resolution reduction)

                out.write(frame_resized)
                frames_processed += 1

                # Log progress occasionally
                if frames_processed % 100 == 0:
                    print(
                        f"[VideoRecorder] Compression progress: {frames_processed}/{frame_count} frames"
                    )

            # Release resources
            cap.release()
            out.release()

            # Verify output
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(
                    f"[VideoRecorder] OpenCV compression successful: {output_path} ({os.path.getsize(output_path)} bytes)"
                )

                # Check if we actually reduced the size
                orig_size = os.path.getsize(input_path)
                new_size = os.path.getsize(output_path)

                if new_size >= orig_size:
                    print(
                        f"[VideoRecorder] Warning: Compressed file is not smaller ({new_size} vs {orig_size} bytes)"
                    )
                    # In this case, we might want to return the original instead
                    try:
                        os.remove(output_path)
                        print(
                            f"[VideoRecorder] Deleted ineffective compressed file: {output_path}"
                        )
                    except Exception as e:
                        print(
                            f"[VideoRecorder] Error deleting ineffective compressed file: {e}"
                        )
                    return input_path

                return output_path
            else:
                print(
                    f"[VideoRecorder] OpenCV compression failed - output file missing or empty"
                )
                return None

        except Exception as e:
            print(f"[VideoRecorder] Error in OpenCV compression: {e}")
            import traceback

            traceback.print_exc()
            return None

    def force_cleanup_temp_videos(self):
        """Aggressively clean up all files in the temp_videos folder without checking flags"""
        print(
            "[VideoRecorder] FORCE CLEANUP: Starting aggressive cleanup of temporary files..."
        )
        try:
            # Clean up temp directory
            temp_dir = os.path.join(self.current_dir, "temp_videos")
            if os.path.exists(temp_dir):
                try:
                    files_removed = 0
                    current_time = time.time()

                    for filename in os.listdir(temp_dir):
                        file_path = os.path.join(temp_dir, filename)
                        if os.path.isfile(file_path):
                            try:
                                # Don't check if file is being accessed, force delete
                                print(
                                    f"[VideoRecorder] FORCE CLEANUP: Attempting to delete {filename}"
                                )

                                # Try multiple deletion strategies
                                try:
                                    # Try regular removal first
                                    os.remove(file_path)
                                    files_removed += 1
                                    print(
                                        f"[VideoRecorder] FORCE CLEANUP: Removed temp file: {filename}"
                                    )
                                except PermissionError:
                                    # If permission error, try to change permissions and retry
                                    try:
                                        print(
                                            f"[VideoRecorder] FORCE CLEANUP: Permission issue, trying to adjust permissions for {filename}"
                                        )
                                        os.chmod(
                                            file_path, 0o777
                                        )  # Give all permissions
                                        os.remove(file_path)
                                        files_removed += 1
                                        print(
                                            f"[VideoRecorder] FORCE CLEANUP: Removed temp file after permission fix: {filename}"
                                        )
                                    except Exception as chmod_err:
                                        print(
                                            f"[VideoRecorder] FORCE CLEANUP: Permission change failed: {chmod_err}"
                                        )

                                        # Try using unlink as a last resort
                                        try:
                                            print(
                                                f"[VideoRecorder] FORCE CLEANUP: Trying unlink for {filename}"
                                            )
                                            os.unlink(file_path)
                                            files_removed += 1
                                            print(
                                                f"[VideoRecorder] FORCE CLEANUP: Removed temp file with unlink: {filename}"
                                            )
                                        except Exception as unlink_err:
                                            print(
                                                f"[VideoRecorder] FORCE CLEANUP: Unlink also failed: {unlink_err}"
                                            )

                                            # If all else fails, schedule the file for deletion on next system boot
                                            if sys.platform == "win32":
                                                try:
                                                    import subprocess

                                                    print(
                                                        f"[VideoRecorder] FORCE CLEANUP: Attempting to schedule deletion via system command for {filename}"
                                                    )
                                                    subprocess.call(
                                                        [
                                                            "cmd",
                                                            "/c",
                                                            f'del /F /Q "{file_path}" > nul 2>&1',
                                                        ]
                                                    )
                                                except Exception as cmd_err:
                                                    print(
                                                        f"[VideoRecorder] FORCE CLEANUP: System command failed: {cmd_err}"
                                                    )
                            except Exception as e:
                                print(
                                    f"[VideoRecorder] FORCE CLEANUP: Error removing temp file {filename}: {e}"
                                )

                    print(
                        f"[VideoRecorder] FORCE CLEANUP: Removed {files_removed} files from temp directory"
                    )

                    # Set processed flag to ensure normal cleanup also works in future
                    self._videos_processed = True

                    # Create cleanup marker
                    marker_path = os.path.join(
                        temp_dir, f"force_cleanup_marker_{int(time.time())}.txt"
                    )
                    try:
                        with open(marker_path, "w") as f:
                            f.write(
                                f"Forced cleanup performed at {datetime.datetime.now().isoformat()}"
                            )
                    except:
                        pass

                    return True
                except Exception as e:
                    print(
                        f"[VideoRecorder] FORCE CLEANUP: Error cleaning up temp directory: {e}"
                    )
                    return False
            else:
                print(
                    f"[VideoRecorder] FORCE CLEANUP: Temp directory {temp_dir} does not exist"
                )
                return False
        except Exception as e:
            print(f"[VideoRecorder] FORCE CLEANUP: Error in force cleanup: {e}")
            import traceback

            traceback.print_exc()
            return False

    def schedule_cleanup(self):
        """Schedule a cleanup after a delay to avoid file lock issues"""
        try:
            cleanup_thread = threading.Thread(target=self._delayed_cleanup)
            cleanup_thread.daemon = True
            cleanup_thread.start()
            print("[VideoRecorder] Scheduled delayed cleanup thread")
            return True
        except Exception as e:
            print(f"[VideoRecorder] Error scheduling cleanup: {e}")
            return False

    def _delayed_cleanup(self):
        """Perform cleanup after a delay to allow file locks to be released"""
        try:
            print("[VideoRecorder] Starting delayed cleanup in 5 seconds...")
            time.sleep(5)  # Wait for 5 seconds

            # Mark videos as processed so cleanup will work
            self._videos_processed = True

            # Try regular cleanup
            try:
                cleanup_result = self.cleanup_temp_files()
                print(f"[VideoRecorder] Delayed cleanup result: {cleanup_result}")
            except Exception as cleanup_err:
                print(f"[VideoRecorder] Error in delayed cleanup: {cleanup_err}")

            # Try force cleanup
            try:
                force_result = self.force_cleanup_temp_videos()
                print(f"[VideoRecorder] Delayed force cleanup result: {force_result}")
            except Exception as force_err:
                print(f"[VideoRecorder] Error in delayed force cleanup: {force_err}")

            # Try API endpoint method as last resort
            try:
                try:
                    # Get the backend URL (localhost if not available)
                    backend_url = os.getenv("BACKEND_URL", "http://localhost:8002")
                    cleanup_url = f"{backend_url}/cleanup-temp-videos"

                    print(
                        f"[VideoRecorder] Calling cleanup API endpoint: {cleanup_url}"
                    )
                    response = requests.post(cleanup_url, timeout=10)

                    if response.status_code == 200:
                        print(
                            f"[VideoRecorder] API cleanup successful: {response.json()}"
                        )
                    else:
                        print(
                            f"[VideoRecorder] API cleanup failed: {response.status_code}"
                        )
                except Exception as req_err:
                    print(f"[VideoRecorder] Error calling cleanup endpoint: {req_err}")
            except ImportError:
                print(
                    "[VideoRecorder] Requests library not available, skipping API cleanup"
                )

            print("[VideoRecorder] Delayed cleanup completed")
        except Exception as e:
            print(f"[VideoRecorder] Error in delayed cleanup thread: {e}")

    def delete_video(self, video_path):
        """Delete a video file"""
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
                print(f"[VideoRecorder] Deleted video: {video_path}")

                # Mark that videos have been processed
                self._videos_processed = True

                # Clean up temp files
                self.cleanup_temp_files()

                # Schedule a delayed cleanup to ensure everything gets removed
                self.schedule_cleanup()

                return True
            else:
                print(f"[VideoRecorder] Video not found: {video_path}")
                return False
        except Exception as e:
            print(f"[VideoRecorder] Error deleting video: {e}")
            return False

    def cleanup(self):
        """Clean up resources and temporary files"""
        if self.recording:
            self.stop_recording()

        # Remove temporary files older than 1 day
        try:
            current_time = time.time()
            for file in os.listdir(self.temp_folder):
                file_path = os.path.join(self.temp_folder, file)
                if (
                    os.path.isfile(file_path)
                    and current_time - os.path.getmtime(file_path) > 86400
                ):
                    os.remove(file_path)
        except Exception as e:
            print(f"Error cleaning up: {e}")

    def add_videos_from_previous_session(self, previous_session_videos):
        """
        Add videos from a previous workout session to be combined with the current session.
        This supports the feature of continuing with different exercises.

        Args:
            previous_session_videos: List of video file paths from the previous session

        Returns:
            bool: True if videos were successfully added, False otherwise
        """
        try:
            if not previous_session_videos:
                print("[VideoRecorder] No previous session videos to add")
                return False

            print(
                f"[VideoRecorder] Adding {len(previous_session_videos)} videos from previous session"
            )
            for i, video_path in enumerate(previous_session_videos):
                print(f"[VideoRecorder] Previous session video {i+1}: {video_path}")

            # Verify the videos exist and are valid
            valid_videos = []
            for video_path in previous_session_videos:
                # Only add videos that exist and have content
                if os.path.exists(video_path):
                    file_size = os.path.getsize(video_path)
                    if file_size > 0:
                        try:
                            # Verify video can be opened
                            cap = cv2.VideoCapture(video_path)
                            if cap.isOpened():
                                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                                if frame_count > 0:
                                    print(
                                        f"[VideoRecorder] Valid previous video: {video_path} ({frame_count} frames, {file_size} bytes)"
                                    )
                                    valid_videos.append(video_path)
                                else:
                                    print(
                                        f"[VideoRecorder] Previous video has no frames: {video_path}"
                                    )
                            else:
                                print(
                                    f"[VideoRecorder] Could not open previous video: {video_path}"
                                )
                            cap.release()
                        except Exception as e:
                            print(
                                f"[VideoRecorder] Error verifying previous video {video_path}: {e}"
                            )
                    else:
                        print(
                            f"[VideoRecorder] Previous video is empty (0 bytes): {video_path}"
                        )
                else:
                    print(f"[VideoRecorder] Previous video not found: {video_path}")

            if not valid_videos:
                print("[VideoRecorder] No valid videos found from previous session")
                return False

            print(
                f"[VideoRecorder] Found {len(valid_videos)} valid videos from previous session"
            )

            # Copy videos to temp_videos folder to ensure they're in the same location
            copied_videos = []
            for video_path in valid_videos:
                try:
                    # Create a new file name in the temp_videos folder
                    timestamp = int(time.time())
                    orig_filename = os.path.basename(video_path)
                    filename = f"continued_workout_{timestamp}_{orig_filename}"
                    temp_folder = os.path.join(self.current_dir, "temp_videos")
                    os.makedirs(temp_folder, exist_ok=True)
                    new_path = os.path.join(temp_folder, filename)

                    # Copy the file
                    import shutil

                    shutil.copy2(video_path, new_path)

                    if os.path.exists(new_path) and os.path.getsize(new_path) > 0:
                        copied_videos.append(new_path)
                        print(
                            f"[VideoRecorder] Copied previous video to: {new_path} ({os.path.getsize(new_path)} bytes)"
                        )
                    else:
                        print(
                            f"[VideoRecorder] Failed to copy previous video to: {new_path}"
                        )
                except Exception as e:
                    print(f"[VideoRecorder] Error copying previous video: {e}")
                    import traceback

                    traceback.print_exc()

            # Add copied videos to exercise_videos list
            for video_path in copied_videos:
                # Add to the beginning of the list so these videos appear first
                self.exercise_videos.insert(0, video_path)

            print(
                f"[VideoRecorder] Added {len(copied_videos)} videos from previous session to exercise_videos list"
            )
            print(
                f"[VideoRecorder] Current exercise_videos list has {len(self.exercise_videos)} videos"
            )

            return len(copied_videos) > 0

        except Exception as e:
            print(f"[VideoRecorder] Error adding videos from previous session: {e}")
            import traceback

            traceback.print_exc()
            return False

    def start_workout_session(self, exercise_name, session_id=None):
        """
        Start a new workout session recording.
        This should be called when the user enters a workout page (/workout?exercise=...)
        """
        if not self.workout_active:
            print(
                f"[VideoRecorder] Starting new workout session for exercise: {exercise_name}"
            )
            self.workout_active = True
            self.last_exercise_name = exercise_name
            return self.start_recording(exercise_name, session_id)
        return False

    def pause_recording(self):
        """
        Pause the current recording without stopping it.
        This is used when navigating away from workout page temporarily.
        """
        if self.recording and not self.is_paused:
            print("[VideoRecorder] Pausing recording")
            self.is_paused = True
            self.workout_active = False
            return True
        return False

    def resume_recording(self):
        """
        Resume a paused recording.
        This is used when returning to the workout page.
        """
        if self.is_paused and self.last_exercise_name:
            print(
                f"[VideoRecorder] Resuming recording for exercise: {self.last_exercise_name}"
            )
            self.is_paused = False
            self.workout_active = True
            return self.start_recording(
                self.last_exercise_name, self.current_session_id
            )
        return False

    def stop_workout_session(self):
        """
        Stop the current workout session recording.
        This should be called when the user clicks "Stop Workout" or navigates away.
        """
        if self.recording:
            print("[VideoRecorder] Stopping workout session")
            self.workout_active = False
            self.is_paused = False
            return self.stop_recording()
        return False

    def handle_navigation_away(self):
        """
        Handle when user navigates away from workout page.
        This will pause the recording if active.
        """
        if self.recording and self.workout_active:
            print(
                "[VideoRecorder] User navigated away from workout page, pausing recording"
            )
            return self.pause_recording()
        return False

    def handle_workout_continuation(self):
        """
        Handle when user chooses "Do another workout?".
        This will resume the current session if it was paused.
        """
        if self.is_paused and self.last_exercise_name:
            print("[VideoRecorder] User chose to continue workout, resuming recording")
            return self.resume_recording()
        return False
