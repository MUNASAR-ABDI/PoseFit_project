"use client"

import { useRouter, useSearchParams } from 'next/navigation';
import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Slider } from "@/components/ui/slider"
import { ArrowLeft, Camera, Settings } from "lucide-react"
import { Exercise } from '@/types/exercise'

// Add a mapping from exercise id to video or gif file
const exerciseMedia: Record<string, string> = {
  'bicep-curls': '/videos/Bicep Curl.gif',
  'warm-up': '/videos/Jumping Jack ( Warm up ).gif',
  'mountain-climbers': '/videos/Mountain Climber.mp4',
  'push-ups': '/videos/Push up.mp4',
  'squats': '/videos/Squat.mp4',
};

export default function ConfigureWorkout() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [exercise, setExercise] = useState<Exercise | null>(null)
  const [sets, setSets] = useState(3)
  const [reps, setReps] = useState(10)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const exerciseId = searchParams.get('exercise') || "bicep-curls"

  useEffect(() => {
    // Get the selected exercise from sessionStorage
    const selectedExerciseStr = sessionStorage.getItem("selectedExercise")
    if (!selectedExerciseStr) {
      router.push("/workouts/exercises")
      return
    }

    try {
      const selectedExercise = JSON.parse(selectedExerciseStr)
      setExercise(selectedExercise)
    } catch (error) {
      console.error("Error parsing exercise data:", error)
      router.push("/workouts/exercises")
    }
  }, [router])

  const startWorkout = async () => {
    // Use the backend method name for the exercise
    if (!exercise) return;
    const backendExercise = exercise.exercise || exerciseId;
    window.location.href = `/workout?exercise=${backendExercise}&sets=${sets}&reps=${reps}`;
  }

  const handleBack = () => {
    router.push("/workouts/exercises")
  }

  if (!exercise) {
    return <div className="container py-8">Loading...</div>
  }

  // Debug: log the exercise id to check mapping
  console.log('Exercise ID:', exercise.id);

  return (
    <div className="container py-8">
      <div className="mb-8 flex items-center">
        <Button variant="ghost" size="icon" onClick={handleBack} className="mr-4">
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-glow">{exercise.name}</h1>
          <p className="text-muted-foreground">Configure your workout parameters</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="relative h-[400px] rounded-2xl overflow-hidden flex items-center justify-center bg-black">
          {exerciseMedia[exercise.id] ? (
            exerciseMedia[exercise.id].endsWith('.mp4') ? (
              <video
                src={exerciseMedia[exercise.id]}
                className="object-cover w-full h-full"
                autoPlay
                loop
                muted
                playsInline
              />
            ) : (
              <img
                src={exerciseMedia[exercise.id]}
                alt={exercise.name}
                className="object-cover w-full h-full"
              />
            )
          ) : (
            <div className="flex flex-col items-center justify-center w-full h-full text-white">
              <div className="text-lg font-bold mb-2">No video or image found for this exercise.</div>
              <div className="text-sm">Exercise ID: {exercise.id}</div>
            </div>
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
          <div className="absolute bottom-0 left-0 p-6 w-full">
            <h2 className="text-2xl font-bold text-white mb-2">{exercise.name}</h2>
            <p className="text-white/80">{exercise.description}</p>
          </div>
        </div>

        <Card className="border-2 border-primary/20 bg-card-gradient">
          <CardHeader>
            <div className="flex items-center gap-2 mb-2">
              <div className="bg-primary/20 p-2 rounded-full">
                <Settings className="h-5 w-5 text-primary" />
              </div>
              <CardTitle>Workout Parameters</CardTitle>
            </div>
            <CardDescription>Customize your workout intensity by adjusting sets and repetitions</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
                <span className="block sm:inline">{error}</span>
              </div>
            )}
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <Label htmlFor="sets" className="text-lg">
                  Number of Sets: <span className="text-primary font-bold">{sets}</span>
                </Label>
                <span className="text-sm text-muted-foreground">(1-5)</span>
              </div>
              <Slider
                id="sets"
                min={1}
                max={5}
                step={1}
                defaultValue={[sets]}
                onValueChange={(value) => setSets(value[0])}
                className="py-4"
              />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <Label htmlFor="reps" className="text-lg">
                  Repetitions per Set: <span className="text-primary font-bold">{reps}</span>
                </Label>
                <span className="text-sm text-muted-foreground">(5-20)</span>
              </div>
              <Slider
                id="reps"
                min={5}
                max={20}
                step={1}
                defaultValue={[reps]}
                onValueChange={(value) => setReps(value[0])}
                className="py-4"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="custom-reps">Or enter custom repetitions:</Label>
              <Input
                id="custom-reps"
                type="number"
                min={1}
                value={reps}
                onChange={(e) => setReps(Number.parseInt(e.target.value) || 10)}
                className="bg-background/50 border-primary/30"
              />
            </div>

            <div className="bg-primary/10 p-4 rounded-lg border border-primary/20">
              <h3 className="font-medium mb-2">Workout Summary</h3>
              <p className="text-muted-foreground">
                You will perform <span className="text-primary font-medium">{sets} sets</span> of{" "}
                <span className="text-primary font-medium">{exercise.name}</span> with{" "}
                <span className="text-primary font-medium">{reps} repetitions</span> per set.
              </p>
              <p className="text-muted-foreground mt-2">
                Total: <span className="text-primary font-medium">{sets * reps} repetitions</span>
              </p>
            </div>
          </CardContent>
          <CardFooter>
            <Button
              className="w-full bg-accent-gradient hover:opacity-90 text-lg py-6"
              onClick={startWorkout}
              disabled={isLoading}
            >
              {isLoading ? (
                "Starting workout..."
              ) : (
                <>
                  <Camera className="mr-2 h-5 w-5" />
                  Start Workout with Camera
                </>
              )}
            </Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}
