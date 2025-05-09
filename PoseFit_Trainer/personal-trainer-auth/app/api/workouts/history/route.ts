import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { cookies } from 'next/headers';

// Empty workout array - no sample data
const emptyWorkouts = [];

export async function GET() {
  try {
    // Set the correct backend URL - use the .env variable or default to localhost:8002
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8002';
    
    // Get authentication token from cookies
    const cookieStore = cookies();
    const authToken = cookieStore.get('next-auth.session-token')?.value || 
                      cookieStore.get('__Secure-next-auth.session-token')?.value;
    
    // Try to connect to the real backend API for workout history
    try {
      // Make the request to the workout-history endpoint
      const response = await fetch(`${backendUrl}/workout-history`, {
        method: &apos;GET&apos;,
        headers: {
          'Content-Type': 'application/json',
          // Add authorization with the token
          &apos;Authorization&apos;: authToken ? `Bearer ${authToken}` : ''
        },
      });
      
      if (response.ok) {
        // Parse the response data
        const data = await response.json();
        console.log('Successfully fetched workout data from backend:', data);
        return NextResponse.json({ workouts: data });
      } else {
        console.error('Backend API error:', response.status, response.statusText);
        
        // For testing purposes, generate some sample workout data if backend fails
        // This allows frontend development when backend is not fully connected
        // Remove this in production when properly connected to the backend
        const testWorkouts = [
          {
            id: &apos;1&apos;,
            date: new Date().toISOString(),
            exercise: 'Bicep Curls',
            duration: 25,
            sets: 3,
            reps: 12,
            calories: 150,
            completed: true
          }
        ];
        
        // Return test data in development, but make it clear in the console
        console.log('Returning test workout data for frontend development');
        return NextResponse.json({ workouts: testWorkouts });
      }
    } catch (error) {
      console.error('Error connecting to backend API:', error);
      
      // Same test data as above for development
      const testWorkouts = [
        {
          id: &apos;1&apos;,
          date: new Date().toISOString(),
          exercise: 'Bicep Curls',
          duration: 25,
          sets: 3,
          reps: 12,
          calories: 150,
          completed: true
        }
      ];
      
      console.log('Returning test workout data due to connection error');
      return NextResponse.json({ workouts: testWorkouts });
    }
        
  } catch (error) {
    console.error('Unexpected error in workout history API:', error);
    
    // Even on error, return valid data structure
    return NextResponse.json(
      { workouts: emptyWorkouts },
      { status: 200 } // Still return 200 with empty data to avoid UI errors
    );
  }
} 