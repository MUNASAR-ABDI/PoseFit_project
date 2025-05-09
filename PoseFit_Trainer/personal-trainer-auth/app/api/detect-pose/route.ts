import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8002';

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const frame = formData.get(&apos;frame&apos;);
    const exercise = formData.get(&apos;exercise&apos;);

    if (!frame || !(frame instanceof Blob)) {
      return NextResponse.json(
        { error: 'Invalid frame data' },
        { status: 400 }
      );
    }

    // Forward the frame to the Python backend for pose detection
    const backendFormData = new FormData();
    backendFormData.append(&apos;frame&apos;, frame);
    backendFormData.append(&apos;exercise&apos;, exercise as string);

    const response = await fetch(`${BACKEND_URL}/detect-pose`, {
      method: &apos;POST&apos;,
      body: backendFormData,
    });

    if (!response.ok) {
      throw new Error('Backend pose detection failed');
    }

    const data = await response.json();

    // Transform the response to match our frontend's expected format
    const processedData = {
      landmarks: data.landmarks,
      processedImage: data.processed_image,
      performance: {
        repsCompleted: data.performance?.reps_completed || 0,
        currentSet: data.performance?.current_set || 0,
        caloriesBurned: data.performance?.calories_burned || 0,
        timeElapsed: data.performance?.time_elapsed || 0,
        repQuality: data.performance?.rep_quality || 0,
        feedback: data.performance?.feedback || ''
      }
    };

    return NextResponse.json(processedData);
  } catch (error) {
    console.error('Error in pose detection:', error);
    return NextResponse.json(
      { error: 'Failed to process frame' },
      { status: 500 }
    );
  }
} 