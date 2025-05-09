import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const frame = formData.get('frame');
    const session_id = formData.get('session_id');

    if (!frame || !session_id) {
      return NextResponse.json(
        { error: 'Missing frame or session_id' },
        { status: 400 }
      );
    }

    // Create a new FormData object to send to the backend
    const backendFormData = new FormData();
    backendFormData.append('frame', frame);
    backendFormData.append('session_id', session_id as string);

    // Get the backend URL from environment variable or use default
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8002';

    // Send the frame to the backend for processing
    const response = await fetch(`${backendUrl}/process-frame`, {
      method: 'POST',
      body: backendFormData,
      credentials: 'include',
    });

    if (!response.ok) {
      const error = await response.text();
      console.error('Backend error:', error);
      return NextResponse.json(
        { error: error },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('Error processing frame:', error);
    return NextResponse.json(
      { error: 'Failed to process frame' },
      { status: 500 }
    );
  }
} 