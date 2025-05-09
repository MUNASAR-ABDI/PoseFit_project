"use client"

import * as React from "react"
import { useState, useEffect, useRef } from "react"
import Image from "next/image"
import { 
  ChevronLeft, ChevronRight, Dumbbell, LineChart, 
  Camera, Award, Check, X, Brain, Zap, BarChart, Activity
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface TutorialStep {
  title: string
  description: string
  icon: React.ReactNode
  visualComponent: React.ReactNode
}

// Sample exercise data for chart visualization
const exerciseData = [
  { day: "Mon", minutes: 45 },
  { day: "Tue", minutes: 0 },
  { day: "Wed", minutes: 30 },
  { day: "Thu", minutes: 0 },
  { day: "Fri", minutes: 60 },
  { day: "Sat", minutes: 0 },
  { day: "Sun", minutes: 25 },
]

// Component for visualization #1: Activity chart
const ActivityChart = () => {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center">
      <div className="mb-4">
        <Activity className="h-12 w-12 text-yellow-300" />
      </div>
      <div className="w-full h-32 flex items-end justify-between px-4">
        {exerciseData.map((day, index) => (
          <div key={index} className="flex flex-col items-center">
            <div 
              className="w-8 bg-indigo-500 rounded-t-md transition-all duration-500" 
              style={{ 
                height: `${day.minutes * 1.5}px`,
                backgroundColor: day.minutes > 0 ? '#8547e9' : '#2d2040',
                border: day.minutes > 0 ? '1px solid rgba(255, 215, 0, 0.3)' : 'none',
              }}
            />
            <div className="text-xs text-gray-400 mt-1">{day.day}</div>
          </div>
        ))}
      </div>
      <div className="mt-4 text-yellow-300 font-bold">Weekly Activity</div>
    </div>
  )
}

// Component for visualization #2: Exercise animation
const ExerciseDemo = () => {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center">
      <div className="relative h-48 w-48 overflow-hidden rounded-xl border border-yellow-300/30">
        <div 
          className="absolute inset-0 animate-pulse-slow"
          style={{
            backgroundImage: `url('/videos/Bicep Curl.gif')`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            filter: 'brightness(1.2) contrast(1.1)',
          }}
        />
        <div className="absolute bottom-2 right-2 bg-purple-900/70 text-white text-xs px-2 py-1 rounded-md border border-yellow-300/20">
          Form: Excellent
        </div>
        <div className="absolute top-2 left-2 bg-yellow-500/80 text-xs px-2 py-1 rounded-md">
          Live Analysis
        </div>
      </div>
    </div>
  )
}

// Component for visualization #3: AI Analysis
const AIAnalysis = () => {
  const points = [
    { x: 30, y: 40 },
    { x: 60, y: 30 },
    { x: 70, y: 70 },
    { x: 100, y: 50 },
    { x: 120, y: 80 },
    { x: 140, y: 90 },
    { x: 160, y: 100 },
  ]
  
  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-gradient-radial from-purple-900/50 to-indigo-900/30">
      <div className="w-full h-48 relative">
        {/* AI pose tracking visualization */}
        <svg width="100%" height="100%" viewBox="0 0 200 150" className="absolute inset-0">
          <path
            d="M30,40 Q60,30 70,70 T120,80 T160,100"
            fill="none"
            stroke="#ffd700"
            strokeWidth="2"
            strokeDasharray="4 2"
            className="animate-dash"
          />
          
          {points.map((point, i) => (
            <circle
              key={i}
              cx={point.x}
              cy={point.y}
              r="4"
              fill="#7747dc"
              stroke="#ffd700"
              strokeWidth="1"
              className="animate-pulse"
              style={{ animationDelay: `${i * 0.1}s` }}
            />
          ))}
          
          <g className="animate-bounce-slow" style={{ transformOrigin: '100px 75px' }}>
            <circle cx="100" cy="30" r="15" fill="#7747dc" />
            <circle cx="80" cy="60" r="8" fill="#8547e9" />
            <circle cx="120" cy="60" r="8" fill="#8547e9" />
            <line x1="100" y1="30" x2="80" y2="60" stroke="#ffd700" strokeWidth="2" />
            <line x1="100" y1="30" x2="120" y2="60" stroke="#ffd700" strokeWidth="2" />
            <line x1="80" y1="60" x2="80" y2="100" stroke="#ffd700" strokeWidth="2" />
            <line x1="120" y1="60" x2="120" y2="100" stroke="#ffd700" strokeWidth="2" />
            <circle cx="80" cy="100" r="8" fill="#8547e9" />
            <circle cx="120" cy="100" r="8" fill="#8547e9" />
          </g>
        </svg>
        
        <div className="absolute bottom-2 right-2 bg-purple-900/70 text-white text-xs px-2 py-1 rounded-md border border-yellow-300/20">
          AI Tracking Active
        </div>
      </div>
      
      <div className="flex gap-2 mt-4">
        <div className="bg-purple-900/60 text-white text-xs px-3 py-1 rounded-full border border-yellow-300/30">
          Angle: 85°
        </div>
        <div className="bg-purple-900/60 text-white text-xs px-3 py-1 rounded-full border border-yellow-300/30">
          Depth: Good
        </div>
        <div className="bg-purple-900/60 text-white text-xs px-3 py-1 rounded-full border border-yellow-300/30">
          Balance: 94%
        </div>
      </div>
    </div>
  )
}

