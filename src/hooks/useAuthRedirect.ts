"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

// Global auth state to prevent double checking
let globalAuthChecked = false;
let globalIsAuthenticated = false;

/**
 * Custom hook to handle authentication redirects
 * 
 * @param {boolean} requireAuth - Whether the current page requires authentication
 * @param {string} redirectTo - Where to redirect if auth requirement is not met
 * @returns {boolean} isLoading - Whether auth check is in progress
 */
export function useAuthRedirect(requireAuth: boolean = false, redirectTo: string = "/") {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function checkAuth() {
      // If we already did the auth check globally, don't do it again
      if (globalAuthChecked) {
        // We already know if the user is authenticated
        const isAuthenticated = globalIsAuthenticated;
        
        // Quick redirect if needed
        if (requireAuth && !isAuthenticated) {
          router.push("/login");
        } else if (!requireAuth && isAuthenticated && redirectTo !== "/") {
          router.push(redirectTo);
        }
        
        // Always finish loading
        setIsLoading(false);
        return;
      }
      
      // Check if the user is authenticated using session cookie
      const hasSession = document.cookie.split(';').some(c => {
        return c.trim().startsWith('session=');
      });

      // Check local storage for auth data as backup
      const hasAuthData = !!localStorage.getItem('auth');
      
      // Check Clerk authentication if available
      let hasClerkAuth = false;
      try {
        if (window.Clerk && window.Clerk.isAuthenticated) {
          hasClerkAuth = true;
        }
      } catch (e) {
        console.error("Error checking Clerk auth:", e);
      }

      const isAuthenticated = hasSession || hasAuthData || hasClerkAuth;
      
      // Store globally to avoid multiple checks
      globalAuthChecked = true;
      globalIsAuthenticated = isAuthenticated;

      // Redirect logic
      if (requireAuth && !isAuthenticated) {
        // If auth is required but user is not authenticated
        router.push("/login");
      } else if (!requireAuth && isAuthenticated && redirectTo !== "/") {
        // If user is authenticated but on a non-auth page (like login)
        router.push(redirectTo);
      }

      // Store authentication state in localStorage for persistence
      if (isAuthenticated) {
        localStorage.setItem('auth', 'true');
      }

      setIsLoading(false);
    }

    checkAuth();
  }, [requireAuth, redirectTo, router]);

  return isLoading;
} 