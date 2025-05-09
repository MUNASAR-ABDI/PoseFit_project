"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { clearInvalidSession } from "@/lib/actions/auth";

interface SessionManagerProps {
  user: unknown | null;
  hasSession: boolean;
}

export function SessionManager({ user, hasSession }: SessionManagerProps) {
  const router = useRouter();
  const pathname = usePathname();
  
  useEffect(() => {
    // If we have a session cookie but no user data, the session might be invalid
    if (hasSession && !user && pathname !== '/login' && !pathname.startsWith('/register')) {
      console.log("Detected potentially invalid session, cleaning up...");
      
      // Clear the invalid session using the server action
      clearInvalidSession().then(() => {
        // Only redirect to login if we're on a protected page
        if (!pathname.startsWith('/login') && 
            !pathname.startsWith('/register') && 
            pathname !== '/' && 
            pathname !== '/home') {
          router.push('/login');
        } else {
          // Just refresh the current page to update UI state
          router.refresh();
        }
      });
    }
  }, [user, hasSession, pathname, router]);

  // This component doesn't render anything visible
  return null;
} 