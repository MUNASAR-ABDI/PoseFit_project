import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { token, email } = body;
    
    if (!token) {
      return NextResponse.json(
        { error: 'No token provided' },
        { status: 400 }
      );
    }
    
    // Store user email if provided
    const userEmail = email || '';
    
    // Set the session cookie with the token - ensure it's accessible
    cookies().set({
      name: &apos;session&apos;,
      value: token,
      httpOnly: true,
      secure: process.env.NODE_ENV === &apos;production&apos;,
      sameSite: &apos;lax&apos;,
      maxAge: 60 * 60 * 24 * 7, // 7 days
      path: '/',
    });
    
    // Also store auth indicator cookie that is accessible to client-side JS
    cookies().set({
      name: 'auth-status',
      value: &apos;authenticated&apos;,
      secure: process.env.NODE_ENV === &apos;production&apos;,
      sameSite: &apos;lax&apos;,
      maxAge: 60 * 60 * 24 * 7, // 7 days
      path: '/',
    });
    
    // Set additional cookies for redundancy
    cookies().set({
      name: 'user-authenticated',
      value: &apos;true&apos;,
      secure: process.env.NODE_ENV === &apos;production&apos;,
      sameSite: &apos;lax&apos;,
      maxAge: 60 * 60 * 24 * 7, // 7 days
      path: '/',
    });
    
    // Store user email if available
    if (userEmail) {
      cookies().set({
        name: 'user-email',
        value: userEmail,
        secure: process.env.NODE_ENV === &apos;production&apos;,
        sameSite: &apos;lax&apos;,
        maxAge: 60 * 60 * 24 * 7, // 7 days
        path: '/',
      });
    }
    
    // Ensure client has info about cookie being set
    return NextResponse.json({ 
      success: true,
      message: 'Session cookie set successfully',
      // Send back authentication status so client can store it
      authenticated: true,
      email: userEmail || null
    }, {
      headers: {
        'Set-Cookie': `auth-status=authenticated; Path=/; Max-Age=${60 * 60 * 24 * 7}; SameSite=Lax;${process.env.NODE_ENV === &apos;production&apos; ? ' Secure;' : ''}`
      }
    });
  } catch (error) {
    console.error('Error setting session cookie:', error);
    return NextResponse.json(
      { error: 'An error occurred setting the session' },
      { status: 500 }
    );
  }
} 