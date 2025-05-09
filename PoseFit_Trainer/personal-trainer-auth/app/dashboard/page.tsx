"use client"

import { useEffect, useState } from "react"
import { Skeleton } from "@/components/ui/skeleton-loader"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell
} from 'recharts'
import { 
  Award, Calendar, Clock, Dumbbell, Flame, 
  TrendingUp, Activity, Target, ChevronRight
} from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { OnboardingTutorial } from "@/components/onboarding/tutorial"

// Types
interface WorkoutSummary {
  id: string
  date: string
  type: string
  duration: number
  calories: number
  completed: boolean
}

interface UserStreak {
  current: number
  best: number
  lastWorkout: string
}

interface Achievement {
  id: string
  name: string
  description: string
  criteria?: string
  icon?: string
  category?: string
  xp?: number
  progress: number
  earned: boolean
  earnedDate?: string | null
}

interface UserStats {
  totalWorkouts: number
  thisWeek: number
  totalMinutes: number
  streaks: UserStreak
  workouts: WorkoutSummary[]
  progressByExercise: { name: string; count: number }[]
  weeklyActivity: { day: string; minutes: number }[]
  achievements: Achievement[]
}

// Utility functions to process workout data
const processWorkoutHistory = (workoutHistory: any[]) => {
  if (!workoutHistory || !Array.isArray(workoutHistory)) {
    return [];
  }
  
  // Convert workout history to WorkoutSummary format
  return workoutHistory.map((workout, index) => {
    // Handle different workout data formats
    const date = workout.date || workout.timestamp || new Date().toISOString();
    const type = workout.exercise_type || workout.exerciseType || workout.type || "Unknown";
    const duration = workout.time_elapsed || workout.duration || 0;
    const calories = workout.calories || workout.caloriesBurned || Math.round(duration * 0.05);
    
    return {
      id: workout.session_id || workout.id || `workout-${index}`,
      date: date,
      type: type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      duration: duration,
      calories: calories,
      completed: workout.sets_completed === workout.total_sets || workout.completed || false
    };
  }).sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
};

const calculateWorkoutStats = (workouts: WorkoutSummary[]) => {
  // Calculate total workouts
  const totalWorkouts = workouts.length;
  
  // Calculate total minutes
  const totalMinutes = workouts.reduce((total, workout) => total + workout.duration, 0);
  
  // Calculate workouts this week
  const now = new Date();
  const startOfWeek = new Date(now);
  startOfWeek.setDate(now.getDate() - now.getDay()); // Sunday
  startOfWeek.setHours(0, 0, 0, 0);
  
  const thisWeek = workouts.filter(workout => 
    new Date(workout.date) >= startOfWeek
  ).length;
  
  // Calculate streaks
  let current = 0;
  let best = 0;
  let lastWorkoutDayDiff = -1;
  
  if (workouts.length > 0) {
    // Calculate days since last workout
    const lastWorkoutDate = new Date(workouts[0].date);
    const diffTime = Math.abs(now.getTime() - lastWorkoutDate.getTime());
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    lastWorkoutDayDiff = diffDays;
    
    // Get unique workout dates
    const workoutDates = [...new Set(workouts.map(workout => 
      new Date(workout.date).toDateString()
    ))];
    
    // Sort dates in descending order
    workoutDates.sort((a, b) => new Date(b).getTime() - new Date(a).getTime());
    
    // Calculate current streak
    let streakCount = 0;
    for (let i = 0; i < workoutDates.length; i++) {
      const currentDate = new Date(workoutDates[i]);
      
      if (i === 0) {
        streakCount = 1;
      } else {
        const prevDate = new Date(workoutDates[i-1]);
        const dayDiff = Math.floor((prevDate.getTime() - currentDate.getTime()) / (1000 * 60 * 60 * 24));
        
        if (dayDiff === 1) {
          streakCount++;
        } else {
          break;
        }
      }
    }
    
    current = streakCount;
    best = Math.max(current, 1); // At least 1 if there's any workout
  }
  
  // Format last workout text
  let lastWorkoutText = "Never";
  if (lastWorkoutDayDiff === 0) {
    lastWorkoutText = "Today";
  } else if (lastWorkoutDayDiff === 1) {
    lastWorkoutText = "Yesterday";
  } else if (lastWorkoutDayDiff > 0) {
    lastWorkoutText = `${lastWorkoutDayDiff} days ago`;
  }
  
  const streaks = {
    current,
    best,
    lastWorkout: lastWorkoutText
  };
  
  return { totalWorkouts, totalMinutes, thisWeek, streaks };
};

