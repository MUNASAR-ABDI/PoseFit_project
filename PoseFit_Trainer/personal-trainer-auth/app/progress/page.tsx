'use client';

import { Suspense, useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { BarChart, LineChart, PieChart } from "lucide-react";

interface WorkoutHistory {
  id: string;
  date: string;
  exercise: string;
  duration: number;
  sets: number;
  reps: number;
  calories: number;
}

function ProgressCharts() {
  const [workoutHistory, setWorkoutHistory] = useState<WorkoutHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchWorkoutHistory() {
      try {
        const response = await fetch('/api/workout/metrics');
        if (!response.ok) {
          throw new Error('Failed to fetch workout history');
        }
        const data = await response.json();
        setWorkoutHistory(data.workouts || []);
      } catch (err) {
        console.error('Error fetching workout history:', err);
        setError('Failed to load workout data. Please try again later.');
        // Use sample data in case of error
        setWorkoutHistory([
          { id: '1', date: '2023-10-01', exercise: 'Bicep Curls', duration: 30, sets: 3, reps: 12, calories: 150 },
          { id: '2', date: '2023-10-03', exercise: 'Push Ups', duration: 25, sets: 3, reps: 15, calories: 120 },
          { id: '3', date: '2023-10-05', exercise: 'Squats', duration: 35, sets: 4, reps: 12, calories: 200 },
          { id: '4', date: '2023-10-08', exercise: 'Mountain Climbers', duration: 20, sets: 3, reps: 20, calories: 180 },
          { id: '5', date: '2023-10-10', exercise: 'Bicep Curls', duration: 32, sets: 3, reps: 12, calories: 155 },
        ]);
      } finally {
        setLoading(false);
      }
    }

    fetchWorkoutHistory();
  }, []);

  // Calculate monthly workout stats
  const monthlyStats = workoutHistory.reduce((acc, workout) => {
    const month = new Date(workout.date).getMonth();
    const monthName = new Date(workout.date).toLocaleString('default', { month: 'short' });
    
    if (!acc[monthName]) {
      acc[monthName] = {
        workouts: 0,
        totalDuration: 0,
        totalCalories: 0
      };
    }
    
    acc[monthName].workouts += 1;
    acc[monthName].totalDuration += workout.duration;
    acc[monthName].totalCalories += workout.calories;
    
    return acc;
  }, {} as Record<string, { workouts: number, totalDuration: number, totalCalories: number }>);

  // Transform data for charts
  const monthNames = Object.keys(monthlyStats);
  const workoutCounts = monthNames.map(month => monthlyStats[month].workouts);
  const durations = monthNames.map(month => monthlyStats[month].totalDuration);
  const calories = monthNames.map(month => monthlyStats[month].totalCalories);

  // Exercise distribution
  const exerciseStats = workoutHistory.reduce((acc, workout) => {
    if (!acc[workout.exercise]) {
      acc[workout.exercise] = 0;
    }
    acc[workout.exercise] += 1;
    return acc;
  }, {} as Record<string, number>);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-center">
        <p className="text-red-500">{error}</p>
        <Button onClick={() => window.location.reload()} className="mt-4">
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="container py-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Progress Charts</h1>
          <p className="text-muted-foreground">Visualize your fitness journey with detailed charts and statistics.</p>
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="duration">Duration</TabsTrigger>
          <TabsTrigger value="calories">Calories</TabsTrigger>
          <TabsTrigger value="exercises">Exercises</TabsTrigger>
        </TabsList>
        
        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Workout Frequency</CardTitle>
              <CardDescription>Number of workouts completed each month</CardDescription>
            </CardHeader>
            <CardContent className="h-80 flex items-center justify-center">
              <div className="w-full h-full flex flex-col items-center justify-center">
                <BarChart className="h-40 w-40 text-muted-foreground mb-4" />
                <div className="w-full flex items-end justify-around h-32 gap-2">
                  {monthNames.map((month, i) => (
                    <div key={i} className="flex flex-col items-center">
                      <div className="flex-1 w-10 bg-primary rounded-t-md" 
                           style={{ height: `${workoutCounts[i] * 20}px` }}></div>
                      <span className="text-xs mt-1">{month}</span>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
          
          <div className="grid md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Workout Time</CardTitle>
                <CardDescription>Total minutes spent per month</CardDescription>
              </CardHeader>
              <CardContent className="h-60">
                <div className="w-full h-full flex items-center justify-center">
                  <LineChart className="h-40 w-40 text-muted-foreground" />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Calories Burned</CardTitle>
                <CardDescription>Estimated calories burned per month</CardDescription>
              </CardHeader>
              <CardContent className="h-60">
                <div className="w-full h-full flex items-center justify-center">
                  <LineChart className="h-40 w-40 text-muted-foreground" />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        
        <TabsContent value="duration">
          <Card>
            <CardHeader>
              <CardTitle>Workout Duration</CardTitle>
              <CardDescription>Total minutes spent working out each month</CardDescription>
            </CardHeader>
            <CardContent className="h-96 flex items-center justify-center">
              <div className="w-full h-full flex flex-col items-center justify-center">
                <LineChart className="h-40 w-40 text-muted-foreground mb-4" />
                <div className="w-full flex items-end justify-around h-40 gap-2">
                  {monthNames.map((month, i) => (
                    <div key={i} className="flex flex-col items-center">
                      <div className="flex-1 w-10 bg-primary rounded-t-md" 
                           style={{ height: `${durations[i] / 5}px` }}></div>
                      <span className="text-xs mt-1">{month}</span>
                      <span className="text-xs font-medium">{durations[i]} min</span>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="calories">
          <Card>
            <CardHeader>
              <CardTitle>Calories Burned</CardTitle>
              <CardDescription>Estimated calories burned each month</CardDescription>
            </CardHeader>
            <CardContent className="h-96 flex items-center justify-center">
              <div className="w-full h-full flex flex-col items-center justify-center">
                <LineChart className="h-40 w-40 text-muted-foreground mb-4" />
                <div className="w-full flex items-end justify-around h-40 gap-2">
                  {monthNames.map((month, i) => (
                    <div key={i} className="flex flex-col items-center">
                      <div className="flex-1 w-10 bg-primary rounded-t-md" 
                           style={{ height: `${calories[i] / 10}px` }}></div>
                      <span className="text-xs mt-1">{month}</span>
                      <span className="text-xs font-medium">{calories[i]} cal</span>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="exercises">
          <Card>
            <CardHeader>
              <CardTitle>Exercise Distribution</CardTitle>
              <CardDescription>Breakdown of your most frequent exercises</CardDescription>
            </CardHeader>
            <CardContent className="h-96 flex items-center justify-center">
              <div className="w-full h-full flex flex-col items-center justify-center">
                <PieChart className="h-40 w-40 text-muted-foreground mb-4" />
                <div className="grid grid-cols-2 gap-4 w-full max-w-md">
                  {Object.entries(exerciseStats).map(([exercise, count], i) => (
                    <div key={i} className="flex items-center gap-2">
                      <div className="w-4 h-4 rounded-full" 
                           style={{ backgroundColor: `hsl(${i * 60}, 70%, 60%)` }}></div>
                      <span className="text-sm">{exercise}: {count} sessions</span>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default function ProgressPage() {
  return (
    <Suspense fallback={
      <div className="container py-8">
        <div className="animate-pulse bg-muted h-6 w-48 mb-2"></div>
        <div className="animate-pulse bg-muted h-4 w-96 mb-8"></div>
        <div className="animate-pulse bg-muted h-80 w-full rounded-md"></div>
      </div>
    }>
      <ProgressCharts />
    </Suspense>
  );
} 