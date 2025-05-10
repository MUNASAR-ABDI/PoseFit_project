"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

/**
 * LogoutAction component that handles logging out a user completely,
 * with client-side redirects and state cleanup
 */
export default function LogoutAction() {
  const router = useRouter();

  useEffect(() => {
    // Clear all cookies
    document.cookie.split(";").forEach(cookie => {
      const [name] = cookie.trim().split("=");
      document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
    });
    
    // Clear localStorage and sessionStorage
    localStorage.clear();
    sessionStorage.clear();
    
    // Perform a hard redirect to home page with cache-busting parameter
    const timestamp = Date.now();
    window.location.href = `/?fresh=true&t=${timestamp}`;
  }, []);

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-background">
      <div className="text-center">
        <p className="mb-2">Signing out...</p>
        <div className="w-8 h-8 border-t-2 border-primary rounded-full animate-spin mx-auto"></div>
      </div>
    </div>
  );
} 