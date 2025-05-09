'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Check, Clock, Dumbbell, Flame } from 'lucide-react';
import { formatExerciseName } from '@/lib/api-utils';
import { useWorkoutHistory } from '@/hooks/useWorkoutHistory';
import { useState, useEffect } from 'react';
import { Progress } from '@/components/ui/progress';

export default function WorkoutSummaryPage() {
  const { lastWorkout, isLoading } = useWorkoutHistory();
  const [showOptions, setShowOptions] = useState(false);
  const [videoAction, setVideoAction] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [progressStatus, setProgressStatus] = useState<string | null>(null);
  const [progressMessage, setProgressMessage] = useState<string | null>(null);
  const [indeterminateProgress, setIndeterminateProgress] = useState(false);

  // Animated progress for visual feedback before we get actual progress
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (indeterminateProgress && progress < 20) {
      interval = setInterval(() => {
        setProgress(prev => {
          const newProgress = prev + 1;
          return newProgress <= 20 ? newProgress : 20;
        });
      }, 100);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [indeterminateProgress, progress]);

  // Poll for progress updates if we have a taskId
  useEffect(() => {
    if (!taskId) return;
    
    const checkProgress = async () => {
      try {
        const res = await fetch(`/api/workout/video/progress/${taskId}`);
        if (!res.ok) return;
        
        const data = await res.json();
        setIndeterminateProgress(false);
        
        // Ensure progress always increases and never goes backward
        setProgress(prev => {
          const newProgress = data.progress || 0;
          return newProgress > prev ? newProgress : prev;
        });
        
        setProgressStatus(data.status || null);
        setProgressMessage(data.message || null);
        
        // If the process is complete or errored, stop polling
        if (['completed', 'error'].includes(data.status)) {
          if (data.status === 'completed') {
            // Ensure progress reaches 100% for completed tasks
            setProgress(100);
            setTimeout(() => {
              setSuccessMessage('Video successfully processed and sent!');
              setVideoAction('save_and_email');
              setLoading(false);
              setTaskId(null);
            }, 500); // Small delay for visual completion
          } else if (data.status === 'error') {
            setError(data.message || 'Error processing video');
            setLoading(false);
            setTaskId(null);
          }
        }
      } catch (e) {
        console.error('Failed to check progress:', e);
      }
    };
    
    // Poll every second
    const interval = setInterval(checkProgress, 1000);
    return () => clearInterval(interval);
  }, [taskId]);

  if (isLoading) {
    return (
      <div className="container max-w-xl py-12 flex justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full"></div>
      </div>
    );
  }

  // Format workout time (MM:SS)
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleContinue = () => {
    window.location.href = '/workouts/exercises';
  };
  
  const handleNo = () => {
    setShowOptions(true);
  };
  
  const handleVideoAction = async (action: string) => {
    setVideoAction(null);
    setLoading(true);
    setError(null);
    setSuccessMessage(null);
    setProgress(0);
    setProgressStatus(null);
    setProgressMessage(null);
    
    // For save_and_email action, immediately show progress bar with indeterminate progress
    if (action === 'save_and_email') {
      setIndeterminateProgress(true);
    }
    
    // Use session ID from sessionStorage
    const sessionId = typeof window !== 'undefined' ? sessionStorage.getItem('activeSessionId') : null;
    if (!sessionId) {
      setError('No session ID found.');
      setLoading(false);
      setIndeterminateProgress(false);
      return;
    }
    
    let endpoint = '';
    if (action === 'save_and_email') endpoint = `/api/workout/video/save-and-email/${sessionId}`;
    else if (action === 'save_only') endpoint = `/api/workout/video/save/${sessionId}`;
    else if (action === 'delete') endpoint = `/api/workout/video/delete/${sessionId}`;
    
    try {
      const res = await fetch(endpoint, { method: 'POST' });
      const data = await res.json();
      
      if (!res.ok || data.error) throw new Error(data.error || 'Failed to process video action');
      
      if (action === 'save_and_email' && data.task_id) {
        // If we received a task_id, start polling for progress
        setTaskId(data.task_id);
      } else {
        // For actions without progress tracking
        setVideoAction(action);
        if (data.message) setSuccessMessage(data.message);
        setLoading(false);
        setIndeterminateProgress(false);
      }
    } catch (e: unknown) {
      setError(e.message || 'Error processing action');
      setLoading(false);
      setIndeterminateProgress(false);
    }
  };

  return (
    <div className="container max-w-xl py-12">
      {successMessage && (
        <div className="mb-4 p-3 bg-green-100 text-green-800 rounded text-center font-semibold shadow">
          {successMessage}
        </div>
      )}
      <Card className="shadow-lg">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 bg-green-100 p-3 rounded-full w-16 h-16 flex items-center justify-center">
            <Check className="h-8 w-8 text-green-600" />
          </div>
          <CardTitle className="text-2xl">Workout Complete!</CardTitle>
          <CardDescription>Great job on your fitness journey</CardDescription>
        </CardHeader>
        
        <CardContent>
          <div className="grid grid-cols-3 gap-4 my-6">
            <div className="flex flex-col items-center p-4 bg-muted rounded-lg">
              <Dumbbell className="h-6 w-6 text-primary mb-2" />
              <span className="text-2xl font-bold">{lastWorkout?.repsCompleted || 0}</span>
              <span className="text-xs text-muted-foreground">Reps</span>
            </div>
            <div className="flex flex-col items-center p-4 bg-muted rounded-lg">
              <Clock className="h-6 w-6 text-primary mb-2" />
              <span className="text-2xl font-bold">{lastWorkout ? formatTime(lastWorkout.duration) : "00:00"}</span>
              <span className="text-xs text-muted-foreground">Duration</span>
            </div>
            <div className="flex flex-col items-center p-4 bg-muted rounded-lg">
              <Flame className="h-6 w-6 text-primary mb-2" />
              <span className="text-2xl font-bold">{lastWorkout?.caloriesBurned || 0}</span>
              <span className="text-xs text-muted-foreground">Calories</span>
            </div>
          </div>
          
          <div className="bg-muted p-4 rounded-lg">
            <h3 className="font-medium mb-2">Workout Overview</h3>
            <ul className="space-y-2">
              <li className="flex justify-between">
                <span>Exercise Type</span>
                <span className="font-medium">{lastWorkout ? formatExerciseName(lastWorkout.exerciseType) : "Unknown"}</span>
              </li>
              <li className="flex justify-between">
                <span>Sets Completed</span>
                <span className="font-medium">{lastWorkout ? `${lastWorkout.setsCompleted}/${lastWorkout.totalSets}` : "0/0"}</span>
              </li>
              <li className="flex justify-between">
                <span>Reps Completed</span>
                <span className="font-medium">{lastWorkout ? `${lastWorkout.repsCompleted}/${lastWorkout.totalReps}` : "0/0"}</span>
              </li>
            </ul>
          </div>
          
          {/* Progress Bar for Video Processing */}
          {(loading && taskId) || indeterminateProgress ? (
            <div className="mt-8">
              <h3 className="font-medium mb-2">Processing Video</h3>
              <Progress value={progress} className="h-2 mb-2" />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>{progress}%</span>
                <span>100%</span>
              </div>
              <p className="text-sm text-center text-muted-foreground mt-2">
                {progressMessage || 'Processing your workout video...'}
              </p>
            </div>
          ) : null}
          
          {!showOptions && videoAction === null && !loading && !indeterminateProgress && (
            <div className="mt-8 text-center">
              <p className="mb-4 text-lg font-semibold">Do you want to continue with a different exercise?</p>
              <div className="flex justify-center gap-4">
                <Button onClick={handleContinue} className="px-8">Yes</Button>
                <Button variant="outline" onClick={handleNo} className="px-8">No</Button>
              </div>
            </div>
          )}
          {showOptions && videoAction === null && !loading && !indeterminateProgress && (
            <div className="mt-8 text-center">
              <p className="mb-4 text-lg font-semibold">What would you like to do with your workout video?</p>
              {error && <div className="text-red-600 mb-2">{error}</div>}
              <div className="flex flex-col gap-4">
                <Button onClick={() => handleVideoAction('save_and_email')} disabled={loading || indeterminateProgress}>Save Video & Email Me</Button>
                <Button onClick={() => handleVideoAction('save_only')} disabled={loading || indeterminateProgress}>Save Only</Button>
                <Button variant="destructive" onClick={() => handleVideoAction('delete')} disabled={loading || indeterminateProgress}>Delete Video</Button>
              </div>
            </div>
          )}
          {videoAction && !loading && !indeterminateProgress && (
            <div className="mt-8 text-center">
              <p className="mb-4 text-lg font-semibold">Thank you! Your choice has been recorded.</p>
              <Button onClick={() => window.location.href = '/dashboard'}>Return to Dashboard</Button>
            </div>
          )}
        </CardContent>
        
        <CardFooter className="flex flex-col space-y-2">
          <Button className="w-full" asChild>
            <Link href="/workouts/exercises">
              Start New Workout
            </Link>
          </Button>
          <Button variant="outline" className="w-full" asChild>
            <Link href="/dashboard">
              Return to Dashboard
            </Link>
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
} 