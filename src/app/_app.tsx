"use client";

import { useEffect } from 'react';

/**
 * Root app component to handle global app logic like resets and page refreshes
 */
export default function App({ children }) {
  // Handle page refresh logic
  useEffect(() => {
    // Function to detect if we're in a logout flow
    const checkForLogoutReset = () => {
      const urlParams = new URLSearchParams(window.location.search);
      const isFresh = urlParams.get('fresh') === 'true';
      
      if (isFresh) {
        // Clear auth data
        localStorage.removeItem('auth');
        sessionStorage.clear();
        
        // Clear URL parameters
        const baseUrl = window.location.href.split('?')[0];
        window.history.replaceState(null, '', baseUrl);
        
        // Force reload to completely reset the app state
        window.location.reload(true);
      }
    };
    
    // Check on initial load
    checkForLogoutReset();
    
    // Also listen for navigation events
    const handleNavigation = () => {
      checkForLogoutReset();
    };
    
    window.addEventListener('popstate', handleNavigation);
    
    return () => {
      window.removeEventListener('popstate', handleNavigation);
    };
  }, []);
  
  return children;
} 