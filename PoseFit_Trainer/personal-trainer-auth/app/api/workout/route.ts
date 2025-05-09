import { NextResponse } from 'next/server';
import { normalizeExerciseName, createErrorResponse } from '@/lib/api-utils';
import { apiRequest } from '@/lib/server-utils';

type WorkoutResponse = {
  session_id: string;
  stream_url: string;
};

export async function POST(request: Request) {
  try {
    const body = await request.json();
    
    // Normalize exercise name for backend
    const normalizedBody = {
      ...body,
      exercise: normalizeExerciseName(body.exercise)
    };
    
    const data = await apiRequest<WorkoutResponse>('/start-workout', {
      method: &apos;POST&apos;,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(normalizedBody)
    });

    return NextResponse.json(data);
  } catch (error) {
    return createErrorResponse(error);
  }
} 