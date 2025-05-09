// Define API URLs with fallbacks
const BACKEND_URLS = [
  "http://localhost:8002",
  "http://127.0.0.1:8002",
  window.location.origin + "/api/backend" // Proxy fallback
]

// Helper function to try multiple URLs until one works
async function tryFetch(path: string, options: RequestInit): Promise<Response> {
  let lastError;
  
  // Try each base URL
  for (const baseUrl of BACKEND_URLS) {
    try {
      console.log(`Trying to fetch from: ${baseUrl}${path}`);
      const response = await fetch(`${baseUrl}${path}`, options);
      if (response.ok || response.status !== 0) { // Status 0 means network error
        console.log(`Successfully connected to: ${baseUrl}`);
        return response;
      }
    } catch (error) {
      console.warn(`Failed to connect to ${baseUrl}:`, error);
      lastError = error;
    }
  }
  
  // If all URLs failed, throw the last error
  throw lastError || new Error("Failed to connect to any backend URL");
}

export type AuthResult = {
  success: boolean
  error?: string
  accessToken?: string
}

export async function verifyEmail(email: string, code: string): Promise<AuthResult> {
  try {
    console.log('Verifying email:', email, 'with code:', code);
    
    // Try to connect to the backend
    const response = await tryFetch("/verify-email", {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        email,
        code,
      }),
      credentials: 'include', // Allow cookies to be sent/received
    });

    if (!response.ok) {
      const error = await response.json();
      console.error('Verification failed:', error);
      return {
        success: false,
        error: error.detail || "Verification failed",
      };
    }

    const result = await response.json();
    console.log('Verification successful:', result);
    
    // Store JWT token in localStorage - use proper field name based on API response
    const accessToken = result.access_token || result.accessToken;
    
    if (accessToken) {
      console.log('Access token received, storing credentials');
      
      // Store token in localStorage
      localStorage.setItem('access_token', accessToken);
      
      // Set authentication flag
      localStorage.setItem('auth', 'true');

      // Set user email for reference
      localStorage.setItem('user_email', email);
      
      // Set cookie directly as well for redundancy
      document.cookie = `auth-status=authenticated; path=/; max-age=${60 * 60 * 24 * 7}`; // 7 days
      document.cookie = `user-authenticated=true; path=/; max-age=${60 * 60 * 24 * 7}`; // 7 days
      
      // Return the token so it can be used for setting cookies on server side
      return { 
        success: true,
        accessToken: accessToken
      };
    }
    
    return { success: true };
  } catch (error) {
    console.error("Verification error:", error);
    return {
      success: false,
      error: "An error occurred during verification. Please ensure the backend server is running.",
    };
  }
}

export async function resendVerification(email: string): Promise<AuthResult> {
  try {
    console.log('Resending verification code to:', email);
    
    const response = await tryFetch("/resend-verification", {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ email }),
      credentials: 'include', // Allow cookies to be sent/received
    });

    if (!response.ok) {
      const error = await response.json();
      console.error('Resend verification failed:', error);
      return {
        success: false,
        error: error.detail || "Failed to resend verification code",
      };
    }

    const result = await response.json();
    console.log('Resend verification successful:', result);
    return { success: true };
  } catch (error) {
    console.error("Resend verification error:", error);
    return {
      success: false,
      error: "An error occurred while resending the verification code. Please ensure the backend server is running.",
    };
  }
} 