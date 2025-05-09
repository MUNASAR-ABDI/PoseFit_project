"use client"

import { useState, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { AlertCircle, CheckCircle2, Mail, ServerOff } from "lucide-react"
import { verifyEmail, resendVerification } from "@/lib/api"
import { setAuthenticated } from "@/lib/client-utils"

export default function VerifyPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const email = searchParams.get("email") || ""

  const [verificationCode, setVerificationCode] = useState("")
  const [isVerifying, setIsVerifying] = useState(false)
  const [isResending, setIsResending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [isVerified, setIsVerified] = useState(false)
  const [isRedirecting, setIsRedirecting] = useState(false)
  const [connectionError, setConnectionError] = useState(false)

  // Check server connection on page load
  useEffect(() => {
    async function checkConnection() {
      try {
        const response = await fetch('/api/backend/profile', {
          method: &apos;GET&apos;,
          headers: { 'Content-Type': 'application/json' },
        });
        
        if (response.ok || response.status !== 0) {
          setConnectionError(false);
        } else {
          setConnectionError(true);
        }
      } catch (error) {
        console.error("Backend connection check failed:", error);
        setConnectionError(true);
      }
    }
    
    checkConnection();
  }, []);

  async function handleVerify() {
    if (!verificationCode) {
      setError("Please enter the verification code")
      return
    }

    setIsVerifying(true)
    setError(null)

    try {
      const result = await verifyEmail(email, verificationCode)

      if (result.success) {
        setSuccess("Email verified successfully! Redirecting to dashboard...")
        setIsVerified(true)
        setConnectionError(false)
        
        // Set auth state in localStorage
        localStorage.setItem(&apos;auth&apos;, &apos;true&apos;)
        
        // Store email for reference
        localStorage.setItem(&apos;user_email&apos;, email)
        
        // If we got a token back, set it in localStorage and session cookie
        if (result.accessToken) {
          localStorage.setItem(&apos;access_token&apos;, result.accessToken)
          
          try {
            // Make a request to our API route to set the cookie
            const response = await fetch('/api/auth/set-session', {
              method: &apos;POST&apos;,
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ 
                token: result.accessToken,
                email: email // Pass the email to be stored in cookies
              }),
            });
            
            if (!response.ok) {
              console.error("Failed to set session cookie:", await response.text());
            } else {
              console.log("Session cookie set successfully");
              
              // Set a slight delay to ensure cookies are properly set
              setTimeout(() => {
                // Use window.location for a full page navigation to ensure cookies are recognized
                window.location.href = '/dashboard';
              }, 1000);
            }
          } catch (err) {
            console.error("Error setting session cookie:", err);
            // Even if setting cookie fails, try to redirect anyway
            setTimeout(() => {
              window.location.href = '/dashboard';
            }, 1000);
          }
        } else {
          // If no token in result but verification was successful, redirect anyway
          setTimeout(() => {
            window.location.href = '/dashboard';
          }, 1000);
        }
      } else {
        setError(result.error || "Verification failed. Please try again.")
        
        // Check if error message indicates server connection issue
        if (result.error && 
            (result.error.includes("backend server") || 
             result.error.includes("Failed to connect") ||
             result.error.includes("fetch"))) {
          setConnectionError(true);
        }
      }
    } catch (error) {
      setError("An unexpected error occurred. Please try again.")
      setConnectionError(true);
    } finally {
      setIsVerifying(false)
    }
  }

  async function handleResend() {
    setIsResending(true)
    setError(null)
    setSuccess(null)

    try {
      const result = await resendVerification(email)

      if (result.success) {
        setSuccess("Verification email resent successfully!")
        setConnectionError(false)
      } else {
        setError(result.error || "Failed to resend verification email. Please try again.")
        
        // Check if error message indicates server connection issue
        if (result.error && 
            (result.error.includes("backend server") || 
             result.error.includes("Failed to connect") ||
             result.error.includes("fetch"))) {
          setConnectionError(true);
        }
      }
    } catch (error) {
      setError("An unexpected error occurred. Please try again.")
      setConnectionError(true);
    } finally {
      setIsResending(false)
    }
  }
  
  function handleGoToDashboard() {
    setIsRedirecting(true);
    
    // Ensure all auth-related data is set
    setAuthenticated(true);
    
    // Delay redirect to ensure state is properly set
    setTimeout(() => {
      // Force full page load instead of client-side navigation
      window.location.href = '/dashboard';
    }, 500);
  }

  // Allow direct access to dashboard for development when backend is down
  function handleForceDashboard() {
    localStorage.setItem(&apos;auth&apos;, &apos;true&apos;);
    localStorage.setItem(&apos;access_token&apos;, &apos;development_token&apos;);
    document.cookie = `auth-status=authenticated; path=/; max-age=${60 * 60 * 24 * 7}`;
    document.cookie = `user-authenticated=true; path=/; max-age=${60 * 60 * 24 * 7}`;
    
    window.location.href = '/dashboard';
  }

  return (
    <div className="container flex items-center justify-center min-h-[calc(100vh-4rem)] py-12">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <div className="rounded-full bg-primary/10 p-3">
              <Mail className="h-6 w-6 text-primary" />
            </div>
          </div>
          <CardTitle className="text-2xl">Verify your email</CardTitle>
          <CardDescription>
            We've sent a verification code to <span className="font-medium">{email}</span>
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{String(error)}</AlertDescription>
            </Alert>
          )}

          {success && (
            <Alert variant="success" className="bg-green-50 text-green-800 border-green-200">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">{success}</AlertDescription>
            </Alert>
          )}
          
          {connectionError && (
            <Alert className="bg-amber-50 text-amber-800 border-amber-200">
              <ServerOff className="h-4 w-4 text-amber-600" />
              <AlertDescription className="text-amber-800">
                Cannot connect to the backend server. Please ensure it's running at http://localhost:8002.
                {process.env.NODE_ENV === &apos;development&apos; && (
                  <Button 
                    variant="outline"
                    size="sm"
                    className="ml-2 text-amber-800 border-amber-300 hover:bg-amber-100"
                    onClick={handleForceDashboard}
                  >
                    Skip Verification (Dev Only)
                  </Button>
                )}
              </AlertDescription>
            </Alert>
          )}

          {!isVerified && (
            <div className="space-y-2">
              <Label htmlFor="code">Verification Code</Label>
              <Input
                id="code"
                placeholder="Enter the 6-digit code"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}
                maxLength={6}
              />
              <p className="text-sm text-muted-foreground">Enter the verification code sent to your email address.</p>
            </div>
          )}
        </CardContent>
        <CardFooter className="flex flex-col space-y-2">
          {!isVerified && (
            <>
              <Button 
                className="w-full" 
                onClick={handleVerify} 
                disabled={isVerifying || (connectionError && process.env.NODE_ENV !== &apos;development&apos;)}
              >
                {isVerifying ? "Verifying..." : "Verify Email"}
              </Button>
              <div className="flex items-center justify-center w-full">
                <Button 
                  variant="link" 
                  onClick={handleResend} 
                  disabled={isResending || (connectionError && process.env.NODE_ENV !== &apos;development&apos;)}
                >
                  {isResending ? "Sending..." : "Resend verification code"}
                </Button>
              </div>
            </>
          )}

          {isVerified && (
            <Button 
              className="w-full" 
              onClick={handleGoToDashboard} 
              disabled={isRedirecting}
            >
              {isRedirecting ? "Redirecting..." : "Go to Dashboard"}
            </Button>
          )}
        </CardFooter>
      </Card>
    </div>
  )
}
