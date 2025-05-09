"use server"

import { revalidatePath } from "next/cache"
import { cookies } from "next/headers"
import { redirect } from "next/navigation"

const API_BASE_URL = "http://localhost:8002"

// Function to check if API is available
async function checkApiAvailability(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/docs`, {
      method: &apos;HEAD&apos;,
    });
    return response.ok;
  } catch (error) {
    return false;
  }
}

// Types for login and register
type LoginData = {
  email: string
  password: string
}

type RegisterData = {
  firstName: string
  lastName: string
  email: string
  gender: string
  age: string
  weight: string
  height: string
  password: string
  fitnessLevel: string
  goals: string
}

type AuthResult = {
  success: boolean
  error?: string
}

// Mock user data for demonstration
const MOCK_USERS = [
  {
    id: "1",
    name: "Demo User",
    email: "demo@example.com",
    password: "password123",
    verified: true,
  },
]

// Mock verification codes
const VERIFICATION_CODES: Record<string, string> = {}

// Login action
export async function login(data: LoginData): Promise<AuthResult> {
  try {
    // Check if API is available
    const isApiAvailable = await checkApiAvailability();
    if (!isApiAvailable) {
      return {
        success: false,
        error: "Unable to connect to server. Please ensure the backend is running.",
      };
    }

    const response = await fetch(`${API_BASE_URL}/token`, {
      method: &apos;POST&apos;,
      headers: { 
        'Content-Type': 'application/x-www-form-urlencoded',
        &apos;Accept&apos;: 'application/json',
      },
      body: new URLSearchParams({
        username: data.email,
        password: data.password,
      }).toString(),
      cache: 'no-store',
    });

    if (!response.ok) {
      let errorMessage = "Invalid email or password";
      try {
        const error = await response.json();
        errorMessage = error.detail || errorMessage;
      } catch {
        // If response is not JSON, use status text
        errorMessage = response.statusText || errorMessage;
      }
      return {
        success: false,
        error: errorMessage,
      };
    }

    const result = await response.json();

    // Set the session cookie with the access token
    cookies().set({
      name: "session",
      value: result.access_token,
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      maxAge: 60 * 60 * 24 * 7, // 1 week
      path: "/",
    });

    revalidatePath("/");
    return { success: true };
  } catch (error) {
    console.error("Login error:", error);
    return {
      success: false,
      error: "An error occurred during login. Please try again.",
    };
  }
}

// Register action
export async function register(data: RegisterData): Promise<AuthResult> {
  try {
    // Check if API is available
    const isApiAvailable = await checkApiAvailability();
    if (!isApiAvailable) {
      return {
        success: false,
        error: "Unable to connect to server. Please ensure the backend is running.",
      };
    }

    // Sanitize email: remove leading/trailing quotes and whitespace
    const cleanEmail = data.email.trim().replace(/^['"]+|['"]+$/g, "");

    const response = await fetch(`${API_BASE_URL}/register`, {
      method: &apos;POST&apos;,
      headers: { 
        'Content-Type': 'application/json',
        &apos;Accept&apos;: 'application/json',
      },
      body: JSON.stringify({
        email: cleanEmail,
        password: data.password,
        first_name: data.firstName,
        last_name: data.lastName,
        age: parseInt(data.age),
        gender: data.gender,
        weight: parseFloat(data.weight),
        height: parseFloat(data.height)
      }),
      cache: 'no-store',
    });

    if (!response.ok) {
      const error = await response.json();
      return {
        success: false,
        error: error.detail || "Registration failed",
      };
    }

    return { success: true };
  } catch (error) {
    console.error("Registration error:", error);
    return {
      success: false,
      error: "Unable to connect to server. Please ensure the backend is running.",
    };
  }
}

// Email verification action
export async function verifyEmail(email: string, code: string): Promise<AuthResult> {
  try {
    console.log('Verifying email:', email, 'with code:', code);
    const response = await fetch(`${API_BASE_URL}/verify-email`, {
      method: &apos;POST&apos;,
      headers: { 
        'Content-Type': 'application/json',
        &apos;Accept&apos;: 'application/json',
      },
      body: JSON.stringify({
        email,
        code,
      }),
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
    return { success: true };
  } catch (error) {
    console.error("Verification error:", error);
    return {
      success: false,
      error: "An error occurred during verification",
    };
  }
}

// Resend verification code
export async function resendVerification(email: string): Promise<AuthResult> {
  try {
    console.log('Resending verification code to:', email);
    // Check if API is available
    const isApiAvailable = await checkApiAvailability();
    if (!isApiAvailable) {
      return {
        success: false,
        error: "Unable to connect to server. Please ensure the backend is running.",
      };
    }

    // Sanitize email: remove leading/trailing quotes and whitespace
    const cleanEmail = email.trim().replace(/^['"]+|['"]+$/g, "");

    const response = await fetch(`${API_BASE_URL}/resend-verification`, {
      method: &apos;POST&apos;,
      headers: { 
        'Content-Type': 'application/json',
        &apos;Accept&apos;: 'application/json',
      },
      body: JSON.stringify({ email: cleanEmail }),
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
      error: "An error occurred while resending the verification code",
    };
  }
}

// Logout action
export async function logout() {
  try {
    // Get the current session token
    const sessionCookie = cookies().get("session");
    if (sessionCookie?.value) {
      // Try to call the backend logout endpoint
      try {
        const response = await fetch(`${API_BASE_URL}/logout`, {
          method: &apos;POST&apos;,
          headers: {
            &apos;Authorization&apos;: `Bearer ${sessionCookie.value}`,
            'Content-Type': 'application/json'
          }
        });
        console.log("Logout API response:", response.status);
      } catch (error) {
        // Don't block the logout flow if the API call fails
        console.error("Error calling logout endpoint:", error);
      }
    }
  } catch (e) {
    console.error("Error during logout process:", e);
  } finally {
    // Always clear cookies and redirect, even if the API call fails
    cookies().delete("session");
    revalidatePath("/");
    // Redirect to login page instead of home
    redirect("/login");
  }
}

// Get current user
export async function getCurrentUser() {
  const cookieStore = cookies();
  const session = cookieStore.get("session");

  if (!session?.value) {
    // Session is not present, no need to log anything
    return null;
  }

  try {
    // Check if the API is available first
    const isApiAvailable = await checkApiAvailability();
    if (!isApiAvailable) {
      // Return a fallback profile if we have a session but API is unreachable
      return {
        email: "tempuser@example.com",
        first_name: "Temporary",
        last_name: "User",
        verified: true,
        // Basic profile data with fallback values
        has_profile: true,
        // Flag indicating this is a fallback profile
        is_fallback: true
      };
    }

    // Make API call to validate the session
    const response = await fetch(`${API_BASE_URL}/profile`, {
      method: &apos;GET&apos;,
      headers: {
        'Content-Type': 'application/json',
        &apos;Authorization&apos;: `Bearer ${session.value}`
      },
      cache: 'no-store'
    });

    if (!response.ok) {
      // 401 is expected when session is invalid, no need to log an error
      if (response.status !== 401) {
        // Only log unexpected error statuses but not in the console
        // You could log these to a server-side logging service if needed
      }
      
      // We'll handle session removal in a separate function
      // or let the user be redirected to login page naturally
      return null;
    }

    const data = await response.json();
    return data || null;
  } catch (error) {
    // Only log unexpected errors, not 401s
    if (error instanceof Error && !error.message.includes(&apos;401&apos;)) {
      // Log to a server-side logging service instead of console
    }
    
    // Avoid direct cookie manipulation here to prevent context errors
    return null;
  }
}

// Create a separate server action for handling session removal
export async function clearInvalidSession() {
  try {
    cookies().delete("session");
    return true;
  } catch (error) {
    return false;
  }
}
