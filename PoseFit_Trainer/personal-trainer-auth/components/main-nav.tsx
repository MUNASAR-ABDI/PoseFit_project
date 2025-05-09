"use client"

import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Dumbbell, Menu, X } from "lucide-react"
import { useState } from "react"
import { cn } from "@/lib/utils"
import type { User } from '@/lib/types/user';
import { logout } from "@/lib/client-utils"
import { ModeToggle } from "@/components/ui/theme-toggle"

export function MainNav({ user }: { user?: User | null }) {
  const pathname = usePathname()
  const router = useRouter()
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  // IMPORTANT: Special case for the home page - always show Sign In/Sign Up
  const isHomePage = pathname === "/";

  // Enhanced check for user authentication - verify user exists and has expected properties
  const isLoggedIn = !isHomePage && !!user && 
                    (typeof user === 'object') && 
                    ((user?.email && user.email.length > 0) || 
                     (user?.first_name && user.first_name.length > 0));
  
  // Ensure proper display of auth elements based on path
  // Home page always shows non-auth UI
  const showAuthUI = isLoggedIn;

  // Function to handle Home link click
  const handleHomeClick = (e: React.MouseEvent) => {
    if (isLoggedIn) {
      e.preventDefault()
      // If logged in, log out before going home
      logout()
    }
    // If not logged in, just follow the link normally
  }

  // Handle Back to PoseFit button click - always log out if logged in
  const handleBackToPoseFit = () => {
    if (isLoggedIn) {
      // If logged in, log out first then redirect
      fetch('/api/auth/logout')
        .then(() => {
          // Clear cookies client-side as well
          document.cookie = "session=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
          // Redirect to landing page
          window.location.href = process.env.NEXT_PUBLIC_LANDING_URL || "http://localhost:4000";
        })
        .catch(() => {
          // On error, just try redirecting
          window.location.href = process.env.NEXT_PUBLIC_LANDING_URL || "http://localhost:4000";
        });
    } else {
      // If not logged in, just redirect
      window.location.href = process.env.NEXT_PUBLIC_LANDING_URL || "http://localhost:4000";
    }
  };

  const routes = [
    {
      href: "/",
      label: "Home",
      active: pathname === "/",
      public: true,
      onClick: handleHomeClick
    },
    {
      href: "/dashboard",
      label: "Dashboard",
      active: pathname === "/dashboard",
      public: false,
    },
    {
      href: "/workouts",
      label: "Workouts",
      active: pathname.includes("/workouts"),
      public: false,
    },
    {
      href: "/profile",
      label: "Profile",
      active: pathname.includes("/profile"),
      public: false,
    },
  ]

  const filteredRoutes = routes.filter((route) => (isLoggedIn ? true : route.public))

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-4">
          {/* Go Back to PoseFit button */}
          <Button 
            variant="ghost" 
            size="sm" 
            className="flex items-center gap-1 mr-2"
            onClick={handleBackToPoseFit}
          >
            <ArrowLeft className="h-4 w-4" />
            <span>PoseFit</span>
          </Button>
          
          <Link 
            href="/" 
            className="flex items-center gap-2"
            onClick={isLoggedIn ? handleHomeClick : undefined}
          >
            <Dumbbell className="h-6 w-6" />
            <span className="font-bold text-xl hidden md:inline-block">PoseFit-Trainer</span>
          </Link>
        </div>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-6">
          {filteredRoutes.map((route) => (
            <Link
              key={route.href}
              href={route.href}
              className={cn(
                "text-sm font-medium transition-colors hover:text-primary",
                route.active ? "text-primary" : "text-muted-foreground",
              )}
              onClick={route.onClick}
            >
              {route.label}
            </Link>
          ))}

          {/* Theme Toggle */}
          <ModeToggle />

          {showAuthUI ? (
            <div className="flex items-center gap-2">
              <span className="font-medium text-sm text-primary">{user?.first_name || user?.email}</span>
              <Button 
                onClick={() => {
                  // Client-side logout that ensures redirect to home page
                  fetch('/api/auth/logout')
                    .then(() => {
                      // Clear cookies client-side as well
                      document.cookie = "session=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
                      // Redirect to home
                      window.location.href = "/?loggedout=true";
                    })
                    .catch(() => {
                      // Fallback redirect
                      window.location.href = "/";
                    });
                }}
                variant="outline" 
                size="sm"
              >
                Sign Out
              </Button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Button asChild variant="ghost" size="sm">
                <Link href="/login">Sign In</Link>
              </Button>
              <Button asChild size="sm">
                <Link href="/register">Sign Up</Link>
              </Button>
            </div>
          )}
        </nav>

        {/* Mobile Menu Button */}
        <div className="md:hidden flex items-center gap-2">
          <ModeToggle />
          <Button variant="ghost" size="icon" onClick={() => setIsMenuOpen(!isMenuOpen)}>
            {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </Button>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isMenuOpen && (
        <div className="md:hidden border-t">
          <div className="container py-4 flex flex-col gap-4">
            {/* Go Back to PoseFit button for mobile */}
            <Button 
              variant="outline" 
              size="sm" 
              className="flex items-center justify-center gap-1 w-full"
              onClick={handleBackToPoseFit}
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back to PoseFit</span>
            </Button>
          
            {filteredRoutes.map((route) => (
              <Link
                key={route.href}
                href={route.href}
                className={cn(
                  "text-sm font-medium transition-colors hover:text-primary p-2",
                  route.active ? "text-primary bg-muted rounded-md" : "text-muted-foreground",
                )}
                onClick={(e) => {
                  setIsMenuOpen(false)
                  if (route.onClick) route.onClick(e)
                }}
              >
                {route.label}
              </Link>
            ))}

            {showAuthUI ? (
              <div className="flex flex-col gap-2 mt-2">
                <span className="font-medium text-sm text-primary">{user?.first_name || user?.email}</span>
                <Button 
                  onClick={() => {
                    // Client-side logout that ensures redirect to home page
                    fetch('/api/auth/logout')
                      .then(() => {
                        // Clear cookies client-side as well
                        document.cookie = "session=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
                        // Redirect to home
                        window.location.href = "/?loggedout=true";
                      })
                      .catch(() => {
                        // Fallback redirect
                        window.location.href = "/";
                      });
                  }}
                  variant="outline" 
                  size="sm"
                >
                  Sign Out
                </Button>
              </div>
            ) : (
              <div className="flex flex-col gap-2 mt-2">
                <Button asChild variant="outline">
                  <Link href="/login">Sign In</Link>
                </Button>
                <Button asChild>
                  <Link href="/register">Sign Up</Link>
                </Button>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  )
}
