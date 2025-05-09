import { RegisterForm } from "@/components/auth/register-form"
import { AuthCard } from "@/components/auth/auth-card"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Home } from "lucide-react"

export default function RegisterPage() {
  return (
    <div className="container flex items-center justify-center min-h-[calc(100vh-4rem)] py-12 relative">
      <div className="absolute top-4 left-4 z-10">
        <Button asChild variant="outline" className="flex items-center gap-2">
          <Link href="/">
            <Home className="h-4 w-4" />
            <span>Return to Home</span>
          </Link>
        </Button>
      </div>
      
      <AuthCard
        title="Create an account"
        description="Sign up to get started with your AI personal trainer"
        footerText="Already have an account?"
        footerLinkText="Sign in"
        footerLinkHref="/login"
      >
        <RegisterForm />
      </AuthCard>
    </div>
  )
}