// Component for visualization #4: Achievements
const AchievementsDemo = () => {
  const achievements = [
    { name: "Early Bird", progress: 100 },
    { name: "Consistency King", progress: 100 },
    { name: "Half-Century", progress: 60 },
    { name: "Perfect Form", progress: 80 },
  ]
  
  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-4" 
      style={{
        backgroundImage: `url('/onboarding/achievements.jpg')`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundBlendMode: 'overlay',
        backgroundColor: 'rgba(42, 20, 71, 0.85)'
      }}>
      <div className="mb-4 flex items-center">
        <Award className="h-8 w-8 text-yellow-300 mr-2" />
        <h3 className="text-white text-lg font-bold">Achievements</h3>
      </div>
      
      <div className="w-full space-y-3 backdrop-blur-sm bg-purple-900/30 p-4 rounded-lg border border-yellow-300/20">
        {achievements.map((achievement, i) => (
          <div key={i} className="w-full">
            <div className="flex justify-between text-xs mb-1">
              <span className="text-gray-300">{achievement.name}</span>
              <span className="text-yellow-300">{achievement.progress}%</span>
            </div>
            <div className="h-2 w-full bg-gray-700 rounded-full overflow-hidden">
              <div 
                className="h-full rounded-full"
                style={{ 
                  width: `${achievement.progress}%`,
                  background: achievement.progress === 100 
                    ? 'linear-gradient(90deg, #ffd700, #ffecb3)' 
                    : 'linear-gradient(90deg, #6a26cd, #8547e9)'
                }}
              />
            </div>
          </div>
        ))}
      </div>
      <div className="mt-2 px-3 py-1 bg-yellow-500/80 text-black text-xs rounded-full font-semibold">
        Keep going to earn more achievements!
      </div>
    </div>
  )
}

