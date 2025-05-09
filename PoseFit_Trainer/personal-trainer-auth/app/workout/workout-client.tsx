'use client';

import { useEffect, useState } from &apos;react&apos;;
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { formatExerciseName } from '@/lib/api-utils';
import { useRouter } from 'next/navigation';
import { useWorkoutHistory } from '@/hooks/useWorkoutHistory';

type WorkoutClientProps = {
  exercise: string;
  sets: number;
  reps: number;
};

function getSessionCookie() {
  if (typeof document === &apos;undefined&apos;) return null;
  const match = document.cookie.match(/(?:^|; )session=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : null;
}

export function WorkoutClient({ exercise, sets, reps }: WorkoutClientProps) {
  const router = useRouter();
  const { saveWorkout } = useWorkoutHistory();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [streamError, setStreamError] = useState<string | null>(null);
  const [metrics, setMetrics] = useState({
    currentSet: 0,
    totalSets: sets,
    reps: 0,
    totalReps: reps,
    caloriesBurned: 0,
    timeElapsed: 0,
    feedback: 'Starting workout...'
  });
  const [isPaused, setIsPaused] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);

  useEffect(() => {
    startWorkout();
    
    // Add beforeunload event listener to clean up when user closes tab or navigates away
    const handleBeforeUnload = () => {
      if (sessionId) {
        // Use the sync version of XMLHttpRequest to ensure it runs before page unloads
        const xhr = new XMLHttpRequest();
        xhr.open(&apos;POST&apos;, '/api/workout/release-cameras', false); // false makes it synchronous
        xhr.setRequestHeader('Content-Type', 'application/json');
        try {
          xhr.send();
          console.log('Released cameras on page unload');
        } catch (e) {
          console.error('Failed to release cameras on unload');
        }
      }
    };
    
    window.addEventListener(&apos;beforeunload&apos;, handleBeforeUnload);
    
    // Cleanup function to ensure camera resources are released
    return () => {
      // Remove the event listener
      window.removeEventListener(&apos;beforeunload&apos;, handleBeforeUnload);
      
      // When component unmounts, release cameras and clean up
      if (sessionId) {
        console.log('Component unmounting, cleaning up resources');
        
        // Release all cameras immediately
        fetch('/api/workout/release-cameras', { method: &apos;POST&apos; })
          .catch(err => console.error('Error releasing cameras on unmount:', err));
          
        // Also try to stop the workout session
        fetch(`/api/workout/stop/${sessionId}`, { method: &apos;POST&apos; })
          .catch(err => console.error('Error stopping workout on unmount:', err));
      }
    };
  }, []);

  const startWorkout = async () => {
    try {
      setStreamError(null);
      setAuthError(null);
      const response = await fetch('/api/workout', {
        method: &apos;POST&apos;,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          exercise,
          sets,
          reps
        })
      });

      if (response.status === 401) {
        // Check for session cookie
        const session = getSessionCookie();
        if (!session) {
          router.push('/login');
          return;
        } else {
          setAuthError('Session expired or invalid. Please sign in again.');
          return;
        }
      }

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Failed to start workout');
      }

      setSessionId(data.session_id);
      if (typeof window !== &apos;undefined&apos;) {
        sessionStorage.setItem(&apos;activeSessionId&apos;, data.session_id);
      }
      startMetricsUpdate();
    } catch (error) {
      console.error('Error starting workout:', error);
      setStreamError('Failed to start workout. Please try again.');
      setMetrics(m => ({ ...m, feedback: 'Error starting workout' }));
    }
  };

  const startMetricsUpdate = () => {
    const interval = setInterval(async () => {
      if (!sessionId) return;

      try {
        const response = await fetch(`/api/workout/metrics/${sessionId}`);
        if (response.status === 401) {
          const session = getSessionCookie();
          if (!session) {
            router.push('/login');
            return;
          } else {
            setAuthError('Session expired or invalid. Please sign in again.');
            clearInterval(interval);
            return;
          }
        }
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.error || 'Failed to get metrics');
        }
        setMetrics({
          currentSet: data.current_set,
          totalSets: sets,
          reps: data.count,
          totalReps: reps,
          caloriesBurned: Math.round(data.calories_burned || 0),
          timeElapsed: data.time_elapsed || 0,
          feedback: data.feedback || 'Keep going!'
        });
      } catch (error) {
        console.error('Error updating metrics:', error);
      }
    }, 1000);
    return () => clearInterval(interval);
  };

  const stopWorkout = async () => {
    if (!sessionId) return;

    try {
      console.log('Stopping workout session:', sessionId);
      
      // First, release all cameras to ensure they are turned off immediately
      await fetch('/api/workout/release-cameras', { method: &apos;POST&apos; })
        .catch(err => console.error('Error releasing cameras:', err));
      
      // Start navigating to summary page immediately
      const navigationPromise = router.push('/workouts/summary');
      
      // Get final metrics in parallel (don't block navigation)
      fetch(`/api/workout/metrics/${sessionId}`)
        .then(async (response) => {
          if (!response.ok) return;
          
          const finalMetrics = await response.json();
          // Calculate repetitions properly from the terminal output data
          const actualReps = finalMetrics.count || 0;
          
          // Save workout results using our hook
          saveWorkout({
            exerciseType: exercise,
            setsCompleted: finalMetrics.current_set || 0,
            totalSets: sets,
            repsCompleted: actualReps,
            totalReps: sets * reps,
            caloriesBurned: Math.round(finalMetrics.calories_burned || 0),
            duration: finalMetrics.time_elapsed || 0
          });
        })
        .catch(error => console.error('Error getting final metrics:', error));
      
      // Stop the workout session in the background
      fetch(`/api/workout/stop/${sessionId}`, { method: &apos;POST&apos; })
        .catch(error => console.error('Error stopping workout:', error));
      
      // Make sure navigation happens regardless
      await navigationPromise;
    } catch (error) {
      console.error('Error stopping workout:', error);
      // If all else fails, try to navigate anyway
      router.push('/workouts/summary');
    }
  };

  const pauseWorkout = async () => {
    if (!sessionId) return;
    try {
      await fetch(`/api/workout/pause/${sessionId}`, { method: &apos;POST&apos; });
      setIsPaused(true);
    } catch (error) {
      console.error('Error pausing workout:', error);
    }
  };

  const resumeWorkout = async () => {
    if (!sessionId) return;
    try {
      await fetch(`/api/workout/resume/${sessionId}`, { method: &apos;POST&apos; });
      setIsPaused(false);
    } catch (error) {
      console.error('Error resuming workout:', error);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, &apos;0&apos;)}:${secs.toString().padStart(2, &apos;0&apos;)}`;
  };

  return (
    <div className="container mx-auto p-4">
      <Card className="p-4 w-full max-w-5xl mx-auto">
        {authError && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
            <span className="block sm:inline">{authError}</span>
            <Button className="ml-4" onClick={() => router.push('/login')}>Sign In</Button>
          </div>
        )}
        <div className="aspect-video bg-black rounded-lg overflow-hidden relative">
          {streamError ? (
            <div className="absolute inset-0 flex items-center justify-center text-white bg-red-900/50">
              <div className="text-center p-4">
                <p className="mb-4">{streamError}</p>
                <Button onClick={startWorkout}>
                  Try Again
                </Button>
              </div>
            </div>
          ) : sessionId ? (
            <>
              {!isPaused ? (
                <img
                  id="workout-stream"
                  src={`/api/workout/stream/${sessionId}`}
                  alt="Workout Stream"
                  className="w-full h-full object-contain"
                  onError={() => setStreamError('Failed to load video stream')}
                />
              ) : (
                <div className="absolute inset-0 flex items-center justify-center bg-black/80 text-white text-2xl font-bold">
                  Paused
                </div>
              )}
              <div className="absolute bottom-4 right-4 flex gap-2">
                <Button
                  variant="secondary"
                  size="lg"
                  className="font-bold text-lg shadow-lg"
                  onClick={isPaused ? resumeWorkout : pauseWorkout}
                >
                  {isPaused ? &apos;Resume&apos; : &apos;Pause&apos;}
                </Button>
                <Button
                  variant="destructive"
                  size="lg"
                  className="font-bold text-lg shadow-lg"
                  onClick={stopWorkout}
                >
                  Stop Workout
                </Button>
              </div>
            </>
          ) : (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
} 