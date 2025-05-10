"use server";

import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { BACKEND_URL, APP_URL } from "../../../../lib/config";

export async function GET() {
  // Use our config URL with safe default
  const API_BASE_URL = BACKEND_URL;
  
  // Attempt to call backend logout endpoint
  try {
    const sessionCookie = cookies().get("session");
    if (sessionCookie?.value) {
      await fetch(`${API_BASE_URL}/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${sessionCookie.value}`,
          'Content-Type': 'application/json'
        }
      }).catch(err => console.error("Error calling logout API:", err));
    }
  } catch (e) {
    console.error("Error during backend logout:", e);
  }
  
  // Delete all cookies that could be related to auth
  const cookieStore = cookies();
  cookieStore.getAll().forEach(cookie => {
    cookieStore.delete(cookie.name);
  });
  
  // Specific cookies we know about
  cookieStore.delete("session");
  cookieStore.delete("next-auth.session-token");
  cookieStore.delete("__Secure-next-auth.session-token");
  
  // Use our config APP_URL which has a safe default
  // Ensure we're creating a proper URL object with an absolute URL
  const redirectUrl = new URL(`/?fresh=true&t=${Date.now()}`, APP_URL);
  
  // Redirect to home page with cache control headers to prevent caching
  const response = NextResponse.redirect(redirectUrl);
  
  // Add cache-control headers to prevent browser caching
  response.headers.set("Cache-Control", "no-store, no-cache, must-revalidate, proxy-revalidate");
  response.headers.set("Pragma", "no-cache");
  response.headers.set("Expires", "0");
  
  return response;
} 