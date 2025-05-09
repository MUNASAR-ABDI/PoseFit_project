"use client"

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, Terminal } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface WorkoutMetrics {
  reps_completed: number;
  calories_burned: number;
  completion_percentage: number;
  feedback: string;
}

export default function TerminalPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [output, setOutput] = useState<string[]>([]);
  const [isStarted, setIsStarted] = useState(false);
  const [currentRep, setCurrentRep] = useState(0);
  const [currentSet, setCurrentSet] = useState(1);
  const [sessionId, setSessionId] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<WorkoutMetrics>({
    reps_completed: 0,
    calories_burned: 0,
    completion_percentage: 0,
    feedback: ''
  });
  const [isProcessing, setIsProcessing] = useState(true);

  const exercise = searchParams.get('exercise');
  const totalSets = parseInt(searchParams.get('sets') || '0');
  const repsPerSet = parseInt(searchParams.get('reps') || '0');

  const initializeWorkout = async () => {
    try {
      const response = await fetch('/api/workout/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          exercise,
          sets: totalSets,
          reps: repsPerSet,
          mode: 'terminal'
        }),
        credentials: 'include'
      });

      if (!response.ok) {
        const errorData = await response.json();
        const errorMessage = errorData.detail || 'Failed to start workout';
        if (response.status === 401) {
          localStorage.setItem('pendingWorkout', JSON.stringify({ exercise, sets: totalSets, reps: repsPerSet }));
          router.push('/login');
          return;
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      setSessionId(data.session_id);
      setIsStarted(true);
      addOutput('Workout started! Complete your first rep...');
    } catch (error: any) {
      console.error('Error initializing workout:', error);
      setError(error.message);
    }
  };

  useEffect(() => {
    if (exercise && repsPerSet && totalSets) {
      router.push(`/workout?exercise=${exercise}&reps=${repsPerSet}&sets=${totalSets}`);
    }
  }, [exercise, repsPerSet, totalSets, router]);

  useEffect(() => {
    if (sessionId) {
      initializeWorkout();
    }
  }, [sessionId, initializeWorkout]);

  const addOutput = (message: string) => {
    setOutput(prev => [...prev, message]);
  };

  const startProcessing = async () => {
    while (isProcessing) {
      try {
        const response = await fetch('/api/workout/process-frame', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_id: sessionId }),
          credentials: 'include'
        });

        if (!response.ok) {
          throw new Error(await response.text());
        }

        const data = await response.json();
        setMetrics(data.metrics ?? metrics);
        
        // Add a small delay to prevent overwhelming the server
        await new Promise(resolve => setTimeout(resolve, 100));
      } catch (error) {
        console.error('Error processing frame:', error);
        setError('Error processing frame. Please try again.');
        break;
      }
    }
  };

  const completeRep = async () => {
    try {
      const newRep = currentRep + 1;
      const isSetComplete = newRep === repsPerSet;
      const isWorkoutComplete = isSetComplete && currentSet === totalSets;

      const response = await fetch('/api/workout/complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          exercise,
          repCount: newRep,
          setCount: currentSet,
          completed: isWorkoutComplete
        })
      });

      if (!response.ok) throw new Error('Failed to record rep');

      if (isWorkoutComplete) {
        addOutput('Congratulations! Workout completed!');
        setTimeout(() => router.push('/dashboard'), 2000);
        return;
      }

      if (isSetComplete) {
        setCurrentSet(prev => prev + 1);
        setCurrentRep(0);
        addOutput(`Set ${currentSet} completed! Rest for 30 seconds...`);
        addOutput(`Starting Set ${currentSet + 1}...`);
      } else {
        setCurrentRep(newRep);
        addOutput(`Rep ${newRep} completed!`);
      }
    } catch (err) {
      setError('Failed to record rep. Please try again.');
    }
  };

  const handleBack = () => {
    router.push('/workouts');
  };

  const formatMetric = (value: number) => Math.floor(value);

  const startCameraWorkout = async () => {
    try {
      const response = await fetch('/api/workout/terminal-camera', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          exercise,
          sets: totalSets,
          reps: repsPerSet
        })
      });

      if (!response.ok) throw new Error('Failed to start camera workout');
      
      addOutput('Starting camera workout...');
      addOutput('A new window will open with the camera feed.');
      addOutput('Press "q" to quit the camera workout.');
    } catch (err) {
      setError('Failed to start camera workout. Please try again.');
    }
  };

  return (
    <div className="container py-8">
      <div className="flex items-center gap-4 mb-6">
        <Button variant="ghost" onClick={handleBack}>
          <ArrowLeft className="mr-2" />
          Back
        </Button>
        <h1 className="text-2xl font-bold">Terminal Workout</h1>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Terminal className="h-5 w-5" />
            Workout Progress
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span>Reps Completed:</span>
              <span className="font-bold">{formatMetric(metrics.reps_completed)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Calories Burned:</span>
              <span className="font-bold">{formatMetric(metrics.calories_burned)} kcal</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Completion:</span>
              <span className="font-bold">{formatMetric(metrics.completion_percentage)}%</span>
            </div>
            <div className="mt-4 p-4 bg-muted rounded-lg">
              <p className="font-medium">Feedback:</p>
              <p className="text-muted-foreground">{metrics.feedback || 'Initializing...'}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col gap-4">
            <p className="text-center text-muted-foreground">
              Choose your workout mode:
            </p>
            <div className="flex justify-center gap-4">
              <Button
                variant="outline"
                onClick={() => {
                  router.push(`/workouts/camera?exercise=${exercise}&sets=${totalSets}&reps=${repsPerSet}`);
                }}
              >
                Web Camera Mode
              </Button>
              <Button
                variant="outline"
                onClick={startCameraWorkout}
              >
                Terminal Camera Mode
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="w-full max-w-3xl bg-black text-green-400 p-4 rounded-lg font-mono">
        <div className="h-64 overflow-y-auto mb-4">
          {output.map((line, index) => (
            <div key={index}>{`> ${line}`}</div>
          ))}
        </div>

        {!isStarted ? (
          <Button
            className="w-full"
            onClick={initializeWorkout}
          >
            Start Workout
          </Button>
        ) : (
          <div className="flex flex-col gap-4">
            <div className="text-white">
              Current progress: Set {currentSet}/{totalSets}, Rep {currentRep}/{repsPerSet}
            </div>
            <Button
              className="w-full"
              onClick={completeRep}
            >
              Complete Rep
            </Button>
          </div>
        )}
      </div>
    </div>
  );
} 