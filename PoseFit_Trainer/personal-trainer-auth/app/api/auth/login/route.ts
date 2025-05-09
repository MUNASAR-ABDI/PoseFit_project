import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function POST(request: Request) {
  try {
    const { email, password } = await request.json();

    // Basic validation
    if (!email || !password) {
      return NextResponse.json(
        { error: 'Email and password are required' }, 
        { status: 400 }
      );
    }

    // Call your backend /token endpoint
    const response = await fetch('http://localhost:8002/token', {
      method: &apos;POST&apos;,
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ username: email, password }),
    });

    if (!response.ok) {
      let errorMessage = 'Login failed';
      try {
        const error = await response.json();
        errorMessage = error.detail || errorMessage;
      } catch (e) {
        console.error('Error parsing error response:', e);
      }
      return NextResponse.json({ error: errorMessage }, { status: response.status });
    }

    // Process successful response
    const data = await response.json();
    
    // Verify that we actually got a token
    if (!data.access_token) {
      console.error('No access token in response:', data);
      return NextResponse.json(
        { error: 'Authentication server error: No token received' },
        { status: 500 }
      );
    }

    // Set the cookie with the token
    cookies().set({
      name: &apos;session&apos;,
      value: data.access_token,
      httpOnly: true,
      secure: process.env.NODE_ENV === &apos;production&apos;,
      sameSite: &apos;lax&apos;,
      maxAge: 60 * 60 * 24 * 7, // 7 days
      path: '/',
    });

    return NextResponse.json({ 
      success: true,
      message: 'Login successful' 
    });
  } catch (error) {
    console.error('Unexpected error during login:', error);
    return NextResponse.json(
      { error: 'An unexpected error occurred. Please try again.' },
      { status: 500 }
    );
  }
} 