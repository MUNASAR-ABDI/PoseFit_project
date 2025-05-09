import { NextResponse } from 'next/server';
import { createErrorResponse } from '@/lib/api-utils';
import { apiRequest } from '@/lib/server-utils';
import { cookies } from 'next/headers';

export async function POST(
  request: Request,
  { params }: { params: { sessionId: string } }
) {
  try {
    // First, immediately trigger camera release to ensure it happens quickly
    await apiRequest('/release-all-cameras', {
      method: &apos;POST&apos;
    }).catch(err => console.error('Error releasing cameras:', err));

    // Then get workout metrics (this doesn't block camera release)
    const metricsPromise = apiRequest('/workout-metrics/' + params.sessionId, {
      method: &apos;GET&apos;
    }).catch(() => null);
    
    // Stop the workout in parallel
    const stopPromise = apiRequest('/stop-workout', {
      method: &apos;POST&apos;,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `session_id=${params.sessionId}`
    });

    // Wait for both operations to complete
    const [metricsResponse, _] = await Promise.all([metricsPromise, stopPromise]);
    
    let workoutData = null;
    if (metricsResponse?.ok) {
      workoutData = await metricsResponse.json();
    }
    
    // Record the workout history in the background (don't await)
    if (workoutData) {
      try {
        // Get authorization token from cookies
        const cookieStore = cookies();
        const authToken = cookieStore.get('next-auth.session-token')?.value || 
                          cookieStore.get('__Secure-next-auth.session-token')?.value;
        
        // Use workout metrics to create a workout history entry (don't await)
        fetch(`/api/workouts/record-workout`, {
          method: &apos;POST&apos;,
          headers: {
            'Content-Type': 'application/json',
            &apos;Authorization&apos;: authToken ? `Bearer ${authToken}` : ''
          },
          body: JSON.stringify({
            sessionId: params.sessionId,
            exercise: workoutData.exercise || 'Unknown Exercise',
            sets: workoutData.sets_completed || 0,
            reps: workoutData.reps_completed || 0,
            duration: Math.round((workoutData.exercise_duration || 0) / 60),
            calories: Math.round((workoutData.exercise_duration || 0) * 0.05),
            completed: workoutData.exercise_completed || false,
            date: new Date().toISOString()
          })
        }).then(res => {
          console.log('Workout recorded in history response:', res.status);
        }).catch(historyError => {
          console.error('Error recording workout history:', historyError);
        });
      } catch (historyError) {
        console.error('Error recording workout history:', historyError);
      }
    }
    
    // Return success response immediately to speed up client navigation
    return NextResponse.json({ 
      success: true, 
      workoutRecorded: !!workoutData,
      metrics: workoutData 
    });
  } catch (error) {
    return createErrorResponse(error);
  }
} 