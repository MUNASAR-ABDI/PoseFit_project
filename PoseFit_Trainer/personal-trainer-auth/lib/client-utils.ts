"use client";

/**
 * Client-side utilities for authentication and session management
 */

/**
 * Check if the user is authenticated by checking cookies, localStorage, and other indicators
 */
export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') {
    return false;
  }

  try {
    // Check for auth cookies
    const hasAuthCookie = document.cookie.split(';').some(cookie => 
      cookie.trim().startsWith('auth-status=') ||
      cookie.trim().startsWith('user-authenticated=') ||
      cookie.trim().startsWith('session=')
    );
    
    // Check localStorage
    const hasLocalStorageAuth = localStorage.getItem('auth') === 'true';
    
    // Check for access token
    const hasAccessToken = !!localStorage.getItem('access_token');
    
    return hasAuthCookie || hasLocalStorageAuth || hasAccessToken;
  } catch (e) {
    console.error('Error checking auth state:', e);
    return false;
  }
}

/**
 * Set authentication state in client storage
 */
export function setAuthenticated(value: boolean = true): void {
  if (typeof window === 'undefined') {
    return;
  }
  
  try {
    if (value) {
      localStorage.setItem('auth', 'true');
      
      // Also set a client-accessible cookie as a backup
      document.cookie = `auth-status=authenticated; path=/; max-age=${60 * 60 * 24 * 7}`; // 7 days
      document.cookie = `user-authenticated=true; path=/; max-age=${60 * 60 * 24 * 7}`; // 7 days
    } else {
      localStorage.removeItem('auth');
      localStorage.removeItem('access_token');
      
      // Clear auth cookies
      document.cookie = 'auth-status=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
      document.cookie = 'user-authenticated=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
    }
  } catch (e) {
    console.error('Error setting auth state:', e);
  }
}

/**
 * Force a complete logout and redirect to login page
 * Enhanced to ensure consistent behavior across the application
 */
export function logout(): void {
  if (typeof window === 'undefined') {
    return;
  }
  
  try {
    // Clear client-side auth state
    setAuthenticated(false);
    
    // Clear all cookies
    document.cookie.split(";").forEach(function(c) {
      document.cookie = c.trim().split("=")[0] + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    });
    
    // Clear localStorage and sessionStorage
    try {
      localStorage.removeItem('auth');
      localStorage.removeItem('token');
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      localStorage.removeItem('workoutHistory');
      localStorage.removeItem('lastWorkoutResults');
      sessionStorage.clear();
      localStorage.clear();
    } catch (e) {
      console.error('Error clearing storage:', e);
    }
    
    // Redirect to the logout endpoint which will clear server-side cookies
    window.location.href = '/api/auth/logout';
  } catch (e) {
    console.error('Error during logout:', e);
    
    // Fallback to direct redirect
    window.location.href = '/login';
  }
} 