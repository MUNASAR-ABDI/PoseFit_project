"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Target, Trophy, Calendar, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { Badge } from "@/components/ui/badge"
import { toast } from "@/hooks/use-toast"

interface GoalData {
  primaryGoal: string
  workoutFrequency: string
  workoutDuration: number
  fitnessLevel: string
  weeklyTarget: number
  weeklyProgress: number
}

export function GoalsProgressCard() {
  const [loading, setLoading] = useState(true)
  const [goalData, setGoalData] = useState<GoalData | null>(null)
  
  useEffect(() => {
    async function fetchGoals() {
      try {
        setLoading(true)
        
        // Fetch profile data which includes goals
        const response = await fetch("/api/profile", {
          credentials: "include",
        })
        
        if (!response.ok) {
          throw new Error("Failed to fetch profile")
        }
        
        const data = await response.json()
        
        // Get weekly target based on frequency
        let weeklyTarget = 3 // Default to 3 workouts per week
        const frequencyMap: Record<string, number> = {
          "1-2": 2,
          "3-4": 4,
          "5-6": 6,
          "7+": 7
        }
        
        let workoutFrequency = "3-4" // Default
        if (data.goals?.weekly_workouts) {
          const weekly = data.goals.weekly_workouts
          if (weekly <= 2) workoutFrequency = "1-2"
          else if (weekly <= 4) workoutFrequency = "3-4"
          else if (weekly <= 6) workoutFrequency = "5-6"
          else workoutFrequency = "7+"
          
          weeklyTarget = frequencyMap[workoutFrequency] || 3
        }
        
        // Also fetch workout history to calculate weekly progress
        const historyResponse = await fetch("/api/workouts/history", {
          credentials: "include",
        })
        
        if (!historyResponse.ok) {
          throw new Error("Failed to fetch workout history")
        }
        
        const historyData = await historyResponse.json()
        const workouts = historyData.workouts || []
        
        // Calculate workouts this week
        const now = new Date()
        const startOfWeek = new Date(now)
        startOfWeek.setDate(now.getDate() - now.getDay()) // Sunday
        startOfWeek.setHours(0, 0, 0, 0)
        
        const weeklyProgress = workouts.filter((workout: unknown) => 
          new Date(workout.date || workout.timestamp) >= startOfWeek
        ).length
        
        // Map the fitness goal type to our UI values
        let primaryGoal = "general"
        if (data.goals?.fitness_goal_type) {
          // Map from backend values to form values
          const goalMap: Record<string, string> = {
            "weight_loss": "Weight Loss",
            "muscle_gain": "Muscle Gain",
            "strength_building": "Strength Building",
            "endurance": "Endurance",
            "general_fitness": "General Fitness"
          }
          primaryGoal = goalMap[data.goals.fitness_goal_type] || "General Fitness"
        }
        
        setGoalData({
          primaryGoal,
          workoutFrequency,
          workoutDuration: data.goals?.minutes_per_workout || 45,
          fitnessLevel: data.body_metrics?.fitness_level || "beginner",
          weeklyTarget,
          weeklyProgress
        })
      } catch (error) {
        console.error("Error fetching goals:", error)
        toast({
          title: "Error",
          description: "Failed to load goals data.",
          variant: "destructive",
        })
      } finally {
        setLoading(false)
      }
    }
    
    fetchGoals()
  }, [])
  
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5 text-blue-500" />
            <span className="h-6 w-32 animate-pulse bg-muted rounded"></span>
          </CardTitle>
          <CardDescription>
            <span className="h-4 w-48 animate-pulse bg-muted rounded"></span>
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="h-5 w-full animate-pulse bg-muted rounded"></div>
          <div className="h-20 w-full animate-pulse bg-muted rounded"></div>
        </CardContent>
      </Card>
    )
  }
  
  if (!goalData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5 text-blue-500" />
            Fitness Goals
          </CardTitle>
          <CardDescription>Set your goals to track progress</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center space-y-4 py-6">
          <AlertCircle className="h-12 w-12 text-muted-foreground" />
          <p className="text-center text-muted-foreground">No fitness goals set yet</p>
          <Button asChild>
            <Link href="/profile">Set Your Goals</Link>
          </Button>
        </CardContent>
      </Card>
    )
  }
  
  // Calculate progress percentage (capped at 100%)
  const progressPercentage = Math.min(
    Math.round((goalData.weeklyProgress / goalData.weeklyTarget) * 100),
    100
  )
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Target className="h-5 w-5 text-blue-500" />
          Fitness Goals
        </CardTitle>
        <CardDescription>Your progress this week</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <Badge variant="outline" className="px-3 py-1">
            <span className="font-medium">{goalData.primaryGoal}</span>
          </Badge>
          <div className="text-sm text-muted-foreground">
            {goalData.fitnessLevel.charAt(0).toUpperCase() + goalData.fitnessLevel.slice(1)} level
          </div>
        </div>
        
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="flex items-center gap-1">
              <Trophy className="h-4 w-4 text-amber-500" />
              Weekly Workouts
            </span>
            <span className="font-medium">
              {goalData.weeklyProgress}/{goalData.weeklyTarget}
            </span>
          </div>
          <Progress value={progressPercentage} className="h-2" />
        </div>
        
        <div className="pt-2 grid grid-cols-2 gap-4 text-sm">
          <div className="flex flex-col p-3 bg-muted/50 rounded-lg">
            <span className="text-muted-foreground">Duration</span>
            <span className="font-medium text-base flex items-center">
              <Calendar className="h-4 w-4 mr-1 text-indigo-400" />
              {goalData.workoutDuration} mins
            </span>
          </div>
          <div className="flex flex-col p-3 bg-muted/50 rounded-lg">
            <span className="text-muted-foreground">Frequency</span>
            <span className="font-medium text-base">
              {goalData.workoutFrequency.replace("-", "–")} × weekly
            </span>
          </div>
        </div>
        
        {progressPercentage >= 100 && (
          <div className="mt-2 p-3 bg-green-500/10 border border-green-500/20 rounded-lg text-center">
            <span className="font-medium text-green-500 flex items-center justify-center">
              <Trophy className="h-4 w-4 mr-1" />
              Weekly goal achieved!
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  )
} 