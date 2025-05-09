import { Suspense } from &apos;react&apos;;
import { WorkoutClient } from '@/app/workout/workout-client';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

export default function WorkoutPage({
  searchParams,
}: {
  searchParams: { [key: string]: string | string[] | undefined }
}) {
  // Server-side: check for session cookie
  const session = cookies().get(&apos;session&apos;);
  if (!session) {
    redirect('/login');
  }

  // Parse and validate params server-side with defaults
  const exercise = 
    typeof searchParams.exercise === &apos;string&apos; ? searchParams.exercise : 'bicep-curls';
    
  const sets = 
    typeof searchParams.sets === &apos;string&apos; && !isNaN(parseInt(searchParams.sets)) 
      ? parseInt(searchParams.sets) 
      : 3;
      
  const reps = 
    typeof searchParams.reps === &apos;string&apos; && !isNaN(parseInt(searchParams.reps)) 
      ? parseInt(searchParams.reps) 
      : 10;

  return (
    <Suspense fallback={<div>Loading...</div>}>
      <WorkoutClient exercise={exercise} sets={sets} reps={reps} />
    </Suspense>
  );
} 