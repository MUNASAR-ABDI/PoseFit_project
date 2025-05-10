/**
 * Clear all cookies from the browser
 */
export function clearAllCookies() {
  document.cookie.split(";").forEach(cookie => {
    const [name] = cookie.trim().split("=");
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
  });
}

/**
 * Perform a full logout that ensures complete session cleanup
 * and forces a hard refresh of the application
 * @param redirectUrl Optional URL to redirect to after logout, defaults to home page
 */
export function performFullLogout(redirectUrl?: string) {
  // Clear clerk state first (if it exists)
  try {
    // If using Clerk, try to directly sign out first
    if (window.Clerk) {
      window.Clerk.signOut();
    }
  } catch (e) {
    console.error("Error with Clerk signout:", e);
  }
  
  // Clear all cookies
  clearAllCookies();
  
  // Clear all local storage
  localStorage.clear();
  sessionStorage.clear();
  
  // Clear auth-specific items just to be sure
  localStorage.removeItem('auth');
  localStorage.removeItem('clerk-db');
  localStorage.removeItem('clerk');
  
  // Stop any ongoing requests
  try {
    if (window.stop) {
      window.stop();
    }
  } catch (e) {
    // Ignore errors
  }
  
  // Force a direct location change to specified URL or home page
  if (redirectUrl) {
    window.location.href = redirectUrl;
  } else {
    // Default redirect to home with cache-busting query parameter
    const timestamp = Date.now();
    window.location.href = `/?fresh=true&t=${timestamp}`;
  }
}

/**
 * Navigate to landing page with logout if user is authenticated
 */
export function navigateToLandingPage(isAuthenticated: boolean = false) {
  const landingUrl = process.env.NEXT_PUBLIC_LANDING_URL || "http://localhost:4000";
  
  if (isAuthenticated) {
    // Call performFullLogout with the landing URL as destination
    performFullLogout(landingUrl);
  } else {
    // If not authenticated, just redirect
    window.location.href = landingUrl;
  }
} 