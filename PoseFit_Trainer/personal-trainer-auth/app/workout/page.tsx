import { Suspense } from 'react';
import { WorkoutClient } from '@/app/workout/workout-client';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

export default function WorkoutPage({
  searchParams,
}: {
  searchParams: { [key: string]: string | string[] | undefined }
}) {
  // Server-side: check for session cookie
  const session = cookies().get('session');
  if (!session) {
    redirect('/login');
  }

  // Parse and validate params server-side with defaults
  const exercise = 
    typeof searchParams.exercise === 'string' ? searchParams.exercise : 'bicep-curls';
    
  const sets = 
    typeof searchParams.sets === 'string' && !isNaN(parseInt(searchParams.sets)) 
      ? parseInt(searchParams.sets) 
      : 3;
      
  const reps = 
    typeof searchParams.reps === 'string' && !isNaN(parseInt(searchParams.reps)) 
      ? parseInt(searchParams.reps) 
      : 10;

  return (
    <Suspense fallback={<div>Loading...</div>}>
      <WorkoutClient exercise={exercise} sets={sets} reps={reps} />
    </Suspense>
  );
} 