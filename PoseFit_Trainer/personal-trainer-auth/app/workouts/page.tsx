"use client"

import { useEffect } from "react"
import { redirect } from "next/navigation"

export default function WorkoutsPage() {
  useEffect(() => {
    redirect("/workouts/exercises")
  }, [])

  return null
} 