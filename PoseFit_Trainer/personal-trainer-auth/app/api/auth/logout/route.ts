import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'

export async function GET() {
  // API endpoint for logout in the backend
  const API_BASE_URL = "http://localhost:8002";
  
  try {
    // Get session token
    const sessionCookie = cookies().get("session");
    
    // Try to call backend logout endpoint if token exists
    if (sessionCookie?.value) {
      try {
        await fetch(`${API_BASE_URL}/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${sessionCookie.value}`,
            'Content-Type': 'application/json'
          }
        });
      } catch (error) {
        console.error("Error calling backend logout endpoint:", error);
        // Continue with logout process even if backend call fails
      }
    }
  } catch (e) {
    console.error("Error during backend logout:", e);
  }
  
  // Delete all auth cookies
  const cookieStore = cookies();
  cookieStore.getAll().forEach(cookie => {
    cookieStore.delete(cookie.name);
  });
  
  // Specifically delete known auth cookies
  cookieStore.delete("session");
  cookieStore.delete("next-auth.session-token");
  cookieStore.delete("__Secure-next-auth.session-token");
  
  // Return HTML that will clear client-side state and redirect
  return new NextResponse(
    `<!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Logging out...</title>
        <script>
          // Clear localStorage and sessionStorage
          try {
            localStorage.removeItem('auth');
            localStorage.removeItem('token');
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            sessionStorage.clear();
            localStorage.clear();
            
            // Clear all cookies
            document.cookie.split(";").forEach(function(c) {
              document.cookie = c.trim().split("=")[0] + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
            });
            
            // Force reload to login page with cache buster
            const cacheBuster = "?t=" + Date.now();
            window.location.href = "/login" + cacheBuster;
          } catch(e) {
            console.error("Logout error:", e);
            // Fallback
            window.location.href = "/login";
          }
        </script>
      </head>
      <body>
        <div style="display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;">
          <div style="text-align:center;">
            <h2>Logging out...</h2>
            <p>Please wait while we clear your session data</p>
            <div style="width:40px;height:40px;border:4px solid #eee;border-top:4px solid #3498db;border-radius:50%;margin:20px auto;animation:spin 1s linear infinite;"></div>
          </div>
        </div>
        <style>
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        </style>
      </body>
    </html>`,
    {
      status: 200,
      headers: {
        "Content-Type": "text/html",
        "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
      }
    }
  );
}
