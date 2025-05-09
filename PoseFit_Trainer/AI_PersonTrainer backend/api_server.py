# Configure absl logging before MediaPipe import to suppress warnings
import logging
import os
import sys
import uuid
import asyncio
import time
from dotenv import load_dotenv
import absl.logging
import socket
import uvicorn

# Redirect absl logging to null to silence TensorFlow warnings
absl.logging.set_verbosity(absl.logging.ERROR)
# Disable TensorFlow logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Disable all TF logging
os.environ['MEDIAPIPE_DISABLE_GPU'] = '1'  # Force CPU usage

# Load environment variables from .env file
load_dotenv()

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Configure logger
logger = logging.getLogger("api_server")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# Suppress TF and MediaPipe warnings
logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('mediapipe').setLevel(logging.ERROR)

# Function to check if a port is available
def is_port_available(port):
    """Check if a port is available for binding"""
    try:
        # Create a socket object
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set socket options
        test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Attempt to bind to the port
        test_socket.bind(('0.0.0.0', port))
        # If we get here, the port is available
        test_socket.close()
        return True
    except socket.error:
        # Port is not available
        return False

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Body, Request, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List, Callable
import json
import cv2
import numpy as np
import mediapipe as mp
import base64
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import DatabaseSys as db_sys
from UserProfile import UserProfileManager
import AIWorkoutCoach as ai_coach
from ExercisesModule import simulate_target_exercies, VideoStream
import EmailingSystem as email_sys
from fastapi.responses import JSONResponse
import time
from collections import defaultdict
import mimetypes
from contextlib import asynccontextmanager
from threading import Lock

# Rate limiting middleware
class RateLimiter:
    def __init__(self, limit: int = 10, window: int = 60):
        self.limit = limit  # Number of requests allowed
        self.window = window  # Time window in seconds
        self.requests = defaultdict(list)  # IP -> list of request times
        
    async def __call__(self, request: Request, call_next: Callable):
        # Get client IP
        ip = request.client.host
        
        # Get current time
        now = time.time()
        
        # Remove old requests outside the window
        self.requests[ip] = [req_time for req_time in self.requests[ip] 
                             if now - req_time < self.window]
        
        # Check if request count exceeds limit
        if len(self.requests[ip]) >= self.limit:
            if request.url.path in ['/token', '/register', '/verify-email', '/resend-verification']:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests, please try again later."}
                )
        
        # Add current request
        self.requests[ip].append(now)
        
        # Process the request
        response = await call_next(request)
        return response

# Fix the deprecated on_event usage with proper lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application startup and shutdown events"""
    # Startup code
    app.state.start_time = time.time()
    logger.info("API server started successfully")
    yield
    # Shutdown code
    logger.info("API server shutting down")

