"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import ForceRefresh from "@/components/ForceRefresh";
import { useAuthRedirect } from "@/hooks/useAuthRedirect";

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const isForced = searchParams.get("force") === "true";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // Use our custom hook - if user is already authenticated, redirect to dashboard
  const isLoading = useAuthRedirect(false, "/");

  // If redirected from logout with force=true, use ForceRefresh
  if (isForced) {
    return <ForceRefresh />;
  }

  useEffect(() => {
    if (isForced) {
      // Clear all cookies
      document.cookie.split(";").forEach(cookie => {
        const [name] = cookie.trim().split("=");
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
      });
      
      // Clear localStorage
      localStorage.clear();
      sessionStorage.clear();
    }
  }, [isForced]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      // Simulate successful login
      // In a real implementation, this would call your auth API
      document.cookie = `session=authenticated; path=/; max-age=2592000`;  // 30 days
      localStorage.setItem('auth', 'true');
      
      // Set global auth state if window is defined
      if (typeof window !== 'undefined') {
        // If a global auth state variable exists, set it
        if ('globalIsAuthenticated' in window) {
          window.globalIsAuthenticated = true;
        }
      }
      
      // Go directly to home without using router to force a complete page load
      window.location.href = "/";
    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="w-8 h-8 border-t-2 border-primary rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-4">Welcome back</h1>
        <p className="text-muted-foreground mb-8">Sign in to your account to continue</p>
        
        <div className="flex flex-col gap-4 w-full max-w-sm mx-auto">
          <form
            onSubmit={handleSubmit}
            className="space-y-4"
          >
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-left mb-1">
                Email
              </label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded bg-gray-800"
                placeholder="Your email"
              />
            </div>
            
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-left mb-1">
                Password
              </label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded bg-gray-800"
                placeholder="Your password"
              />
            </div>
            
            <button
              type="submit"
              className="w-full py-2 bg-primary text-white rounded"
            >
              Sign In
            </button>
          </form>
          
          <div className="text-sm">
            Don't have an account?{" "}
            <a href="/register" className="text-primary hover:underline">
              Sign up
            </a>
          </div>
        </div>
      </div>
    </div>
  );
} 