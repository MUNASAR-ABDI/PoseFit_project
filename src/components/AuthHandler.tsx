"use client";

import { useClerk } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { createContext, useContext, useState, useEffect } from "react";

type AuthContextType = {
  forceSignOut: () => Promise<void>;
  isSignedOut: boolean;
};

const AuthContext = createContext<AuthContextType | null>(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};

export function AuthHandler({ children }: { children: React.ReactNode }) {
  const { signOut } = useClerk();
  const router = useRouter();
  const [isSignedOut, setIsSignedOut] = useState(false);

  const forceSignOut = async () => {
    setIsSignedOut(true);
    // Force a hard reload after sign out
    try {
      await signOut();
      window.location.href = "/";
    } catch (error) {
      console.error("Sign out error:", error);
      setIsSignedOut(false);
    }
  };

  return (
    <AuthContext.Provider value={{ forceSignOut, isSignedOut }}>
      {children}
    </AuthContext.Provider>
  );
} 