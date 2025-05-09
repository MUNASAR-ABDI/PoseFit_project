import { NextResponse } from 'next/server';
import { createErrorResponse } from '@/lib/api-utils';
import { apiRequest } from '@/lib/server-utils';

type WorkoutMetrics = {
  current_set: number;
  count: number;
  calories_burned: number;
  time_elapsed: number;
  feedback: string;
};

export async function GET(
  request: Request,
  { params }: { params: { sessionId: string } }
) {
  try {
    const data = await apiRequest<WorkoutMetrics>(`/workout-metrics/${params.sessionId}`);
    return NextResponse.json(data);
  } catch (error) {
    return createErrorResponse(error);
  }
} 