// Component for visualization #5: Program Generator
const ProgramGenerator = () => {
  const programs = [
    { name: "Strength Training", difficulty: "Intermediate", duration: "45 min" },
    { name: "HIIT Cardio", difficulty: "Advanced", duration: "30 min" },
    { name: "Yoga Flow", difficulty: "Beginner", duration: "60 min" }
  ]
  
  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-4">
      <div className="mb-4">
        <Brain className="h-12 w-12 text-yellow-300" />
      </div>
      
      <div className="w-full space-y-3">
        {programs.map((program, i) => (
          <div 
            key={i} 
            className="w-full rounded-md p-2 border border-yellow-300/20 bg-purple-900/40 flex justify-between items-center"
          >
            <div>
              <div className="text-white text-sm font-medium">{program.name}</div>
              <div className="text-gray-300 text-xs">{program.difficulty}</div>
            </div>
            <div className="text-xs text-yellow-300">{program.duration}</div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 text-center">
        <div className="inline-block px-3 py-1 bg-gradient-to-r from-purple-700 to-purple-900 rounded-full text-white text-xs border border-yellow-300/30">
          AI-generated workouts
        </div>
      </div>
    </div>
  )
}

export function OnboardingTutorial({ onComplete }: { onComplete: () => void }) {
  const [currentStep, setCurrentStep] = useState(0)
  const [visible, setVisible] = useState(true)

  // Tutorial steps
  const steps: TutorialStep[] = [
    {
      title: "Welcome to PoseFit!",
      description: "Your AI-powered personal trainer that helps you achieve your fitness goals with real-time feedback and personalized workouts.",
      icon: <Dumbbell className="h-8 w-8 text-primary" />,
      visualComponent: <ExerciseDemo />
    },
    {
      title: "Real-time Feedback",
      description: "PoseFit uses your camera to analyze your form and provide instant feedback during workouts to help you perform exercises correctly.",
      icon: <Camera className="h-8 w-8 text-primary" />,
      visualComponent: <AIAnalysis />
    },
    {
      title: "AI Workout Generation",
      description: "Our AI creates personalized workout programs tailored to your goals, fitness level, and available equipment.",
      icon: <Brain className="h-8 w-8 text-primary" />,
      visualComponent: <ProgramGenerator />
    },
    {
      title: "Track Your Progress",
      description: "View detailed statistics and charts to monitor your progress over time and see how you're improving.",
      icon: <LineChart className="h-8 w-8 text-primary" />,
      visualComponent: <ActivityChart />
    },
    {
      title: "Earn Achievements",
      description: "Complete workouts and challenges to earn badges and track your fitness journey milestones.",
      icon: <Award className="h-8 w-8 text-primary" />,
      visualComponent: <AchievementsDemo />
    }
  ]

  // Handle navigation
  const goToNextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
    } else {
      handleComplete()
    }
  }

  const goToPrevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleComplete = () => {
    // Store in local storage that tutorial has been completed
    if (typeof window !== 'undefined') {
      localStorage.setItem('tutorial_completed', 'true')
    }
    setVisible(false)
    if (onComplete) onComplete()
  }

  const handleDismiss = () => {
    // Store in local storage that tutorial has been seen
    if (typeof window !== 'undefined') {
      localStorage.setItem('tutorial_completed', 'true')
    }
    setVisible(false)
    if (onComplete) onComplete()
  }

  // Check if the tutorial has already been completed
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const tutorialCompleted = localStorage.getItem('tutorial_completed')
      if (tutorialCompleted === 'true') {
        setVisible(false)
      }
    }
  }, [])

  if (!visible) return null

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card className="max-w-2xl w-full">
        <CardContent className="p-6">
          <div className="absolute top-2 right-2">
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={handleDismiss} 
              className="h-8 w-8 rounded-full"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          
          {/* Progress indicators */}
          <div className="flex justify-center mb-4">
            {steps.map((_, index) => (
              <div 
                key={index}
                className={cn(
                  "h-2 w-12 mx-1 rounded-full transition-colors",
                  index === currentStep ? "bg-primary" : "bg-muted"
                )}
              />
            ))}
          </div>
          
          {/* Current step content */}
          <div className="text-center mb-6">
            <div className="flex justify-center mb-4">
              {steps[currentStep].icon}
            </div>
            <h2 className="text-2xl font-bold mb-2">
              {steps[currentStep].title}
            </h2>
            <p className="text-muted-foreground">
              {steps[currentStep].description}
            </p>
          </div>
          
          {/* Visual display - real components from the app */}
          <div 
            className="mb-6 rounded-lg overflow-hidden h-64 flex items-center justify-center bg-gradient-to-br from-purple-800/40 to-indigo-900/40 border border-yellow-300/20"
          >
            {steps[currentStep].visualComponent}
            </div>
          
          {/* Navigation */}
          <div className="flex justify-between">
            <Button 
              variant="outline" 
              onClick={goToPrevStep}
              disabled={currentStep === 0}
            >
              <ChevronLeft className="mr-2 h-4 w-4" />
              Previous
            </Button>
            
            <Button onClick={goToNextStep}>
              {currentStep < steps.length - 1 ? (
                <>
                  Next
                  <ChevronRight className="ml-2 h-4 w-4" />
                </>
              ) : (
                <>
                  Get Started
                  <Check className="ml-2 h-4 w-4" />
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 

// Add these styles to your globals.css
// @keyframes dash {
//   to {
//     stroke-dashoffset: 24;
//   }
// }

// .animate-dash {
//   animation: dash 1.5s linear infinite;
// }

// @keyframes bounce-slow {
//   0%, 100% {
//     transform: translateY(0);
//   }
//   50% {
//     transform: translateY(5px);
//   }
// }

// .animate-bounce-slow {
//   animation: bounce-slow 3s ease-in-out infinite;
// }

// @keyframes pulse-slow {
//   0%, 100% {
//     opacity: 1;
//   }
//   50% {
//     opacity: 0.6;
//   }
// }

// .animate-pulse-slow {
//   animation: pulse-slow 2s ease-in-out infinite;
// } 