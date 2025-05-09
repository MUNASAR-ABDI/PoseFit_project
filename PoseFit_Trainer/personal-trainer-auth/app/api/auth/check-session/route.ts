import { NextRequest, NextResponse } from 'next/server'
import { cookies } from 'next/headers'

export async function GET(request: NextRequest) {
  try {
    // Get session token from cookie or Authorization header
    const cookieStore = cookies()
    const sessionCookie = cookieStore.get(&apos;session&apos;)
    
    // Get from Authorization header as fallback
    const authHeader = request.headers.get(&apos;Authorization&apos;)
    const token = sessionCookie?.value || 
      (authHeader?.startsWith('Bearer ') ? authHeader.substring(7) : null)
    
    if (!token) {
      console.log('check-session: No token found');
      return NextResponse.json(
        { authenticated: false, message: 'No session token found' },
        { status: 401 }
      )
    }
    
    // Validate token by making a request to the backend API
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002'
      console.log(`check-session: Validating token against ${apiUrl}/profile`);
      
      const response = await fetch(`${apiUrl}/profile`, {
        method: &apos;GET&apos;,
        headers: {
          'Content-Type': 'application/json',
          &apos;Authorization&apos;: `Bearer ${token}`
        },
        // Disable cache to ensure fresh responses
        cache: 'no-store'
      })
      
      if (!response.ok) {
        console.log(`check-session: Invalid token response (${response.status})`);
        
        // Try to get more detailed error information
        let errorDetail = '';
        try {
          const errorBody = await response.json();
          errorDetail = JSON.stringify(errorBody);
        } catch (_) {
          errorDetail = 'Could not parse error response';
        }
        
        console.log(`check-session: Error details: ${errorDetail}`);
        
        return NextResponse.json(
          { 
            authenticated: false, 
            message: 'Invalid session',
            status: response.status,
            detail: errorDetail
          },
          { status: 401 }
        )
      }
      
      // Get user data from the response
      const userData = await response.json()
      console.log('check-session: Successfully validated token');
      
      return NextResponse.json({
        authenticated: true,
        user: userData
      })
    } catch (error) {
      console.error('Error validating session:', error)
      return NextResponse.json(
        { authenticated: false, message: 'Error validating session', error: String(error) },
        { status: 500 }
      )
    }
  } catch (error) {
    console.error('Unexpected error in check-session route:', error)
    return NextResponse.json(
      { authenticated: false, message: 'Server error', error: String(error) },
      { status: 500 }
    )
  }
} 