"use client";

import { SignInButton, SignUpButton, useUser } from "@clerk/nextjs";
import { ArrowLeft, DumbbellIcon, HomeIcon, UserIcon, ZapIcon } from "lucide-react";
import Link from "next/link";
import { Button } from "./ui/button";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { navigateToLandingPage, performFullLogout } from "@/lib/auth";

const Navbar = () => {
  const { isLoaded, isSignedIn } = useUser();
  const router = useRouter();

  // Initialize auth state
  useEffect(() => {
    if (isLoaded) {
      const authOnly = document.querySelectorAll('.auth-only');
      const authHidden = document.querySelectorAll('.auth-hidden');
      
      if (isSignedIn) {
        // User is signed in - show auth-only, hide auth-hidden
        authOnly.forEach(el => {
          if (el instanceof HTMLElement) {
            el.style.display = 'flex';
          }
        });
        
        authHidden.forEach(el => {
          if (el instanceof HTMLElement) {
            el.style.display = 'none';
          }
        });
      } else {
        // User is not signed in - hide auth-only, show auth-hidden
        authOnly.forEach(el => {
          if (el instanceof HTMLElement) {
            el.style.display = 'none';
          }
        });
        
        authHidden.forEach(el => {
          if (el instanceof HTMLElement) {
            el.style.display = 'flex';
          }
        });
      }
    }
  }, [isLoaded, isSignedIn]);

  // Handle sign out with our improved approach
  const handleSignOut = (e) => {
    e.preventDefault();
    performFullLogout();
  };

  // Handle Home button click - also log out if signed in
  const handleHomeClick = (e) => {
    if (isSignedIn) {
      e.preventDefault();
      performFullLogout();
    }
    // If not signed in, just follow the link normally
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-background/60 backdrop-blur-md border-b border-border py-3">
      <div className="container mx-auto flex items-center justify-between">
        {/* LOGO AND BACK BUTTON */}
        <div className="flex items-center gap-4">
          {/* Go Back button */}
          <Button 
            variant="ghost" 
            size="sm" 
            className="flex items-center gap-1 mr-2 hover:bg-primary/10"
            onClick={() => navigateToLandingPage(isSignedIn)}
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back to PoseFit</span>
          </Button>
          
          <Link 
            href="/" 
            className="flex items-center gap-2"
            onClick={isSignedIn ? handleHomeClick : undefined}
          >
            <div className="p-1 bg-primary/10 rounded">
              <ZapIcon className="w-4 h-4 text-primary" />
            </div>
            <span className="text-xl font-bold font-mono">
              Pose<span className="text-primary">Fit</span>.assistant
            </span>
          </Link>
        </div>

        {/* NAVIGATION */}
        <nav className="flex items-center gap-5">
          {/* Authenticated UI */}
          <div className="flex items-center gap-5 auth-only" style={{ display: isLoaded && isSignedIn ? 'flex' : 'none' }}>
            <a
              href="/"
              className="flex items-center gap-1.5 text-sm hover:text-primary transition-colors"
              onClick={handleHomeClick}
            >
              <HomeIcon size={16} />
              <span>Home</span>
            </a>

            <Link
              href="/generate-program"
              className="flex items-center gap-1.5 text-sm hover:text-primary transition-colors"
            >
              <DumbbellIcon size={16} />
              <span>Generate</span>
            </Link>

            <Link
              href="/profile"
              className="flex items-center gap-1.5 text-sm hover:text-primary transition-colors"
            >
              <UserIcon size={16} />
              <span>Profile</span>
            </Link>
            <Button
              asChild
              variant="outline"
              className="ml-2 border-primary/50 text-primary hover:text-white hover:bg-primary/10"
            >
              <Link href="/generate-program">Get Started</Link>
            </Button>
            
            {/* Improved sign-out button */}
            <button 
              className="inline-flex items-center justify-center text-red-500 hover:text-red-600 hover:bg-red-500/10 text-sm font-medium px-4 py-2 rounded-md"
              onClick={handleSignOut}
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
              Sign Out
            </button>
          </div>

          {/* Unauthenticated UI */}
          <div className="flex items-center gap-5 auth-hidden" style={{ display: isLoaded && !isSignedIn ? 'flex' : 'none' }}>
            <SignInButton mode="modal">
              <Button
                variant={"outline"}
                className="border-primary/50 text-primary hover:text-white hover:bg-primary/10"
              >
                Sign In
              </Button>
            </SignInButton>

            <SignUpButton mode="modal">
              <Button className="bg-primary text-primary-foreground hover:bg-primary/90">
                Sign Up
              </Button>
            </SignUpButton>
          </div>
        </nav>
      </div>
    </header>
  );
};

export default Navbar;