# Initialize FastAPI app with improved documentation and lifespan
app = FastAPI(
    title="PoseFit AI Personal Trainer API",
    description="""
    ## PoseFit AI Personal Trainer API

    This API provides endpoints for real-time pose detection and exercise tracking.
    
    ### Features

    * **User Authentication**: Register and authenticate users
    * **Pose Detection**: Detect human poses in real-time using computer vision
    * **Workout Tracking**: Start, monitor, and complete workout sessions
    * **Video Processing**: Record and share workout videos
    
    ### Getting Started

    1. Register a new user using `/register`
    2. Verify your email using `/verify-email`
    3. Log in using `/token` to get an access token
    4. Start a workout session using `/start-workout`
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Add redirects for standard documentation URLs
from fastapi.responses import RedirectResponse

@app.api_route("/docs", methods=["GET", "HEAD"], include_in_schema=False)
async def docs_redirect(request: Request):
    """Redirect from /docs to /api/docs"""
    return RedirectResponse(url="/api/docs")

@app.api_route("/redoc", methods=["GET", "HEAD"], include_in_schema=False)
async def redoc_redirect(request: Request):
    """Redirect from /redoc to /api/redoc"""
    return RedirectResponse(url="/api/redoc")

@app.api_route("/openapi.json", methods=["GET", "HEAD"], include_in_schema=False)
async def openapi_redirect(request: Request):
    """Redirect from /openapi.json to /api/openapi.json"""
    return RedirectResponse(url="/api/openapi.json")

# Define a custom StaticFiles class to add caching headers
class CachedStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if response.status_code == 200:
            # Add cache headers for static files (cache for 1 week)
            response.headers['Cache-Control'] = 'public, max-age=604800, immutable'
        return response

# Mount static files with caching
app.mount("/static", CachedStaticFiles(directory=os.path.join(current_dir, "static")), name="static")

# Initialize templates
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

# Initialize MediaPipe Pose with optimized settings
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Optimize MediaPipe pose detection based on environment variables
min_detection_confidence = float(os.getenv("MP_MIN_DETECTION_CONFIDENCE", "0.5"))
min_tracking_confidence = float(os.getenv("MP_MIN_TRACKING_CONFIDENCE", "0.5"))
enable_segmentation = os.getenv("MP_ENABLE_SEGMENTATION", "False").lower() == "true"
model_complexity = int(os.getenv("MP_MODEL_COMPLEXITY", "1"))  # 0, 1, or 2

pose = mp_pose.Pose(
    min_detection_confidence=min_detection_confidence,
    min_tracking_confidence=min_tracking_confidence,
    enable_segmentation=enable_segmentation,
    model_complexity=model_complexity,
    static_image_mode=False
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security configurations
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")  # Load from environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    weight: Optional[float] = None
    height: Optional[float] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    verified: bool = False

class EmailVerificationRequest(BaseModel):
    email: str
    code: str

class ResendVerificationRequest(BaseModel):
    email: str

class WorkoutStartRequest(BaseModel):
    exercise: str
    sets: int
    reps: int

# Password reset request and reset endpoints
class ResetPasswordRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    email: EmailStr
    reset_code: str
    new_password: str

# Add a global progress tracker for video processing tasks
task_progress = {}
task_progress_lock = Lock()

# Helper function to update progress
def update_task_progress(task_id, progress, status=None, message=None):
    """Update the progress of a task."""
    with task_progress_lock:
        if task_id not in task_progress:
            task_progress[task_id] = {
                "progress": 0,
                "status": "initializing",
                "message": "Task initialized",
                "start_time": time.time(),
                "last_update": time.time()
            }
        
        task_progress[task_id]["progress"] = progress
        if status:
            task_progress[task_id]["status"] = status
        if message:
            task_progress[task_id]["message"] = message
        task_progress[task_id]["last_update"] = time.time()

# Helper functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # Just verify the user exists in the database
    user = db_sys.get_user(email)
    if user is None:
        raise credentials_exception
        
    return user

# Add rate limiting middleware for auth endpoints
@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    # Apply rate limiting only to auth endpoints
    limiter = RateLimiter(limit=20, window=60)  # 20 requests per minute
    if request.url.path in ['/token', '/register', '/verify-email', '/resend-verification', 
                         '/request-password-reset', '/reset-password']:
        return await limiter(request, call_next)
    return await call_next(request)

# API endpoints
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db_sys.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=User)
async def register_user(user: UserCreate):
    try:
        user_db = db_sys.load_user_database()
        if user_db and user.email in user_db:
            raise HTTPException(status_code=400, detail="Email already registered")
        user_data = {
            "email": user.email,
            "password": user.password,  # DatabaseSys will hash this
            "first_name": user.first_name,
            "last_name": user.last_name,
            "age": user.age if user.age else None,
            "gender": user.gender if user.gender else None,
            "weight": user.weight if user.weight else None,
            "height": user.height if user.height else None
        }
        db_sys.register_user_api(user_data)
        verification_code = email_sys.generate_verification_code()
        try:
            email_sys.send_verification_email(user.email, verification_code)
        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")
            # Continue with registration even if email fails
        response_data = user_data.copy()
        del response_data["password"]
        response_data["verified"] = False
        return response_data
    except ValueError as ve:
        logger.error(f"ValueError in register_user: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Exception in register_user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify-email")
async def verify_email(request: EmailVerificationRequest = Body(...)):
    try:
        logger.info(f"Verifying email for user: {request.email}")
        # Check if user exists
        user_db = db_sys.load_user_database()
        if request.email not in user_db:
            raise HTTPException(status_code=404, detail="User not found")
        user = user_db[request.email]
        
        # Check if already verified, handle gracefully
        if user.get("verified", False):
            # Already verified, return token anyway
            access_token = create_access_token(data={"sub": request.email})
            
            # Include verification time if needed
            current_time = time.time()
            user_db[request.email]["verification_time"] = current_time
            db_sys.save_user_database(user_db)
            
            # Return with appropriate headers for CORS
            return JSONResponse(
                content={
                    "message": "Email already verified", 
                    "access_token": access_token, 
                    "token_type": "bearer",
                    "user_email": request.email
                },
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": "true",
                }
            )
        
        # Mark user as verified and save
        user_db[request.email]["verified"] = True
        # Add verification timestamp
        user_db[request.email]["verification_time"] = time.time()
        db_sys.save_user_database(user_db)
        
        logger.info(f"Email verified successfully for: {request.email}")
        
        # Generate JWT token for the user
        access_token = create_access_token(data={"sub": request.email})
        
        # Return success response with token and necessary headers
        return JSONResponse(
            content={
                "message": "Email verified successfully", 
                "access_token": access_token, 
                "token_type": "bearer",
                "user_email": request.email,
                "verified": True
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true",
            }
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error verifying email: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    try:
        user_profile_manager = UserProfileManager()
        profile = user_profile_manager.load_profile(current_user["email"])
        if not profile:
            profile = user_profile_manager.create_user_profile(
                current_user["email"],
                current_user["first_name"],
                current_user["last_name"],
                current_user.get("age"),
                current_user.get("gender"),
                current_user.get("weight"),
                current_user.get("height")
            )
        return profile
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/start-workout")
async def start_workout(
    workout: WorkoutStartRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Normalize exercise name (replace hyphens with underscores)
        exercise_name = workout.exercise.replace('-', '_')
        logger.info(f"Starting workout: {exercise_name} with {workout.sets} sets and {workout.reps} reps")
        # Map exercise names to valid method names if needed
        exercise_method_map = {
            "bicep_curls": "bicep_curls",
            "push_ups": "push_ups",
            "squats": "squats",
            "mountain_climbers": "mountain_climbers",
            "bicep-curls": "bicep_curls",
            "push-ups": "push_ups"
        }
        # Use mapped method name if available, otherwise use normalized name
        exercise_method = exercise_method_map.get(exercise_name, exercise_name)
        # Create a new workout session using simulate_target_exercies
        session = simulate_target_exercies(
            sets=workout.sets,
            reps=workout.reps,
            camera_index=0,  # Use default camera
            exercise_type=exercise_method  # Pass the mapped exercise type
        )
        # Set the user profile (with email) on the session
        session.user_profile = current_user
        logger.info(f"Set user_profile for session: {current_user.get('email')}")
        # Store the session
        session_id = str(uuid.uuid4())
        simulate_target_exercies._active_sessions[session_id] = session
        return {
            "session_id": session_id,
            "stream_url": f"/workout-stream/{session_id}"
        }
    except ValueError as ve:
        logger.error(f"Validation error starting workout: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error starting workout: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start workout: {str(e)}")

@app.post("/stop-workout")
async def stop_workout(session_id: str = Form(...)):
    try:
        logger.info(f"Stopping workout for session: {session_id}")
        session = simulate_target_exercies.get_workout_session(session_id)
        if session:
            session.stopped = True  # Signal all exercise loops to stop
            # Stop and release video stream
            if hasattr(session, 'video_stream') and session.video_stream is not None:
                logger.info("Stopping video stream...")
                session.video_stream.stop()
                if hasattr(session.video_stream, 'stream') and session.video_stream.stream is not None:
                    logger.info("Releasing camera resource...")
                    session.video_stream.stream.release()
            # Release camera from target_exercises
            if hasattr(session, 'target_exercises') and session.target_exercises is not None:
                session.target_exercises.release_camera()
                logger.info("Called release_camera() on target_exercises.")
            # Join thread if exists
            if hasattr(session, 'exercise_thread') and session.exercise_thread is not None:
                logger.info("Joining exercise thread...")
                session.exercise_thread.join(timeout=2)
            logger.info("Workout stopped and camera released.")
            return {"message": "Workout session stopped and camera released successfully"}
        return {"error": "Session not found"}
    except Exception as e:
        logger.error(f"Error in stop_workout: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workout-history")
async def get_workout_history(current_user: dict = Depends(get_current_user)):
    try:
        user_profile_manager = UserProfileManager()
        profile = user_profile_manager.load_profile(current_user["email"])
        if not profile or "workout_history" not in profile:
            return []
        return profile["workout_history"]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/detect-pose")
async def detect_pose(file: UploadFile = File(...)):
    try:
        # Read the image file
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image data")

        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame with MediaPipe Pose
        results = pose.process(frame_rgb)
        
        if not results.pose_landmarks:
            return {"landmarks": None, "message": "No pose detected"}

        # Convert landmarks to list format
        landmarks_list = []
        for landmark in results.pose_landmarks.landmark:
            landmarks_list.append({
                "x": landmark.x,
                "y": landmark.y,
                "z": landmark.z,
                "visibility": landmark.visibility
            })

        # Draw the pose landmarks on the frame
        frame_rgb.flags.writeable = True
        mp_drawing.draw_landmarks(
            frame_rgb,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
        )
        
        # Convert the frame back to BGR for encoding
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        
        # Encode the frame to base64
        _, buffer = cv2.imencode('.jpg', frame_bgr)
        img_base64 = base64.b64encode(buffer).decode('utf-8')

        return {
            "landmarks": landmarks_list,
            "processed_image": img_base64,
            "message": "Pose detected successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/resend-verification")
async def resend_verification(request: ResendVerificationRequest = Body(...)):
    try:
        # Sanitize email: remove leading/trailing quotes and whitespace
        clean_email = str(request.email).strip().strip("'\"")
        logger.info(f"Resend verification requested for: {clean_email}")
        user_db = db_sys.load_user_database()
        if clean_email not in user_db:
            raise HTTPException(status_code=404, detail="User not found")
        verification_code = email_sys.generate_verification_code()
        expiry = (datetime.utcnow() + timedelta(minutes=30)).timestamp()
        user_db[clean_email]["verification_code"] = verification_code
        user_db[clean_email]["verification_code_expiry"] = expiry
        db_sys.save_user_database(user_db)
        try:
            email_sys.send_verification_email(clean_email, verification_code)
            logger.info(f"Verification code resent successfully to: {clean_email}")
            return {"message": "Verification code resent successfully"}
        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to send verification email"
            )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Exception in resend_verification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-frame")
async def process_frame(session_id: str = Form(...)):
    try:
        # Get workout session
        workout_session = simulate_target_exercies.get_workout_session(session_id)
        if not workout_session:
            return JSONResponse(
                status_code=404,
                content={"error": "Workout session not found"}
            )
            
        # In web mode, we don't need to capture new frames here
        # Just get the latest frame and metrics from the session
        metrics = workout_session.process_frame()
        
        # Return the encoded frame and metrics
        return metrics
        
    except Exception as e:
        logger.error(f"Error processing frame: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process frame: {str(e)}"}
        )

@app.get("/workout-stream/{session_id}")
async def workout_stream(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        session = simulate_target_exercies.get_workout_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Workout session not found")
            
        return StreamingResponse(
            generate_frames(session),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def generate_frames(session):
    """Generate video frames for streaming with performance optimizations"""
    try:
        last_frame_time = time.time()
        frame_interval = float(os.getenv("FRAME_INTERVAL", "0.033"))  # ~30 FPS by default
        downscale_factor = float(os.getenv("DOWNSCALE_FACTOR", "1.0"))  # No downscaling by default
        
        while True:
            # Rate limit frame processing to reduce CPU usage
            current_time = time.time()
            time_diff = current_time - last_frame_time
            
            if time_diff < frame_interval:
                await asyncio.sleep(frame_interval - time_diff)
            
            # Get the latest metrics with the processed frame
            metrics = session.process_frame()
            last_frame_time = time.time()
            
            if 'processed_image' in metrics:
                # Convert base64 back to binary for streaming
                frame_bytes = base64.b64decode(metrics['processed_image'])
                
                # Optionally resize the image to reduce bandwidth
                if downscale_factor != 1.0:
                    try:
                        nparr = np.frombuffer(frame_bytes, np.uint8)
                        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        if img is not None:
                            h, w = img.shape[:2]
                            new_h, new_w = int(h / downscale_factor), int(w / downscale_factor)
                            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
                            _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 85])
                            frame_bytes = buffer.tobytes()
                    except Exception as e:
                        logger.error(f"Error resizing frame: {e}")
                
                # Yield frame in proper format for streaming
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            else:
                # Create blank frame with text if no image available
                frame = np.zeros((550, 980, 3), dtype=np.uint8)
                cv2.putText(
                    frame, 
                    "Waiting for camera...", 
                    (frame.shape[1]//2 - 150, frame.shape[0]//2),
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1, 
                    (255, 255, 255), 
                    2
                )
                
                # Encode to jpeg
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                frame_bytes = buffer.tobytes()
                
                # Yield blank frame
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    except Exception as e:
        logger.error(f"Error generating frames: {str(e)}")
        # Return a blank frame on error
        frame = np.zeros((550, 980, 3), dtype=np.uint8)
        cv2.putText(
            frame, 
            f"Error: {str(e)}", 
            (frame.shape[1]//2 - 150, frame.shape[0]//2),
            cv2.FONT_HERSHEY_SIMPLEX, 
            1, 
            (255, 0, 0), 
            2
        )
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/workout", response_class=HTMLResponse)
async def workout_page(
    request: Request,
    exercise: str = Query("bicep_curls", description="Exercise type"),
    sets: int = Query(3, description="Number of sets"),
    reps: int = Query(10, description="Number of reps per set")
):
    return templates.TemplateResponse(
        "workout.html",
        {
            "request": request,
            "exercise": exercise,
            "sets": sets,
            "reps": reps
        }
    )

@app.get("/workout-metrics/{session_id}")
async def get_workout_metrics(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        session = simulate_target_exercies.get_workout_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Workout session not found")
            
        # Get metrics from the session using process_frame without image data
        metrics = session.process_frame()
        
        # Remove processed_image field if present to reduce response size
        if 'processed_image' in metrics:
            del metrics['processed_image']
            
        return metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pause-workout")
async def pause_workout(session_id: str = Form(...)):
    try:
        logger.info(f"Pausing workout for session: {session_id}")
        session = simulate_target_exercies.get_workout_session(session_id)
        if session and hasattr(session, 'target_exercises') and session.target_exercises is not None:
            session.stopped = True
            session.target_exercises.release_camera()
            logger.info("Called release_camera() on target_exercises (pause).");
            return {"message": "Workout session paused and camera released successfully"}
        return {"error": "Session or target_exercises not found"}
    except Exception as e:
        logger.error(f"Error in pause_workout: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/resume-workout")
async def resume_workout(session_id: str = Form(...)):
    try:
        session = simulate_target_exercies.get_workout_session(session_id)
        if session and hasattr(session, 'video_stream'):
            session.video_stream.stopped = False
            session.video_stream.start()
            return {"message": "Workout session resumed successfully"}
        return {"error": "Session or video stream not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save-video")
async def save_video(session_id: str = Form(...)):
    try:
        session = simulate_target_exercies.get_workout_session(session_id)
        if session and hasattr(session, 'video_recorder'):
            final_video_path = session.video_recorder.combine_videos()
            saved_path = session.video_recorder.save_locally(final_video_path)
            return {"message": "Video saved", "path": saved_path}
        return {"error": "Session or video recorder not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save-and-email-video")
async def save_and_email_video(request: Request, session_id: str = Form(...), current_user: dict = Depends(get_current_user)):
    try:
        task_id = f"video-{session_id}-{int(time.time())}"
        update_task_progress(task_id, 0, "starting", "Initializing video processing...")
        
        logger.info(f"Save and email video for session: {session_id}")
        
        # Get session and ensure it exists
        session = simulate_target_exercies.get_workout_session(session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            update_task_progress(task_id, 0, "error", "Session not found")
            return {"error": "Session not found", "task_id": task_id}
        
        # Get user info for email
        user_email = current_user.get("email", None)
        user_name = current_user.get("first_name", current_user.get("name", "User"))
        
        if not user_email:
            logger.error("Missing email address for user")
            update_task_progress(task_id, 0, "error", "Missing email address")
            return {"error": "User email not found", "task_id": task_id}
        
        update_task_progress(task_id, 10, "processing", "Initializing video recorder...")
        
        # Step 1: Ensure VideoRecorder is initialized
        if not hasattr(session, 'video_recorder') or session.video_recorder is None:
            logger.info(f"Creating new video recorder for session {session_id}")
            try:
                from VideoRecorder import VideoRecorder
                session.video_recorder = VideoRecorder(progress_callback=lambda p, msg: update_task_progress(task_id, 10 + int(p * 0.6), "processing", msg))
                logger.info("Successfully created VideoRecorder")
            except Exception as e:
                logger.error(f"Error creating video recorder: {e}")
                update_task_progress(task_id, 0, "error", f"Failed to create video recorder: {str(e)}")
                return {"error": "Failed to create video recorder", "task_id": task_id}
        
        update_task_progress(task_id, 20, "processing", "Stopping active recording...")
        
        # Step 2: Stop recording if currently active
        if hasattr(session.video_recorder, 'recording') and session.video_recorder.recording:
            logger.info("Stopping active recording")
            try:
                session.video_recorder.stop_recording()
                logger.info("Successfully stopped recording")
            except Exception as e:
                logger.error(f"Error stopping recording: {e}")
                update_task_progress(task_id, 20, "warning", f"Warning: Error stopping recording: {str(e)}")
        
        update_task_progress(task_id, 30, "processing", "Combining videos...")
        
        # Step 3: Combine all videos for this session using the enhanced method
        logger.info(f"Combining all videos for session: {session_id}")
        final_video_path = session.video_recorder.combine_videos_for_session(session_id)
        
        # Step 4: Check if a valid video was created
        if not final_video_path or not os.path.exists(final_video_path):
            logger.error("No valid video found after combining")
            update_task_progress(task_id, 30, "error", "No video file available")
            return {"error": "No video file available. Please ensure a workout was recorded.", "task_id": task_id}
        
        if os.path.getsize(final_video_path) == 0:
            logger.error(f"Video file is empty: {final_video_path}")
            update_task_progress(task_id, 30, "error", "Video file is empty")
            return {"error": "Video file is empty. Please try recording again.", "task_id": task_id}
        
        logger.info(f"Successfully combined videos to: {final_video_path} ({os.path.getsize(final_video_path)} bytes)")
        update_task_progress(task_id, 70, "processing", "Saving video locally...")
        
        # Step 5: Save video locally for backup
        saved_path = None
        try:
            saved_path = session.video_recorder.save_locally(final_video_path)
            if saved_path:
                logger.info(f"Successfully saved video locally: {saved_path}")
            else:
                logger.info("Failed to save video locally, continuing with original path")
                saved_path = final_video_path
        except Exception as save_err:
            logger.error(f"Error saving video locally: {save_err}")
            saved_path = final_video_path  # Use original path as fallback
            update_task_progress(task_id, 70, "warning", f"Warning: Could not save locally: {str(save_err)}")
        
        update_task_progress(task_id, 80, "processing", "Sending email with video...")
        
        # Step 6: Send the email with the video
        logger.info(f"Sending combined workout video to {user_email}")
        
        # Try handle_video_options first if available
        if hasattr(session, 'handle_video_options'):
            try:
                result = session.handle_video_options(saved_path, user_email, user_name)
                if result:
                    logger.info("Successfully sent video via handle_video_options")
                    update_task_progress(task_id, 100, "completed", "Video saved and sent successfully")
                    return {
                        "message": "Video saved and sent successfully", 
                        "path": result,
                        "task_id": task_id
                    }
            except Exception as e:
                logger.error(f"Error in handle_video_options: {e}")
                update_task_progress(task_id, 80, "warning", f"Warning: Error in video options: {str(e)}")
                # Fall through to direct method
        
        # Use direct email_user_with_video as fallback
        try:
            from EmailingSystem import email_user_with_video
            result = email_user_with_video(user_email, user_name, 0, 0, saved_path)
            if result:
                logger.info("Successfully sent video via direct email method")
                
                # Mark videos as processed so they will be deleted in cleanup
                if hasattr(session, 'video_recorder') and session.video_recorder:
                    session.video_recorder._videos_processed = True
                    # Clean up temp videos immediately
                    try:
                        update_task_progress(task_id, 90, "processing", "Cleaning up temporary files...")
                        cleanup_result = session.video_recorder.cleanup_temp_files()
                        logger.info(f"Temp video cleanup result: {cleanup_result}")
                    except Exception as cleanup_err:
                        logger.error(f"Error during temp video cleanup: {cleanup_err}")
                        update_task_progress(task_id, 90, "warning", f"Warning: Cleanup issue: {str(cleanup_err)}")
                    
                    # Also force cleanup for maximum effectiveness
                    try:
                        force_cleanup_result = session.video_recorder.force_cleanup_temp_videos()
                        logger.info(f"Force cleanup result: {force_cleanup_result}")
                    except Exception as force_err:
                        logger.error(f"Error during force cleanup: {force_err}")
                
                update_task_progress(task_id, 100, "completed", "Video saved and sent successfully")
                return {
                    "message": "Video saved and sent successfully", 
                    "path": saved_path,
                    "task_id": task_id
                }
            else:
                logger.info("Direct email failed, returning path to saved video")
                update_task_progress(task_id, 90, "partial", "Video saved but email failed")
                return {
                    "message": "Video saved but email failed", 
                    "path": saved_path,
                    "task_id": task_id
                }
        except Exception as email_err:
            logger.error(f"Error sending email: {email_err}")
            import traceback
            traceback.print_exc()
            
            # At least return the saved path if we have one
            if saved_path and os.path.exists(saved_path):
                update_task_progress(task_id, 80, "partial", f"Video saved but not emailed: {str(email_err)}")
                return {
                    "message": "Video saved but not emailed", 
                    "path": saved_path,
                    "task_id": task_id
                }
            else:
                update_task_progress(task_id, 0, "error", f"Failed to send email: {str(email_err)}")
                return {"error": f"Failed to send email: {str(email_err)}", "task_id": task_id}
    except Exception as e:
        logger.error(f"Unhandled error in save-and-email-video: {e}")
        import traceback
        traceback.print_exc()
        update_task_progress(task_id, 0, "error", f"Server error: {str(e)}")
        return {"error": f"Server error: {str(e)}", "task_id": task_id}

@app.post("/delete-video")
async def delete_video(session_id: str = Form(...)):
    try:
        session = simulate_target_exercies.get_workout_session(session_id)
        if session and hasattr(session, 'video_recorder'):
            final_video_path = session.video_recorder.combine_videos()
            session.video_recorder.delete_video(final_video_path)
            return {"message": "Video deleted"}
        return {"error": "Session or video recorder not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/release-all-cameras")
async def release_all_cameras():
    try:
        from ExercisesModule import simulate_target_exercies
        simulate_target_exercies.release_all_cameras()
        return {"message": "All cameras released for all active sessions."}
    except Exception as e:
        logger.error(f"Error in release_all_cameras: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/continue-workout")
async def continue_workout(
    session_id: str = Form(...),
    exercise: str = Form(...),
    sets: int = Form(...),
    reps: int = Form(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        logger.info(f"Continue workout for session: {session_id} with new exercise: {exercise}")
        
        # Get the existing session
        session = simulate_target_exercies.get_workout_session(session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            return {"error": "Session not found"}
        
        # Normalize exercise name (replace hyphens with underscores)
        exercise_name = exercise.replace('-', '_')
        logger.info(f"Continuing with exercise: {exercise_name}, {sets} sets, {reps} reps")
        
        # Stop current recording if active
        if hasattr(session, 'video_recorder') and session.video_recorder:
            if session.video_recorder.recording:
                session.video_recorder.stop_recording()
                logger.info(f"Stopped current recording to prepare for next exercise")
        
        # Update the session with new exercise parameters
        session.sets = sets
        session.reps = reps
        session.exercise_type = exercise_name
        
        # Map exercise names to valid method names if needed
        exercise_method_map = {
            "bicep_curls": "bicep_curls",
            "push_ups": "push_ups",
            "squats": "squats",
            "mountain_climbers": "mountain_climbers",
            "bicep-curls": "bicep_curls",
            "push-ups": "push_ups"
        }
        exercise_method = exercise_method_map.get(exercise_name, exercise_name)
        
        # Update the target exercise
        if hasattr(session, 'target_exercises') and session.target_exercises:
            session.target_exercises.exercise_type = exercise_method
            session.target_exercises.target_sets = sets
            session.target_exercises.target_reps = reps
            session.target_exercises.current_set = 0
            session.target_exercises.reps_completed = 0
            session.target_exercises.exercise_completed = False
            logger.info(f"Updated target exercise parameters")
        
        # Continue recording in the same session with the new exercise
        if hasattr(session, 'video_recorder') and session.video_recorder:
            session.video_recorder.continue_recording_session(exercise_name, session_id)
            logger.info(f"Started recording for new exercise in the same session")
        
        # If video stream is stopped, restart it
        if hasattr(session, 'video_stream') and session.video_stream:
            if session.video_stream.stopped:
                session.video_stream.stopped = False
                session.video_stream.start()
                logger.info(f"Restarted video stream")
        
        # Reset the session stop flag
        session.stopped = False
        
        return {
            "message": f"Successfully continued workout with {exercise_name}",
            "session_id": session_id,
            "stream_url": f"/workout-stream/{session_id}"
        }
    except Exception as e:
        logger.error(f"Error in continue_workout: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Server error: {str(e)}"}

@app.post("/cleanup-temp-videos")
async def cleanup_temp_videos():
    """Endpoint to clean up all files in the temp_videos directory"""
    try:
        logger.info("Running temp videos cleanup")
        
        # Import and run the cleanup function
        try:
            from cleanup_temp import clean_temp_videos
            result = clean_temp_videos()
            if result:
                return {"message": "Successfully cleaned up temp_videos directory", "success": True}
            else:
                return {"message": "Cleanup completed with some errors", "success": False}
        except ImportError:
            # If import fails, do manual cleanup
            import os
            import time
            from datetime import datetime
            
            logger.info("Cleanup module not found, doing manual cleanup")
            current_dir = os.path.dirname(os.path.abspath(__file__))
            temp_dir = os.path.join(current_dir, "temp_videos")
            
            if not os.path.exists(temp_dir):
                return {"message": "temp_videos directory not found", "success": False}
                
            files_removed = 0
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                        files_removed += 1
                        logger.info(f"Removed: {filename}")
                    except Exception as e:
                        logger.error(f"Error removing {filename}: {e}")
            
            # Create marker file
            try:
                marker_path = os.path.join(temp_dir, f"api_cleanup_{int(time.time())}.txt")
                with open(marker_path, "w") as f:
                    f.write(f"API cleanup performed at {datetime.now().isoformat()}")
            except:
                pass
                
            return {"message": f"Manual cleanup completed. Removed {files_removed} files.", "success": True}
    except Exception as e:
        logger.error(f"Error in cleanup endpoint: {e}")
        import traceback
        traceback.print_exc()
        return {"message": f"Error: {str(e)}", "success": False}

@app.post("/logout")
async def logout():
    """Endpoint to log a user out - useful for client-side token invalidation"""
    try:
        logger.info("Handling user logout request")
        # In a more robust implementation, we would track and invalidate tokens
        # For now, we'll just return a success message
        return {"message": "Logout successful"}
    except Exception as e:
        logger.error(f"Error in logout endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Password reset request and reset endpoints
@app.post("/request-password-reset")
async def request_password_reset(request: ResetPasswordRequest = Body(...)):
    try:
        # Sanitize email
        clean_email = str(request.email).strip().strip("'\"")
        logger.info(f"Password reset requested for: {clean_email}")
        
        # Check if user exists
        user_db = db_sys.load_user_database()
        if clean_email not in user_db:
            logger.info("User not found for password reset.")
            # Return success anyway for security (don't reveal if email exists)
            return {"message": "If your email is registered, you will receive a reset code"}
        
        # Generate reset code
        reset_code = email_sys.generate_verification_code()
        expiry = (datetime.utcnow() + timedelta(minutes=30)).timestamp()
        
        # Store reset code in user record
        user_db[clean_email]["reset_code"] = reset_code
        user_db[clean_email]["reset_code_expiry"] = expiry
        db_sys.save_user_database(user_db)
        
        # Send reset email
        try:
            logger.info(f"Sending password reset email to {clean_email} with code {reset_code}")
            email_sys.send_password_reset_email(clean_email, reset_code)
            logger.info(f"Password reset code sent successfully to: {clean_email}")
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to send password reset email"
            )
            
        return {"message": "If your email is registered, you will receive a reset code"}
    except Exception as e:
        logger.error(f"Error in request_password_reset: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset-password")
async def reset_password(request: PasswordReset = Body(...)):
    try:
        # Sanitize email
        clean_email = str(request.email).strip().strip("'\"")
        logger.info(f"Password reset for: {clean_email}")
        
        # Check if user exists
        user_db = db_sys.load_user_database()
        if clean_email not in user_db:
            logger.info("User not found for password reset.")
            raise HTTPException(status_code=404, detail="Invalid or expired reset code")
        
        user = user_db[clean_email]
        
        # Verify reset code
        stored_reset_code = user.get("reset_code")
        reset_code_expiry = user.get("reset_code_expiry", 0)
        
        # Check if reset code is valid and not expired
        current_time = datetime.utcnow().timestamp()
        if not stored_reset_code or stored_reset_code != request.reset_code or current_time > reset_code_expiry:
            logger.info("Invalid or expired reset code.")
            raise HTTPException(status_code=400, detail="Invalid or expired reset code")
        
        # Update password
        hashed_password = db_sys.get_password_hash(request.new_password)
        user_db[clean_email]["hashed_password"] = hashed_password
        
        # Clear reset code
        user_db[clean_email].pop("reset_code", None)
        user_db[clean_email].pop("reset_code_expiry", None)
        
        # Save updated user data
        db_sys.save_user_database(user_db)
        
        logger.info(f"Password reset successful for: {clean_email}")
        return {"message": "Password reset successful"}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in reset_password: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        dict: Status information about the API
    """
    return {
        "status": "ok",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": time.time() - app.state.start_time if hasattr(app.state, "start_time") else None
    }

# Add 404 error handler
@app.exception_handler(404)
async def custom_404_handler(request, exc):
    """Custom handler for 404 errors to provide a more helpful message"""
    path = request.url.path
    
    # Create a more detailed error response
    response = {
        "error": "Not Found",
        "message": f"The requested URL '{path}' was not found on this server.",
        "available_docs": [
            {"url": "/api/docs", "description": "Swagger UI API documentation"},
            {"url": "/api/redoc", "description": "ReDoc API documentation"},
            {"url": "/health", "description": "API health check endpoint"}
        ]
    }
    
    return JSONResponse(
        status_code=404,
        content=response
    )

# Add endpoint to get task progress
@app.get("/task-progress/{task_id}")
async def get_task_progress(task_id: str):
    """Get the progress of a long-running task."""
    with task_progress_lock:
        if task_id not in task_progress:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Calculate elapsed time
        elapsed = time.time() - task_progress[task_id]["start_time"]
        
        # Return progress information
        return {
            "task_id": task_id,
            "progress": task_progress[task_id]["progress"],
            "status": task_progress[task_id]["status"],
            "message": task_progress[task_id]["message"],
            "elapsed_seconds": elapsed
        }

if __name__ == "__main__":
    # Get port from environment variable or use default 8002
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8002"))
    
    # Check if specified port is available
    if not is_port_available(port):
        logger.warning(f"Port {port} is not available, trying to find an available port...")
        # Try to find an available port starting from 8003
        for try_port in range(8003, 8100):
            if is_port_available(try_port):
                logger.info(f"Found available port: {try_port}")
                port = try_port
                break
        else:
            logger.error("Could not find an available port. Exiting.")
            sys.exit(1)
    
    # Set the new port in environment variable for other components
    os.environ["PORT"] = str(port)
    logger.info(f"Starting server on {host}:{port}")
    
    # Run the server with uvicorn
    try:
        uvicorn.run(app, host=host, port=port)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1) 