"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"

interface Exercise {
  id: string
  name: string
  description: string
  icon: LucideIcon
  difficulty: string
  duration: string
  targetMuscles: string[]
  image: string
}

interface ExerciseCardProps {
  exercise: Exercise
  isSelected: boolean
  onSelect: (exerciseId: string) => void
}

export function ExerciseCard({ exercise, isSelected, onSelect }: ExerciseCardProps) {
  const { id, name, description, icon: Icon, difficulty, duration, targetMuscles, image } = exercise

  return (
    <Card
      className={cn(
        "overflow-hidden transition-all border-2",
        isSelected ? "border-primary glow" : "border-transparent",
      )}
    >
      <div className="relative h-48 w-full overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage: `url(${image})`,
            filter: "brightness(0.7)",
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
        <div className="absolute bottom-0 left-0 p-4 w-full">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="bg-primary/20 backdrop-blur-sm p-2 rounded-full">
                <Icon className="h-5 w-5 text-primary" />
              </div>
              <h3 className="text-xl font-bold text-white text-glow">{name}</h3>
            </div>
            <Badge
              variant={difficulty === "Easy" ? "outline" : difficulty === "Moderate" ? "secondary" : "default"}
              className="bg-black/50 backdrop-blur-sm"
            >
              {difficulty}
            </Badge>
          </div>
        </div>
      </div>
      <CardContent className="pt-4">
        <p className="text-muted-foreground mb-4">{description}</p>
        <div className="flex flex-wrap gap-2 mb-2">
          {targetMuscles.map((muscle) => (
            <Badge key={muscle} variant="outline" className="bg-secondary/50">
              {muscle}
            </Badge>
          ))}
        </div>
        <p className="text-sm text-muted-foreground">Duration: {duration}</p>
      </CardContent>
      <CardFooter className="border-t bg-card p-4">
        <Button className="w-full bg-accent-gradient hover:opacity-90" onClick={() => onSelect(id)}>
          {isSelected ? "Selected" : "Select Exercise"}
        </Button>
      </CardFooter>
    </Card>
  )
}
