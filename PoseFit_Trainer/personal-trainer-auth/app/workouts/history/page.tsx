'use client';

import { useState, useEffect } from &apos;react&apos;;
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Calendar, Clock, Dumbbell, Filter, Trophy } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface WorkoutSession {
  id: string;
  date: string;
  exercise: string;
  duration: number;
  sets: number;
  reps: number;
  calories: number;
  completed: boolean;
}

export default function WorkoutHistoryPage() {
  const [workouts, setWorkouts] = useState<WorkoutSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState(&apos;all&apos;);

  useEffect(() => {
    async function fetchWorkoutHistory() {
      try {
        setLoading(true);
        const response = await fetch('/api/workouts/history');
        
        if (!response.ok) {
          throw new Error('Failed to fetch workout history');
        }
        
        const data = await response.json();
        setWorkouts(data.workouts || []);
      } catch (err) {
        console.error('Error fetching workout history:', err);
        setError('Failed to load workout history. Please try again later.');
        
        // Empty array instead of sample data
        setWorkouts([]);
      } finally {
        setLoading(false);
      }
    }
    
    fetchWorkoutHistory();
  }, []);

  // Filter workouts based on selected filter
  const filteredWorkouts = workouts.filter(workout => {
    if (filter === &apos;all&apos;) return true;
    if (filter === &apos;completed&apos;) return workout.completed;
    if (filter === &apos;incomplete&apos;) return !workout.completed;
    
    // Filter by exercise type
    return workout.exercise.toLowerCase().includes(filter.toLowerCase());
  });

  // Get unique exercise types for filter
  const exerciseTypes = [...new Set(workouts.map(w => w.exercise))];

  // Calculate stats
  const totalWorkouts = workouts.length;
  const completedWorkouts = workouts.filter(w => w.completed).length;
  const totalDuration = workouts.reduce((sum, w) => sum + w.duration, 0);
  const totalCalories = workouts.reduce((sum, w) => sum + w.calories, 0);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: &apos;numeric&apos;, 
      month: &apos;short&apos;, 
      day: &apos;numeric&apos; 
    });
  };

  if (loading) {
    return (
      <div className="container py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container py-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Workout History</h1>
          <p className="text-muted-foreground">View and analyze your previous workout sessions</p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={filter} onValueChange={setFilter}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Filter workouts" />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectLabel>Status</SelectLabel>
                <SelectItem value="all">All Workouts</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="incomplete">Incomplete</SelectItem>
              </SelectGroup>
              <SelectGroup>
                <SelectLabel>Exercise Type</SelectLabel>
                {exerciseTypes.map(type => (
                  <SelectItem key={type} value={type}>{type}</SelectItem>
                ))}
              </SelectGroup>
            </SelectContent>
          </Select>
          <Button variant="outline" size="icon">
            <Filter className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Workouts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalWorkouts}</div>
            <p className="text-xs text-muted-foreground">All time</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Completion Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {totalWorkouts > 0 ? Math.round((completedWorkouts / totalWorkouts) * 100) : 0}%
            </div>
            <p className="text-xs text-muted-foreground">
              {completedWorkouts} of {totalWorkouts} workouts completed
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalDuration} min</div>
            <p className="text-xs text-muted-foreground">Time spent exercising</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Calories Burned</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalCalories}</div>
            <p className="text-xs text-muted-foreground">Estimated total</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Workout Sessions</CardTitle>
          <CardDescription>
            {filteredWorkouts.length} {filter !== &apos;all&apos; ? 'filtered ' : ''}
            workout{filteredWorkouts.length !== 1 ? &apos;s&apos; : ''}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {filteredWorkouts.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Exercise</TableHead>
                  <TableHead>Sets × Reps</TableHead>
                  <TableHead>Duration</TableHead>
                  <TableHead>Calories</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredWorkouts.map((workout) => (
                  <TableRow key={workout.id}>
                    <TableCell className="font-medium">
                      {formatDate(workout.date)}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Dumbbell className="h-4 w-4 text-muted-foreground" />
                        {workout.exercise}
                      </div>
                    </TableCell>
                    <TableCell>{workout.sets} × {workout.reps}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3 text-muted-foreground" />
                        {workout.duration} min
                      </div>
                    </TableCell>
                    <TableCell>{workout.calories} cal</TableCell>
                    <TableCell>
                      <Badge variant={workout.completed ? "success" : "destructive"}>
                        {workout.completed ? "Completed" : "Incomplete"}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="sm">
                        Details
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <Trophy className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">No workouts found</h3>
              <p className="text-sm text-muted-foreground max-w-md">
                {filter !== &apos;all&apos;
                  ? "Try changing your filter to see more workouts."
                  : "You haven't recorded any workouts yet. Start your fitness journey today!"}
              </p>
              {filter !== &apos;all&apos; && (
                <Button variant="outline" className="mt-4" onClick={() => setFilter(&apos;all&apos;)}>
                  Show all workouts
                </Button>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
} 