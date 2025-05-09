import { useState, useEffect } from 'react';

export interface WorkoutResults {
  id: string;
  exerciseType: string;
  setsCompleted: number;
  totalSets: number;
  repsCompleted: number;
  totalReps: number;
  caloriesBurned: number;
  duration: number; // in seconds
  timestamp: string; // ISO string
}

// Maximum number of workouts to store in history
const MAX_HISTORY_SIZE = 10;

export function useWorkoutHistory() {
  const [history, setHistory] = useState<WorkoutResults[]>([]);
  const [lastWorkout, setLastWorkout] = useState<WorkoutResults | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load workout history from localStorage
  useEffect(() => {
    try {
      const storedHistory = localStorage.getItem('workoutHistory');
      if (storedHistory) {
        const parsedHistory = JSON.parse(storedHistory) as WorkoutResults[];
        setHistory(parsedHistory);
        
        if (parsedHistory.length > 0) {
          // Sort by timestamp descending and get the most recent
          const sorted = [...parsedHistory].sort((a, b) => 
            new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
          );
          setLastWorkout(sorted[0]);
        }
      }

      // Try to get the last workout results
      const lastResults = localStorage.getItem('lastWorkoutResults');
      if (lastResults) {
        setLastWorkout(JSON.parse(lastResults));
      }
    } catch (error) {
      console.error('Error loading workout history:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Save a new workout to history
  const saveWorkout = (workout: Omit<WorkoutResults, 'id' | 'timestamp'>) => {
    try {
      // Create a new workout entry with ID and timestamp
      const newWorkout: WorkoutResults = {
        ...workout,
        id: crypto.randomUUID(),
        timestamp: new Date().toISOString()
      };

      // Update the last workout
      setLastWorkout(newWorkout);
      localStorage.setItem('lastWorkoutResults', JSON.stringify(newWorkout));

      // Update history
      setHistory(prevHistory => {
        // Add new workout to beginning of history
        const updatedHistory = [newWorkout, ...prevHistory];
        
        // Limit history size
        const limitedHistory = updatedHistory.slice(0, MAX_HISTORY_SIZE);
        
        // Save to localStorage
        localStorage.setItem('workoutHistory', JSON.stringify(limitedHistory));
        
        return limitedHistory;
      });

      return newWorkout;
    } catch (error) {
      console.error('Error saving workout:', error);
      return null;
    }
  };

  // Clear workout history
  const clearHistory = () => {
    setHistory([]);
    setLastWorkout(null);
    localStorage.removeItem('workoutHistory');
    localStorage.removeItem('lastWorkoutResults');
  };

  return {
    history,
    lastWorkout,
    isLoading,
    saveWorkout,
    clearHistory
  };
} 