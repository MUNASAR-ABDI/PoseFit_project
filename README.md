# PoseFit - AI-Powered Fitness Trainer

PoseFit is a full-stack web application that uses computer vision to provide real-time exercise tracking, form correction, and workout guidance. The system serves as a personal AI fitness coach that can monitor your workout form through your webcam.

## Features

- **Real-time Pose Detection**: Uses computer vision (MediaPipe) to detect and track body poses during workouts
- **Exercise Form Feedback**: Provides immediate feedback on exercise form
- **Workout Tracking**: Records workout history and performance metrics
- **Video Recording**: Saves workout videos for later review
- **User Authentication**: Secure login/registration with email verification
- **Responsive Design**: Works on desktop and mobile devices
- **Rate Limiting**: Protection against brute force attacks
- **Static File Caching**: Improved performance with optimized resource delivery
- **Dockerized Deployment**: Easy containerized deployment

## System Components

PoseFit consists of three main applications:

1. **PoseFit Landing Page** (port 4000): The main entry point with navigation to all PoseFit components
2. **PoseFit Trainer** (port 3000): Real-time workout trainer with pose detection and form correction
3. **PoseFit Assistant** (port 3001): AI-powered fitness coach providing personalized workout plans

## System Requirements

- **Python 3.8+** with the following packages:
  - FastAPI
  - MediaPipe
  - OpenCV
  - NumPy
  - Pydantic
  - PyJWT
  - Email-validator
  - Passlib
  - Python-jose
  - Uvicorn
  
- **Node.js 16+** with npm/yarn for the frontend

- **Docker & Docker Compose** (optional, for containerized deployment)

## Project Structure

The project is organized into three main components:

1. **Backend AI Trainer** (`PoseFit_Trainer/AI_PersonTrainer backend`): Python FastAPI server that handles pose detection, workout processing, and user data.

2. **Frontend Web Application** (`PoseFit_Trainer/personal-trainer-auth`): Next.js application that provides the user interface for interacting with the AI trainer.

3. **PoseFit Assistant** (`PoseFit_assistant`): Next.js + Convex application for AI-generated fitness plans.

4. **Landing Page** (`posefit-landing`): Simple landing page that links to all PoseFit components.

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd posefit
```

### 2. Set up environment variables

Each application component needs its own environment variables. We've provided templates in the `.env-templates` directory:

```bash
# For the PoseFit Trainer
cp .env-templates/trainer.env PoseFit_Trainer/personal-trainer-auth/.env.local

# For the PoseFit Assistant
cp .env-templates/assistant.env PoseFit_assistant/.env.local

# For the Landing Page
cp .env-templates/landing.env posefit-landing/.env.local
```

### 3. Set up the Backend

```bash
cd PoseFit_Trainer/AI_PersonTrainer\ backend
pip install -r requirements.txt

# Generate a secure secret key for production
python generate_key.py
```

### 4. Set up the Frontend Components

```bash
# Set up the PoseFit Trainer
cd ../personal-trainer-auth
npm install

# Set up the PoseFit Assistant
cd ../../PoseFit_assistant
npm install

# Set up the Landing Page
cd ../posefit-landing
npm install
```

## Running the Application

### Option 1: Using the startup scripts (recommended for development)

#### Windows
```
start-services.bat
```

#### macOS / Linux
```bash
chmod +x start-all.sh
./start-all.sh
```

### Option 2: Using Docker (recommended for production)

```bash
# Build and start the containers
docker-compose up -d

# View logs
docker-compose logs -f
```

### Option 3: Manual Startup

1. Start the backend server:
```bash
cd PoseFit_Trainer/AI_PersonTrainer\ backend
python api_server.py
```

2. In a new terminal, start the PoseFit Trainer:
```bash
cd PoseFit_Trainer/personal-trainer-auth
npm run dev
```

3. In a new terminal, start the Convex development server for PoseFit Assistant:
```bash
cd PoseFit_assistant
npx convex dev
```

4. In a new terminal, start the PoseFit Assistant:
```bash
cd PoseFit_assistant
npm run dev
```

5. In a new terminal, start the Landing Page:
```bash
cd posefit-landing
npm run dev
```

6. Open your browser and navigate to:
   - Landing Page: `http://localhost:4000`
   - PoseFit Trainer: `http://localhost:3000`
   - PoseFit Assistant: `http://localhost:3001`

## Configuration

### Environment Variables

The application uses environment variables for configuration:

#### Backend Environment Variables
Create a `.env` file in the `PoseFit_Trainer/AI_PersonTrainer backend` directory:

```bash
# Use the provided script to generate a secure key
python generate_key.py
```

Key backend environment variables:

- `SECRET_KEY`: JWT signing key (important for security!)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `HOST`: API server host
- `PORT`: API server port
- `FRAME_INTERVAL`: Time between video frames (controls FPS)
- `DOWNSCALE_FACTOR`: Video downscaling factor (1.0 = no scaling)

#### Frontend Environment Variables
See the `.env-templates` directory for templates for each application component. Key variables include:

- `NEXT_PUBLIC_LANDING_URL`: URL for the landing page (default: http://localhost:4000)
- `NEXT_PUBLIC_TRAINER_URL`: URL for the PoseFit Trainer (default: http://localhost:3000)
- `NEXT_PUBLIC_ASSISTANT_URL`: URL for the PoseFit Assistant (default: http://localhost:3001)
- `BACKEND_URL`: URL for the backend API (default: http://localhost:8002)

## API Documentation

The API documentation is available at:
- Swagger UI: `http://localhost:8002/api/docs`
- ReDoc: `http://localhost:8002/api/redoc`

## Performance Optimization

The application includes several performance optimizations:

- **Video Processing**: Adjustable framerate and resolution to reduce CPU usage
- **Static File Caching**: HTTP caching headers for optimal resource delivery
- **Rate Limiting**: Protection against abuse of authentication endpoints

## Usage

1. Start at the Landing Page (`http://localhost:4000`)
2. Navigate to the PoseFit Trainer or PoseFit Assistant
3. Create an account and log in
4. Follow the on-screen instructions for each component

## Troubleshooting

- **Camera access issues**: Ensure your browser has permission to access your webcam
- **Backend connection errors**: Verify the API server is running on port 8002
- **Exercise detection problems**: Make sure you're in a well-lit area with a clear view of your body
- **Docker issues**: Make sure ports 3000, 3001, 4000, and 8002 are available and Docker is running
- **Navigation issues**: If "Back to PoseFit" buttons don't work, check that the environment variables are set correctly

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Git Setup
This project is now under version control with Git. 