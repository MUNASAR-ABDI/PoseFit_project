import { NextResponse } from 'next/server';

export const BACKEND_URL = 'http://localhost:8002';

// Exercise name mapping between frontend and backend
export const EXERCISE_MAPPING = {
  'bicep-curls': 'bicep_curls',
  'push-ups': 'push_ups',
  'squats': 'squats',
  'mountain-climbers': 'mountain_climbers',
};

// Standardize exercise name for backend API
export function normalizeExerciseName(exerciseName: string): string {
  return EXERCISE_MAPPING[exerciseName as keyof typeof EXERCISE_MAPPING] || exerciseName.replace(/-/g, '_');
}

// Formats exercise name for display
export function formatExerciseName(exerciseName: string): string {
  return exerciseName
    .split(/[-_]/)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

// Error response helper
export function createErrorResponse(error: unknown, status = 500) {
  console.error('API error:', error);
  const message = error instanceof Error ? error.message : 'An unexpected error occurred';
  
  return NextResponse.json(
    { error: message },
    { status }
  );
} 