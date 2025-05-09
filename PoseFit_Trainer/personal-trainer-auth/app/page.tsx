'use client';

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ArrowLeft, ArrowRight } from "lucide-react"
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { logout } from "@/lib/client-utils";

export default function Home() {
  const router = useRouter();

  // Force logout if on home page by clearing all auth cookies
  useEffect(() => {
    // Use the centralized logout utility function for cookie and storage cleanup
    // but don't redirect since we're already on the home page
    if (typeof window !== &apos;undefined&apos;) {
      // Clear any existing session cookies client-side
      document.cookie = "session=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
      document.cookie = "user-authenticated=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
      document.cookie = "auth-status=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
      document.cookie = "next-auth.session-token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
      document.cookie = "__Secure-next-auth.session-token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
      
      // Also clear session storage
      sessionStorage.clear();
      localStorage.removeItem(&apos;auth&apos;);
      localStorage.removeItem(&apos;token&apos;);
      localStorage.removeItem(&apos;user&apos;);
      localStorage.removeItem(&apos;workoutHistory&apos;);
      localStorage.removeItem(&apos;lastWorkoutResults&apos;);
    }
  }, []);

  // Handle back to PoseFit button click
  const handleBackToPoseFit = () => {
    // Since we're already logged out on this page, just redirect
    window.location.href = process.env.NEXT_PUBLIC_LANDING_URL || "http://localhost:4000";
  };

  return (
    <div className="flex flex-col items-center min-h-screen px-4 py-12 bg-gradient-to-b from-gray-50 to-gray-100">
      {/* Back to PoseFit button */}
      <div className="w-full max-w-5xl flex justify-start mb-8">
        <Button 
          variant="outline" 
          size="sm" 
          className="flex items-center gap-1"
          onClick={handleBackToPoseFit}
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to PoseFit</span>
        </Button>
      </div>
      
      <div className="w-full max-w-4xl text-center space-y-8">
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">Your PoseFit-Trainer</h1>
        <p className="max-w-2xl mx-auto text-xl text-gray-600">
          Personalized workouts, real-time feedback, and progress tracking - all powered by AI.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button asChild size="lg" className="gap-2">
            <Link href="/register">
              Get Started <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link href="/login">Sign In</Link>
          </Button>
        </div>
      </div>

      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-5xl">
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <h3 className="text-lg font-medium mb-2">Smart Workout Planning</h3>
          <p className="text-gray-600">Personalized workouts based on your fitness level that adapt as you improve.</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <h3 className="text-lg font-medium mb-2">Progress Tracking</h3>
          <p className="text-gray-600">Visualize your progress over time with detailed metrics and insights.</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <h3 className="text-lg font-medium mb-2">Real-time Feedback</h3>
          <p className="text-gray-600">Get immediate feedback on your form and performance during workouts.</p>
        </div>
      </div>
    </div>
  )
}
