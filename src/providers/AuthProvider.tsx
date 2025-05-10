"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useUser, useClerk } from "@clerk/nextjs";
import { useRouter } from "next/navigation";

type AuthContextType = {
  isAuthenticated: boolean;
  isLoading: boolean;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { isSignedIn, isLoaded } = useUser();
  const clerk = useClerk();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    setIsLoading(!isLoaded);
    setIsAuthenticated(!!isSignedIn);
  }, [isLoaded, isSignedIn]);

  const handleSignOut = async () => {
    try {
      setIsAuthenticated(false); // Immediately update UI
      setIsLoading(true); // Show loading state
      await clerk.signOut();
      router.push("/");
      router.refresh();
    } catch (error) {
      console.error("Sign out error:", error);
      setIsAuthenticated(true); // Revert on error
    } finally {
      setIsLoading(false);
    }
  };

  // Force update auth state when clerk session changes
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        setIsAuthenticated(!!isSignedIn);
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    window.addEventListener("focus", handleVisibilityChange);

    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      window.removeEventListener("focus", handleVisibilityChange);
    };
  }, [isSignedIn]);

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        isLoading,
        signOut: handleSignOut,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}; 