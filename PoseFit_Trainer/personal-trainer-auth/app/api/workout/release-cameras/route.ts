import { NextResponse } from 'next/server';
import { createErrorResponse } from '@/lib/api-utils';
import { apiRequest } from '@/lib/server-utils';

export async function POST() {
  try {
    // Call the backend endpoint to release all cameras
    await apiRequest('/release-all-cameras', {
      method: &apos;POST&apos;
    });
    
    return NextResponse.json({ 
      success: true,
      message: 'All cameras released successfully'
    });
  } catch (error) {
    console.error('Error releasing cameras:', error);
    return createErrorResponse(error);
  }
} 