import { NextResponse } from 'next/server';
import { createErrorResponse } from '@/lib/api-utils';
import { apiRequest } from '@/lib/server-utils';

export async function POST(
  request: Request,
  { params }: { params: { sessionId: string } }
) {
  try {
    const response = await apiRequest('/save-and-email-video', {
      method: &apos;POST&apos;,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `session_id=${params.sessionId}`
    });
    
    // Generate a fallback task_id if one isn't provided
    // This ensures our progress tracking works even if the backend doesn't support it yet
    const taskId = response?.task_id || `video-${params.sessionId}-${Date.now()}`;
    
    return NextResponse.json({ 
      success: true,
      task_id: taskId,
      message: response?.message || 'Request submitted successfully'
    });
  } catch (error) {
    return createErrorResponse(error);
  }
} 