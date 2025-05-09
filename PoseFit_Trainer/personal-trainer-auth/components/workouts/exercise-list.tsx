"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { ExerciseCard } from "@/components/workouts/exercise-card"
import { Flame, ArrowDown, Mountain, HandIcon as Arm, MoveUp } from "lucide-react"

const exercises = [
  {
    id: "warm-up",
    name: "Warm Up",
    description: "Prepare your body for exercise with dynamic stretching and light movements",
    icon: Flame,
    difficulty: "Easy",
    duration: "5-10 min",
    targetMuscles: ["Full body"],
    image: "https://placehold.co/600x400/png?text=Warm+Up",
    backendName: "warmup",
  },
  {
    id: "squats",
    name: "Squats",
    description: "A compound exercise that targets your lower body and core",
    icon: ArrowDown,
    difficulty: "Moderate",
    duration: "Varies",
    targetMuscles: ["Quadriceps", "Hamstrings", "Glutes", "Core"],
    image: "https://placehold.co/600x400/png?text=Squats",
    backendName: "squats",
  },
  {
    id: "mountain-climbers",
    name: "Mountain Climbers",
    description: "A dynamic full-body exercise that elevates your heart rate",
    icon: Mountain,
    difficulty: "Moderate",
    duration: "Varies",
    targetMuscles: ["Core", "Shoulders", "Chest", "Hip flexors"],
    image: "https://placehold.co/600x400/png?text=Mountain+Climbers",
    backendName: "mountain_climbers",
  },
  {
    id: "bicep-curls",
    name: "Bicep Curls",
    description: "An isolation exercise that targets your biceps",
    icon: Arm,
    difficulty: "Easy",
    duration: "Varies",
    targetMuscles: ["Biceps", "Forearms"],
    image: "https://placehold.co/600x400/png?text=Bicep+Curls",
    backendName: "bicep_curls",
  },
  {
    id: "push-ups",
    name: "Push Ups",
    description: "A compound exercise that targets your upper body and core",
    icon: MoveUp,
    difficulty: "Moderate to Hard",
    duration: "Varies",
    targetMuscles: ["Chest", "Shoulders", "Triceps", "Core"],
    image: "https://placehold.co/600x400/png?text=Push+Ups",
    backendName: "push_ups",
  },
]

export function ExerciseList() {
  const router = useRouter()
  const [selectedExercise, setSelectedExercise] = useState<string | null>(null)

  const handleSelectExercise = (exerciseId: string) => {
    const exercise = exercises.find(e => e.id === exerciseId);
    if (!exercise) return;

    setSelectedExercise(exerciseId)

    // Store the backend method name in sessionStorage for use in workout
    sessionStorage.setItem("selectedExercise", JSON.stringify({
      ...exercise,
      exercise: exercise.backendName
    }))

    // Navigate to the configure page
    router.push("/workouts/configure")
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {exercises.map((exercise) => (
        <ExerciseCard
          key={exercise.id}
          exercise={exercise}
          isSelected={selectedExercise === exercise.id}
          onSelect={handleSelectExercise}
        />
      ))}
    </div>
  )
}
