"use client"

import { useRouter, useSearchParams } from 'next/navigation'
import { useState, useEffect } from &apos;react&apos;
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { ArrowLeft, Flame, Timer } from 'lucide-react'

interface WorkoutStats {
  calories: number
  duration: number
  videoUrl: string
}

export default function ReviewPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const [stats, setStats] = useState<WorkoutStats>({
    calories: 0,
    duration: 0,
    videoUrl: ''
  })

  useEffect(() => {
    const calories = Number(searchParams.get(&apos;calories&apos;)) || 0
    const duration = Number(searchParams.get(&apos;duration&apos;)) || 0
    const videoPath = searchParams.get(&apos;video&apos;) || ''

    setStats({
      calories,
      duration,
      videoUrl: `${process.env.NEXT_PUBLIC_API_URL}/${videoPath}`
    })
  }, [searchParams])

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, &apos;0&apos;)}`
  }

  const handleBack = () => {
    router.push('/workouts')
  }

  return (
    <div className="container mx-auto p-4">
      <div className="flex flex-col space-y-4">
        <div className="flex items-center justify-between">
          <Button variant="ghost" onClick={handleBack}>
            <ArrowLeft className="mr-2" />
            Back
          </Button>
        </div>

        <h1 className="text-2xl font-bold text-center">Workout Complete!</h1>

        <Card>
          <CardContent className="p-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center justify-center space-x-2">
                <Flame className="text-red-500" />
                <div>
                  <p className="text-sm text-gray-500">Calories Burned</p>
                  <p className="text-xl font-bold">{stats.calories.toFixed(1)} kcal</p>
                </div>
              </div>
              <div className="flex items-center justify-center space-x-2">
                <Timer className="text-blue-500" />
                <div>
                  <p className="text-sm text-gray-500">Duration</p>
                  <p className="text-xl font-bold">{formatDuration(stats.duration)}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <h2 className="text-xl font-semibold mb-4">Workout Recording</h2>
            <video
              src={stats.videoUrl}
              controls
              className="w-full rounded-lg"
              poster="/workout-thumbnail.jpg"
            />
          </CardContent>
        </Card>

        <div className="flex justify-center">
          <Button onClick={handleBack} size="lg">
            Return to Workouts
          </Button>
        </div>
      </div>
    </div>
  )
}
