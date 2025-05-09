import { NextResponse } from 'next/server';
import { BACKEND_URL, createErrorResponse } from '@/lib/api-utils';
import { getAuthToken } from '@/lib/server-utils';

export async function GET(
  request: Request,
  { params }: { params: { sessionId: string } }
) {
  try {
    const token = await getAuthToken();
    
    if (!token) {
      return NextResponse.json({ error: &apos;Unauthorized&apos; }, { status: 401 });
    }

    // Need to handle this one differently as we're returning a streaming response
    const response = await fetch(
      `${BACKEND_URL}/workout-stream/${params.sessionId}`,
      {
        headers: {
          &apos;Authorization&apos;: `Bearer ${token}`
        }
      }
    );

    if (!response.ok) {
      throw new Error('Failed to get workout stream');
    }

    // Return the stream directly
    return new NextResponse(response.body, {
      headers: {
        'Content-Type': 'multipart/x-mixed-replace; boundary=frame'
      }
    });
  } catch (error) {
    return createErrorResponse(error);
  }
} 