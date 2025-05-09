import { NextResponse } from 'next/server';
import { createErrorResponse } from '@/lib/api-utils';
import { apiRequest } from '@/lib/server-utils';

export async function GET(
  request: Request,
  { params }: { params: { taskId: string } }
) {
  try {
    let data;
    try {
      data = await apiRequest(`/task-progress/${params.taskId}`, {
        method: 'GET',
      });
    } catch (error) {
      // Return a fallback response if the API call fails
      return NextResponse.json({
        task_id: params.taskId,
        progress: 5, // Show some progress to give feedback
        status: 'processing',
        message: 'Preparing your video...'
      });
    }

    // Ensure we have valid progress data
    const responseData = {
      task_id: params.taskId,
      progress: Math.max(0, Math.min(100, data?.progress || 5)), // Clamp between 0-100
      status: data?.status || 'processing',
      message: data?.message || 'Processing your workout video...',
      elapsed_seconds: data?.elapsed_seconds || 0
    };

    return NextResponse.json(responseData);
  } catch (error) {
    return createErrorResponse(error);
  }
} 