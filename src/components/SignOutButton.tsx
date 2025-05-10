"use client";

import { useClerk } from "@clerk/nextjs";
import { LogOutIcon } from "lucide-react";
import { Button } from "./ui/button";
import { useState } from "react";

export default function SignOutButton() {
  const { signOut } = useClerk();
  const [isSigningOut, setIsSigningOut] = useState(false);

  const handleSignOut = async (e: React.MouseEvent) => {
    e.preventDefault();
    
    // Immediately set signing out state
    setIsSigningOut(true);
    
    try {
      // Force immediate reload to sign-in page
      window.location.href = "/sign-in";
      
      // Also trigger the clerk sign-out in the background
      // but don't wait for it since we're already redirecting
      signOut().catch(console.error);
    } catch (error) {
      // Even if there's an error, force a reload
      console.error("Sign out error:", error);
      window.location.href = "/sign-in";
    }
  };

  return (
    <Button
      variant="ghost"
      className="text-red-500 hover:text-red-600 hover:bg-red-500/10"
      onClick={handleSignOut}
      disabled={isSigningOut}
    >
      <LogOutIcon className="w-4 h-4 mr-2" />
      {isSigningOut ? "Signing out..." : "Sign Out"}
    </Button>
  );
} 