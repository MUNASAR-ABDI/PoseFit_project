'use client'

import { login } from "@/lib/actions/auth"
import { useRouter, useSearchParams } from "next/navigation"
import { useState, useEffect } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Home } from "lucide-react"

export default function LoginPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [error, setError] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  
  // Check for timestamp parameter which indicates we came from logout
  const timestamp = searchParams.get(&apos;t&apos;)
  const fromLogout = !!timestamp
  
  // Clear client-side state on initial load if coming from logout
  useEffect(() => {
    if (fromLogout) {
      console.log("Login page loaded after logout, clearing state")
      
      // Clear browser storage
      try {
        localStorage.clear()
        sessionStorage.clear()
        
        // Clear any auth-specific cookies again for good measure
        document.cookie.split(";").forEach(function(c) {
          document.cookie = c.trim().split("=")[0] + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;"
        })
      } catch (e) {
        console.error("Error clearing state:", e)
      }
    }
  }, [fromLogout])

  async function handleSubmit(formData: FormData) {
    try {
      setIsLoading(true)
      setError("")
      
      const result = await login({
        email: formData.get("email") as string,
        password: formData.get("password") as string,
      })

      if (result.success) {
        // Check if we have return parameters
        const returnTo = searchParams.get(&apos;returnTo&apos;)
        if (returnTo === '/workouts/camera') {
          // Reconstruct workout parameters
          const params = new URLSearchParams({
            exercise: searchParams.get(&apos;exercise&apos;) || &apos;pushup&apos;,
            sets: searchParams.get(&apos;sets&apos;) || &apos;3&apos;,
            reps: searchParams.get(&apos;reps&apos;) || &apos;10&apos;,
            from: &apos;login&apos;
          });
          // Use a direct navigation approach
          window.location.href = `/workouts/camera?${params.toString()}`
        } else {
          // Use direct navigation to ensure a clean state
          window.location.href = "/dashboard"
        }
      } else {
        setError(result.error || "Login failed")
        setIsLoading(false)
      }
    } catch (error) {
      console.error("Login error:", error)
      setError("An error occurred during login. Please try again.")
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-900 p-4 relative">
      <div className="absolute top-4 left-4 z-10 flex gap-2">
        <Button asChild variant="outline" className="flex items-center gap-2 bg-gray-800 text-white hover:bg-gray-700 border-gray-700">
          <Link href="/">
            <Home className="h-4 w-4" />
            <span>Home</span>
          </Link>
        </Button>
        <Button 
          variant="outline" 
          className="flex items-center gap-2 bg-gray-800 text-white hover:bg-gray-700 border-gray-700"
          onClick={() => {
            // Since we're on the login page, user is likely already logged out
            // Just redirect to the landing page
            window.location.href = process.env.NEXT_PUBLIC_LANDING_URL || "http://localhost:4000";
          }}
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to PoseFit</span>
        </Button>
      </div>
      
      <div className="w-full max-w-md space-y-8 rounded-2xl border border-gray-800 bg-gray-900 p-8 shadow-lg">
        <div>
          <h1 className="text-4xl font-bold text-white">Welcome back</h1>
          <p className="mt-2 text-gray-400">Sign in to your account to continue</p>
        </div>

        {error && (
          <div className="rounded-md bg-red-500 bg-opacity-10 p-3">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        <form action={handleSubmit} className="mt-8 space-y-6">
          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-white">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                className="mt-1 block w-full rounded-lg border border-gray-700 bg-gray-800 px-4 py-2 text-white placeholder-gray-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>

            <div>
              <div className="flex items-center justify-between">
                <label htmlFor="password" className="block text-sm font-medium text-white">
                  Password
                </label>
                <Link href="/forgot-password" className="text-sm text-indigo-400 hover:text-indigo-300">
                  Forgot password?
                </Link>
              </div>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="mt-1 block w-full rounded-lg border border-gray-700 bg-gray-800 px-4 py-2 text-white placeholder-gray-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full rounded-lg bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-70"
          >
            {isLoading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-400">
            Don't have an account?{" "}
            <a href="/register" className="text-indigo-400 hover:text-indigo-300">
              Sign up
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}
