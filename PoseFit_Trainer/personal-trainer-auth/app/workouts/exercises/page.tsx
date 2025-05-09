import { ExerciseList } from "@/components/workouts/exercise-list"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Dumbbell } from "lucide-react"

export default function ExercisesPage() {
  return (
    <div className="container py-8">
      <div className="mb-8 text-center">
        <div className="flex justify-center mb-4">
          <div className="bg-primary/20 p-3 rounded-full">
            <Dumbbell className="h-8 w-8 text-primary" />
          </div>
        </div>
        <h1 className="text-4xl font-bold tracking-tight text-glow">Choose Your Exercise</h1>
        <p className="text-muted-foreground mt-2 max-w-2xl mx-auto">
          Select an exercise to begin your workout. Our AI trainer will guide you through proper form and technique.
        </p>
      </div>

      <Card className="border-2 border-primary/20 bg-card-gradient">
        <CardHeader>
          <CardTitle className="text-2xl">Available Exercises</CardTitle>
          <CardDescription>
            Choose from the following exercises. Each one is designed to target specific muscle groups.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ExerciseList />
        </CardContent>
      </Card>
    </div>
  )
}
