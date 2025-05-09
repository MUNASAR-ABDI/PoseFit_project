import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '../../auth/[...nextauth]/route';
import { prisma } from '@/lib/prisma';

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    
    if (!session?.user?.email) {
      return NextResponse.json({ error: &apos;Unauthorized&apos; }, { status: 401 });
    }

    const data = await request.json();
    const { exercise, repCount, setCount, completed } = data;

    // Get the user's active workout session
    const user = await prisma.user.findUnique({
      where: { email: session.user.email },
      include: { activeWorkoutSession: true }
    });

    if (!user?.activeWorkoutSession) {
      return NextResponse.json({ error: 'No active workout session' }, { status: 400 });
    }

    // If this is a workout completion request
    if (completed) {
      await prisma.workoutSession.update({
        where: { id: user.activeWorkoutSession.id },
        data: {
          completed: true,
          completedAt: new Date(),
        }
      });

      // Remove the active workout session reference
      await prisma.user.update({
        where: { id: user.id },
        data: { activeWorkoutSessionId: null }
      });

      return NextResponse.json({ message: 'Workout completed successfully' });
    }

    // Otherwise, this is a rep completion request
    await prisma.workoutSession.update({
      where: { id: user.activeWorkoutSession.id },
      data: {
        currentSet: setCount,
        currentRep: repCount,
        lastUpdated: new Date()
      }
    });

    return NextResponse.json({ 
      message: 'Rep recorded successfully',
      currentSet: setCount,
      currentRep: repCount
    });
  } catch (error) {
    console.error('Error in workout completion:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
} 