const calculateExerciseDistribution = (workouts: WorkoutSummary[]) => {
  // Count exercises by type
  const exerciseCounts: Record<string, number> = {};
  
  workouts.forEach(workout => {
    const type = workout.type;
    exerciseCounts[type] = (exerciseCounts[type] || 0) + 1;
  });
  
  // Convert to array format for chart
  return Object.entries(exerciseCounts).map(([name, count]) => ({
    name,
    count
  })).sort((a, b) => b.count - a.count);
};

const calculateWeeklyActivity = (workouts: WorkoutSummary[]) => {
  // Initialize empty activity data for each day
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const weeklyActivity = days.map(day => ({ day, minutes: 0 }));
  
  // Get today's day index (0 = Sunday in JS)
  const today = new Date().getDay();
  
  // Get the start date of the current week (Sunday)
  const startOfWeek = new Date();
  startOfWeek.setDate(startOfWeek.getDate() - today);
  startOfWeek.setHours(0, 0, 0, 0);
  
  // Fill in activity data
  workouts.forEach(workout => {
    const workoutDate = new Date(workout.date);
    
    // Only include workouts from this week
    if (workoutDate >= startOfWeek) {
      // Convert day of week (0-6, where 0 is Sunday) to our array index
      // We use Mon-Sun format, so convert Sunday (0) to index 6, and others (1-6) to (0-5)
      const dayIndex = workoutDate.getDay() === 0 ? 6 : workoutDate.getDay() - 1;
      
      // Add workout duration to the appropriate day
      weeklyActivity[dayIndex].minutes += workout.duration;
    }
  });
  
  return weeklyActivity;
};

// Default achievements that exist
const DEFAULT_ACHIEVEMENTS = [
  { id: "1", name: "Early Bird", description: "Complete 5 workouts before 8 AM", earned: false },
  { id: "2", name: "Consistency King", description: "Work out 3 days in a row", earned: false },
  { id: "3", name: "Half-Century", description: "Complete 50 total exercises", earned: false },
  { id: "4", name: "Perfect Form", description: "Get 95% form accuracy in a workout", earned: false },
];

