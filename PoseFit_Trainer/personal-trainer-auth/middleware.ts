import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// URLs that can be accessed without authentication
const publicUrls = [
  '/',
  '/login',
  '/register',
  '/api/auth/login',
  '/api/auth/logout',
  '/api/auth/set-session',
  '/api/auth/check-session',
  '/verify',
  '/forgot-password',
  '/reset-password',
]

// URLs that are authentication-related API endpoints
const authApiUrls = [
  '/api/auth',
  '/api/backend',
]

// Function to check if the URL is public
function isPublicUrl(url: string): boolean {
  // Check exact matches
  if (publicUrls.includes(url)) {
    return true
  }
  
  // Check prefixes
  for (const publicUrl of authApiUrls) {
    if (url.startsWith(publicUrl)) {
      return true
    }
  }
  
  // Check special URLs 
  if (url.includes('/verify') || 
      url.includes('/forgot-password') || 
      url.includes('/reset-password') || 
      url.includes('/_next/') || 
      url.includes('/favicon.ico')) {
    return true
  }

  // Static assets
  if (url.includes('.jpg') || 
      url.includes('.png') || 
      url.includes('.css') || 
      url.includes('.js') ||
      url.includes('/images/')) {
    return true
  }
  
  return false
}

export function middleware(request: NextRequest) {
  const response = NextResponse.next()
  
  // Store the current URL in a cookie for server components to access
  const url = request.nextUrl.pathname
  
  // Debug request URL and check for session
  const hasSession = request.cookies.has(&apos;session&apos;)
  
  // Add debugging headers if needed
  if (process.env.NODE_ENV === &apos;development&apos;) {
    response.headers.set('X-Debug-URL', url)
    response.headers.set('X-Has-Session', hasSession ? &apos;true&apos; : &apos;false&apos;)
  }
  
  response.cookies.set('next-url', url, {
    httpOnly: true,
    secure: process.env.NODE_ENV === &apos;production&apos;,
    path: '/',
  })
  
  return response
}

// See: https://nextjs.org/docs/app/building-your-application/routing/middleware
export const config = {
  matcher: [
    /*
     * Match all paths except for:
     * 1. /api routes
     * 2. /_next (Next.js internals)
     * 3. /static (public static files)
     * 4. /_vercel (Vercel internals)
     * 5. All files in the public folder
     */
    '/((?!api|_next|_vercel|static|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)).*)',
  ],
} 