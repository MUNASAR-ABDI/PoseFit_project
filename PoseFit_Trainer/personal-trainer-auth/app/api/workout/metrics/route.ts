import { NextResponse } from 'next/server';

// Simulated workout history data (fallback only)
const sampleWorkoutData = [
  { id: &apos;1&apos;, date: '2023-10-01', exercise: 'Bicep Curls', duration: 30, sets: 3, reps: 12, calories: 150 },
  { id: &apos;2&apos;, date: '2023-10-03', exercise: 'Push Ups', duration: 25, sets: 3, reps: 15, calories: 120 },
  { id: &apos;3&apos;, date: '2023-10-05', exercise: &apos;Squats&apos;, duration: 35, sets: 4, reps: 12, calories: 200 },
  { id: &apos;4&apos;, date: '2023-10-08', exercise: 'Mountain Climbers', duration: 20, sets: 3, reps: 20, calories: 180 },
  { id: &apos;5&apos;, date: '2023-10-10', exercise: 'Bicep Curls', duration: 32, sets: 3, reps: 12, calories: 155 },
  { id: &apos;6&apos;, date: '2023-11-02', exercise: 'Push Ups', duration: 28, sets: 3, reps: 15, calories: 130 },
  { id: &apos;7&apos;, date: '2023-11-05', exercise: &apos;Squats&apos;, duration: 40, sets: 4, reps: 12, calories: 220 },
  { id: &apos;8&apos;, date: '2023-11-09', exercise: 'Mountain Climbers', duration: 22, sets: 3, reps: 20, calories: 190 },
  { id: &apos;9&apos;, date: '2023-11-12', exercise: 'Bicep Curls', duration: 33, sets: 3, reps: 12, calories: 160 },
  { id: &apos;10&apos;, date: '2023-12-01', exercise: 'Push Ups', duration: 30, sets: 3, reps: 15, calories: 140 },
  { id: &apos;11&apos;, date: '2023-12-05', exercise: &apos;Squats&apos;, duration: 42, sets: 4, reps: 12, calories: 225 },
  { id: &apos;12&apos;, date: '2023-12-10', exercise: 'Mountain Climbers', duration: 25, sets: 3, reps: 20, calories: 200 },
  { id: &apos;13&apos;, date: '2024-01-03', exercise: 'Bicep Curls', duration: 35, sets: 3, reps: 12, calories: 165 },
  { id: &apos;14&apos;, date: '2024-01-07', exercise: 'Push Ups', duration: 32, sets: 3, reps: 15, calories: 145 },
  { id: &apos;15&apos;, date: '2024-01-12', exercise: &apos;Squats&apos;, duration: 45, sets: 4, reps: 12, calories: 230 },
];

export async function GET() {
  try {
    // Set the correct backend URL - use the .env variable or default to localhost:8002
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8002';
    
    // Try to connect to the real backend API for workout metrics
    try {
      // Make the request to the workout metrics endpoint
      const response = await fetch(`${backendUrl}/workout-metrics`, {
        method: &apos;GET&apos;,
        headers: {
          'Content-Type': 'application/json',
          // Add authorization if needed
          // &apos;Authorization&apos;: `Bearer ${token}`
        },
      });
      
      if (response.ok) {
        // Parse the response data
        const data = await response.json();
        console.log('Successfully fetched workout metrics from backend:', data);
        return NextResponse.json({ workouts: data });
      } else {
        console.error('Backend API error:', response.status, response.statusText);
        
        // Try alternate endpoint if the first one fails
        try {
          const alternateResponse = await fetch(`${backendUrl}/workout-history`, {
            method: &apos;GET&apos;,
            headers: {
              'Content-Type': 'application/json',
            },
          });
          
          if (alternateResponse.ok) {
            const altData = await alternateResponse.json();
            console.log('Successfully fetched from alternate endpoint:', altData);
            return NextResponse.json({ workouts: altData });
          }
        } catch (altError) {
          console.error('Error with alternate endpoint:', altError);
        }
      }
    } catch (error) {
      console.error('Error connecting to backend API:', error);
    }
    
    // Fallback to sample data if backend connection failed
    console.log('Using sample workout metrics data as fallback');
    return NextResponse.json({ workouts: sampleWorkoutData });
    
  } catch (error) {
    console.error('Unexpected error in workout metrics API:', error);
    return NextResponse.json(
      { error: 'Failed to fetch workout metrics', workouts: sampleWorkoutData },
      { status: 200 } // Still return 200 with sample data to avoid UI errors
    );
  }
} 