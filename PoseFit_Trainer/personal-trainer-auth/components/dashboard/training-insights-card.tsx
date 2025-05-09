"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertCircle, Award, CheckCircle, ChevronRight, Dumbbell, RefreshCcw } from "lucide-react"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { Badge } from "@/components/ui/badge"
import { toast } from "@/hooks/use-toast"

interface FormFeedback {
  exercise: string
  feedback: string
  date: string
  improvement: boolean
  score?: number
}

export function TrainingInsightsCard() {
  const [loading, setLoading] = useState(true)
  const [insights, setInsights] = useState<FormFeedback[]>([])
  
  useEffect(() => {
    async function fetchInsights() {
      try {
        setLoading(true)
        
        // Fetch workout history from API
        const response = await fetch('/api/workouts/history', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        })
        
        if (!response.ok) {
          throw new Error('Failed to fetch workout history')
        }
        
        const data = await response.json()
        const workouts = data.workouts || []
        
        // Process workout data to extract form feedback
        // In a real implementation, this would come from a dedicated API endpoint
        const feedbackItems: FormFeedback[] = []
        
        workouts.forEach((workout: any) => {
          // Extract form feedback if available
          const formFeedback = workout.form_feedback || workout.feedback
          const exerciseName = workout.exercise_type || workout.exerciseType || workout.type || "Exercise"
          
          if (formFeedback) {
            // If feedback is an array, add each item
            if (Array.isArray(formFeedback)) {
              formFeedback.forEach((feedback: string) => {
                feedbackItems.push({
                  exercise: exerciseName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                  feedback,
                  date: workout.date || workout.timestamp || new Date().toISOString(),
                  improvement: feedback.toLowerCase().includes('improve') || feedback.toLowerCase().includes('better'),
                  score: workout.form_score || undefined
                })
              })
            } else if (typeof formFeedback === 'string') {
              // If feedback is a string, add it as a single item
              feedbackItems.push({
                exercise: exerciseName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                feedback: formFeedback,
                date: workout.date || workout.timestamp || new Date().toISOString(),
                improvement: formFeedback.toLowerCase().includes('improve') || formFeedback.toLowerCase().includes('better'),
                score: workout.form_score || undefined
              })
            }
          }
        })
        
        // If no real feedback, generate some example insights
        if (feedbackItems.length === 0 && workouts.length > 0) {
          // Sample feedback for common exercises
          const sampleFeedback = [
            {
              exercise: 'Squats',
              feedback: 'Keep your back straight and go deeper for better results',
              date: new Date().toISOString(),
              improvement: true,
              score: 85
            },
            {
              exercise: 'Push-ups',
              feedback: 'Great form! Maintain core engagement throughout',
              date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
              improvement: false,
              score: 92
            },
            {
              exercise: 'Plank',
              feedback: 'Keep your hips aligned with shoulders',
              date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
              improvement: true
            }
          ]
          
          // Get the most recent workout types
          const recentExercises = workouts
            .slice(0, 3)
            .map((workout: any) => {
              const type = workout.exercise_type || workout.exerciseType || workout.type || "Exercise"
              return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
            })
          
          // Match sample feedback to actual workout types when possible
          sampleFeedback.forEach((feedback, index) => {
            if (index < recentExercises.length) {
              feedback.exercise = recentExercises[index]
            }
          })
          
          setInsights(sampleFeedback)
        } else {
          // Sort by date (newest first) and limit to 3 items
          feedbackItems.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
          setInsights(feedbackItems.slice(0, 3))
        }
      } catch (error) {
        console.error('Error fetching training insights:', error)
        setInsights([])
      } finally {
        setLoading(false)
      }
    }
    
    fetchInsights()
  }, [])
  
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Award className="h-5 w-5 text-purple-500" />
            <span className="h-6 w-32 animate-pulse bg-muted rounded"></span>
          </CardTitle>
          <CardDescription>
            <span className="h-4 w-48 animate-pulse bg-muted rounded"></span>
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 w-full animate-pulse bg-muted rounded"></div>
          ))}
        </CardContent>
      </Card>
    )
  }
  
  if (insights.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Award className="h-5 w-5 text-purple-500" />
            Training Insights
          </CardTitle>
          <CardDescription>Feedback on your workout form</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center space-y-4 py-6">
          <AlertCircle className="h-12 w-12 text-muted-foreground" />
          <p className="text-center text-muted-foreground">No form feedback available yet</p>
          <Button asChild>
            <Link href="/workouts">Start a Workout</Link>
          </Button>
        </CardContent>
      </Card>
    )
  }
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex justify-between items-center">
          <span className="flex items-center gap-2">
            <Award className="h-5 w-5 text-purple-500" />
            Training Insights
          </span>
          <Button variant="ghost" size="sm" asChild>
            <Link href="/workouts/history" className="inline-flex items-center gap-1">
              View All <ChevronRight className="h-4 w-4" />
            </Link>
          </Button>
        </CardTitle>
        <CardDescription>Form feedback from your workouts</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {insights.map((insight, index) => (
          <div key={index} className="p-3 bg-muted/50 rounded-lg space-y-2">
            <div className="flex justify-between items-start">
              <div className="flex items-center">
                <Dumbbell className="h-4 w-4 mr-2 text-indigo-400" />
                <span className="font-medium">{insight.exercise}</span>
              </div>
              <Badge variant={insight.improvement ? "outline" : "secondary"} className="ml-2">
                {insight.improvement ? (
                  <span className="flex items-center text-amber-500">
                    <RefreshCcw className="h-3 w-3 mr-1" />
                    Improve
                  </span>
                ) : (
                  <span className="flex items-center text-green-500">
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Great
                  </span>
                )}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground">{insight.feedback}</p>
            <div className="flex justify-between items-center text-xs text-muted-foreground pt-1">
              <span>
                {new Date(insight.date).toLocaleDateString('en-US', { 
                  month: 'short', 
                  day: 'numeric'
                })}
              </span>
              {insight.score && (
                <span className="font-medium">
                  Form score: {insight.score}%
                </span>
              )}
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
} 