export default function DashboardPage() {
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<UserStats | null>(null)
  const [showTutorial, setShowTutorial] = useState(false)
  
  // Fetch user stats
  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        
        // Fetch workout history from API
        const response = await fetch('/api/workouts/history', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch workout history');
        }
        
        const data = await response.json();
        const workouts = processWorkoutHistory(data.workouts || []);
        
        // Calculate statistics from workouts
        const { totalWorkouts, totalMinutes, thisWeek, streaks } = calculateWorkoutStats(workouts);
        const progressByExercise = calculateExerciseDistribution(workouts);
        const weeklyActivity = calculateWeeklyActivity(workouts);
        
        // Set stats state
        setStats({
          totalWorkouts,
          thisWeek,
          totalMinutes,
          streaks,
          workouts: workouts.slice(0, 5), // Only show first 5 workouts
          progressByExercise,
          weeklyActivity,
          achievements: [] // Empty achievements array
        });
        
        setLoading(false);
        
        // Show tutorial for first-time users
        if (totalWorkouts === 0) {
          setShowTutorial(true);
        }
      } catch (error) {
        console.error('Error fetching workout stats:', error);
        setLoading(false);
      }
    };
    
    fetchStats();
  }, []);
  
  if (loading) {
    return <DashboardSkeleton />;
  }
  
  return (
    <div className="container mx-auto p-4 space-y-6">
      {showTutorial && (
        <OnboardingTutorial onClose={() => setShowTutorial(false)} />
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Workouts"
          value={stats?.totalWorkouts?.toString() || "0"}
          description="All-time workout sessions"
          icon={<Dumbbell className="h-6 w-6 text-indigo-400" />}
        />
        <StatCard
          title="This Week"
          value={stats?.thisWeek?.toString() || "0"}
          description="Workouts this week"
          icon={<Calendar className="h-6 w-6 text-green-400" />}
        />
        <StatCard
          title="Minutes"
          value={stats?.totalMinutes?.toString() || "0"}
          description="Total workout time"
          icon={<Clock className="h-6 w-6 text-amber-400" />}
        />
        <StatCard
          title="Current Streak"
          value={stats?.streaks?.current?.toString() || "0"}
          description={`Last workout: ${stats?.streaks?.lastWorkout || "Never"}`}
          icon={<Flame className="h-6 w-6 text-red-400" />}
          footer={`Best streak: ${stats?.streaks?.best || 0} days`}
        />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weekly Activity Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-blue-500" />
              Weekly Activity
            </CardTitle>
            <CardDescription>Your daily workout minutes this week</CardDescription>
          </CardHeader>
          <CardContent className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats?.weeklyActivity || []}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                <XAxis dataKey="day" />
                <YAxis name="Minutes" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }}
                  labelStyle={{ color: 'white' }}
                  formatter={(value) => [`${value} mins`, 'Duration']}
                />
                <Bar dataKey="minutes" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        
        {/* Exercise Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5 text-rose-500" />
              Exercise Focus
            </CardTitle>
            <CardDescription>Distribution of workout types</CardDescription>
          </CardHeader>
          <CardContent className="h-80">
            {stats?.progressByExercise && stats.progressByExercise.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={stats.progressByExercise}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {stats.progressByExercise.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={[
                        '#6366f1', '#10b981', '#3b82f6', '#f59e0b', '#ef4444',
                        '#8b5cf6', '#ec4899'
                      ][index % 7]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }}
                    labelStyle={{ color: 'white' }}
                    formatter={(value) => [`${value} workouts`, 'Count']}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-gray-400">
                <p>No workout data yet</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
      
      {/* Recent Workouts */}
      <Card>
        <CardHeader>
          <CardTitle className="flex justify-between items-center">
            <span className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-emerald-500" />
              Recent Workouts
            </span>
            <Button variant="ghost" size="sm" asChild>
              <Link href="/workout-history" className="inline-flex items-center gap-1">
                View All <ChevronRight className="h-4 w-4" />
              </Link>
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {stats?.workouts && stats.workouts.length > 0 ? (
              stats.workouts.map((workout) => (
                <div key={workout.id} className="flex justify-between p-3 bg-gray-800 rounded-lg">
                  <div className="flex flex-col">
                    <span className="font-medium">{workout.type}</span>
                    <span className="text-sm text-gray-400">
                      {new Date(workout.date).toLocaleDateString('en-US', { 
                        year: 'numeric', 
                        month: 'short', 
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>
                  </div>
                  <div className="flex flex-col items-end">
                    <span className="flex items-center gap-1 text-amber-400">
                      <Clock className="h-4 w-4" />
                      {workout.duration} mins
                    </span>
                    <span className="flex items-center gap-1 text-sm text-red-400">
                      <Flame className="h-4 w-4" />
                      {workout.calories} cals
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center p-6 text-gray-400">
                <p>No workout history yet</p>
                <Button variant="outline" className="mt-4" asChild>
                  <Link href="/workouts">Start Your First Workout</Link>
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="container py-8 space-y-8">
      <div className="space-y-2">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-4 w-64" />
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array(4).fill(0).map((_, i) => (
          <div key={i} className="rounded-lg border bg-card shadow">
            <div className="p-6 space-y-2">
              <Skeleton className="h-5 w-24" />
              <Skeleton className="h-8 w-16" />
              <Skeleton className="h-4 w-20" />
            </div>
          </div>
        ))}
      </div>
      
      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-lg border bg-card shadow">
          <div className="p-6 space-y-4">
            <Skeleton className="h-6 w-36" />
            <Skeleton className="h-[300px] w-full" />
          </div>
        </div>
        
        <div className="rounded-lg border bg-card shadow">
          <div className="p-6 space-y-4">
            <Skeleton className="h-6 w-36" />
            <div className="space-y-4">
              {Array(4).fill(0).map((_, i) => (
                <div key={i} className="flex items-center space-x-4">
                  <Skeleton className="h-10 w-10 rounded-full" />
                  <div className="space-y-2 flex-1">
                    <Skeleton className="h-5 w-full" />
                    <Skeleton className="h-4 w-full" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({ 
  title, 
  value, 
  description, 
  icon,
  footer
}: { 
  title: string
  value: string
  description: string
  icon: React.ReactNode
  footer?: string
}) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-md font-medium text-muted-foreground">{title}</h3>
        {icon}
        </div>
        <div className="text-3xl font-bold">
          {value}
        </div>
        <p className="text-sm text-muted-foreground">
          {description}
        </p>
        {footer && (
          <div className="mt-3 pt-3 border-t text-sm text-muted-foreground">
            {footer}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
