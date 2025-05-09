import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8002';

export async function POST(request: Request) {
  try {
    // Get auth token from cookies
    const sessionToken = cookies().get(&apos;session&apos;);

    if (!sessionToken?.value) {
      console.log('No session token found');
      return NextResponse.json({ error: 'Authentication required' }, { status: 401 });
    }

    // Parse request body
    const body = await request.json();
    const { exercise, sets, reps } = body;

    if (!exercise || !sets || !reps) {
      return NextResponse.json({ error: 'Missing required parameters' }, { status: 400 });
    }

    console.log('Starting workout session:', { exercise, sets, reps, backendUrl: BACKEND_URL });

    // Make request to backend
    const backendResponse = await fetch(`${BACKEND_URL}/start-workout`, {
      method: &apos;POST&apos;,
      headers: {
        'Content-Type': 'application/json',
        &apos;Authorization&apos;: `Bearer ${sessionToken.value}`
      },
      body: JSON.stringify({ exercise, sets, reps })
    });

    // Log response details for debugging
    console.log('Backend response status:', backendResponse.status);
    console.log('Backend response headers:', Object.fromEntries(backendResponse.headers.entries()));
    const responseText = await backendResponse.text();
    console.log('Backend raw response:', responseText);

    if (!backendResponse.ok) {
      console.log('Backend server error:', responseText);
      return NextResponse.json(
        { error: responseText || 'Failed to start workout session' },
        { status: backendResponse.status }
      );
    }

    // Parse response if it's JSON
    let data;
    try {
      data = JSON.parse(responseText);
    } catch (e) {
      console.log('Error parsing backend response:', e);
      return NextResponse.json(
        { error: 'Invalid response from workout server' },
        { status: 500 }
      );
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in workout start:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
} 