"use client";

import { useEffect } from "react";

/**
 * ForceRefresh component that guarantees a page refresh
 * Uses multiple strategies to ensure browser cache is cleared
 */
export default function ForceRefresh() {
  useEffect(() => {
    // Clear all caches possible in browser
    const clearCaches = async () => {
      // Clear auth state in localStorage and sessionStorage
      try {
        // Clear specific auth-related items first
        localStorage.removeItem('auth');
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        localStorage.removeItem('access_token');
        sessionStorage.removeItem('auth');
        sessionStorage.removeItem('token');
        sessionStorage.removeItem('user');
        
        // Then clear everything
        localStorage.clear();
        sessionStorage.clear();
        
        // Remove any global auth state
        if (typeof window !== 'undefined') {
          if ('globalIsAuthenticated' in window) {
            window.globalIsAuthenticated = false;
          }
        }
      } catch (e) {
        console.error("Error clearing storage:", e);
      }
      
      // Clear cookies - focus on auth-related ones first
      const authCookies = ['session', 'auth', 'token', 'next-auth.session-token', 
                          '__Secure-next-auth.session-token', 'next-auth.csrf-token'];
      
      // Clear specific auth cookies first
      authCookies.forEach(name => {
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
      });
      
      // Then clear all cookies
      document.cookie.split(";").forEach(cookie => {
        const [name] = cookie.trim().split("=");
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
      });
      
      // Attempt to clear caches if available
      if ('caches' in window) {
        try {
          const cacheNames = await caches.keys();
          await Promise.all(cacheNames.map(name => caches.delete(name)));
          console.log("Cache cleared successfully");
        } catch (e) {
          console.error("Error clearing caches:", e);
        }
      }
    };

    // Execute cache clearing
    clearCaches();
    
    // Force the browser to reload the page completely
    const forceReload = () => {
      // Add cache-busting parameter
      const cacheBuster = `?nocache=${Date.now()}`;
      const baseUrl = window.location.href.split('?')[0];
      const newUrl = baseUrl + cacheBuster;
      
      // Try multiple reload strategies
      try {
        // First try: normal reload with cache validation
        window.location.reload(true);
        
        // Second try: change location with cache buster
        setTimeout(() => {
          window.location.href = newUrl;
        }, 100);
        
        // Third try: replace location
        setTimeout(() => {
          window.location.replace(newUrl);
        }, 200);
        
        // Last resort - redirect to login page with cache buster
        setTimeout(() => {
          window.location.href = "/login" + cacheBuster;
        }, 500);
      } catch (e) {
        console.error("Error during reload:", e);
        // Last-ditch effort
        window.location.href = "/login";
      }
    };
    
    // Force reload immediately
    forceReload();
    
    return () => {};
  }, []);
  
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background">
      <div className="text-center">
        <div className="mb-4 text-xl font-bold">Logging you out...</div>
        <div className="text-sm text-muted-foreground mb-4">Please wait while we clear your session data</div>
        <div className="w-12 h-12 border-t-4 border-primary rounded-full animate-spin mx-auto"></div>
      </div>
    </div>
  );
} 