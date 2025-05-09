import { NextResponse } from 'next/server';
import { createErrorResponse } from '@/lib/api-utils';
import { apiRequest } from '@/lib/server-utils';

export async function POST(
  request: Request,
  { params }: { params: { sessionId: string } }
) {
  try {
    await apiRequest('/pause-workout', {
      method: &apos;POST&apos;,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `session_id=${params.sessionId}`
    });
    return NextResponse.json({ success: true });
  } catch (error) {
    return createErrorResponse(error);
  }
} 