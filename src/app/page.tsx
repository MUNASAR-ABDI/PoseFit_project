"use client";

import TerminalOverlay from "@/components/TerminalOverlay";
import { Button } from "@/components/ui/button";
import UserPrograms from "@/components/UserPrograms";
import { ArrowRightIcon } from "lucide-react";
import Link from "next/link";
import ForceRefresh from "@/components/ForceRefresh";
import { useSearchParams } from "next/navigation";
import { useAuthRedirect } from "@/hooks/useAuthRedirect";
import { useEffect, useState } from "react";

const HomePage = () => {
  const searchParams = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : null;
  const isFresh = searchParams?.get("fresh") === "true";
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  // No redirection needed here, as this page is accessible to everyone
  // but we'll check if the user is authenticated
  const isLoading = useAuthRedirect();
  
  useEffect(() => {
    // Check authentication locally to decide what UI to show
    const hasSession = document.cookie.split(';').some(c => 
      c.trim().startsWith('session=')
    );
    const hasAuthData = typeof window !== 'undefined' && !!localStorage.getItem('auth');
    setIsAuthenticated(hasSession || hasAuthData);
  }, []);

  // Check if we need to force a refresh
  useEffect(() => {
    // Additional guard to ensure page refreshes
    const urlParams = new URLSearchParams(window.location.search);
    const isFreshParam = urlParams.get('fresh') === 'true';
    
    if (isFreshParam) {
      // Clear URL by removing parameters but keep forcing refresh
      const baseUrl = window.location.href.split('?')[0];
      window.history.replaceState(null, '', baseUrl);
      
      // Clear localStorage auth state to force re-login
      localStorage.removeItem('auth');
      
      // Force a reload without parameters after a brief delay
      setTimeout(() => {
        window.location.reload(true);
      }, 100);
    }
  }, []);

  // If redirected from logout with fresh=true, use ForceRefresh
  if (isFresh && typeof window !== 'undefined') {
    return <ForceRefresh />;
  }

  // Show loading state while checking auth
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="w-8 h-8 border-t-2 border-primary rounded-full animate-spin"></div>
      </div>
    );
  }

  // Add this function to force a refresh when needed
  function ForceRefreshScript() {
    // This creates an inline script element that executes immediately
    return (
      <script dangerouslySetInnerHTML={{
        __html: `
          (function() {
            // Check for fresh parameter
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.get('fresh') === 'true') {
              // Clear localStorage items
              localStorage.removeItem('auth');
              localStorage.removeItem('clerk-db');
              
              // Clear URL parameters
              const baseUrl = window.location.href.split('?')[0];
              window.history.replaceState(null, '', baseUrl);
              
              // Force reload after a slight delay
              setTimeout(() => {
                window.location.reload(true);
              }, 50);
            }
          })();
        `
      }} />
    );
  }

  return (
    <>
      <ForceRefreshScript />
      <div className="flex flex-col min-h-screen text-foreground overflow-hidden">
        <section className="relative z-10 py-24 flex-grow">
          <div className="container mx-auto px-4">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center relative">
              {/* CORNER DECARATION */}
              <div className="absolute -top-10 left-0 w-40 h-40 border-l-2 border-t-2" />

              {/* LEFT SIDE CONTENT */}
              <div className="lg:col-span-7 space-y-8 relative">
                <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight">
                  <div>
                    <span className="text-foreground">Transform</span>
                  </div>
                  <div>
                    <span className="text-primary">Your Body</span>
                  </div>
                  <div className="pt-2">
                    <span className="text-foreground">With our</span>
                  </div>
                  <div className="pt-2">
                    <span className="text-foreground">Ai</span>
                    <span className="text-primary"> Assistant</span>
                  </div>
                </h1>

                {/* SEPERATOR LINE */}
                <div className="h-px w-full bg-gradient-to-r from-primary via-secondary to-primary opacity-50"></div>

                <p className="text-xl text-muted-foreground w-2/3">
                  Talk to our AI assistant and get personalized diet plans and workout routines
                  designed just for you
                </p>

                {/* STATS */}
                <div className="flex items-center gap-10 py-6 font-mono">
                  <div className="flex flex-col">
                    <div className="text-2xl text-primary">50+</div>
                    <div className="text-xs uppercase tracking-wider">ACTIVE USERS</div>
                  </div>
                  <div className="h-12 w-px bg-gradient-to-b from-transparent via-border to-transparent"></div>
                  <div className="flex flex-col">
                    <div className="text-2xl text-primary">3min</div>
                    <div className="text-xs uppercase tracking-wider">GENERATION</div>
                  </div>
                  <div className="h-12 w-px bg-gradient-to-b from-transparent via-border to-transparent"></div>
                  <div className="flex flex-col">
                    <div className="text-2xl text-primary">100%</div>
                    <div className="text-xs uppercase tracking-wider">PERSONALIZED</div>
                  </div>
                </div>

                {/* BUTTONS */}
                <div className="flex flex-col sm:flex-row gap-4 pt-6">
                  <Button
                    size="lg"
                    asChild
                    className="overflow-hidden bg-primary text-primary-foreground px-8 py-6 text-lg font-medium"
                  >
                    <Link href={isAuthenticated ? "/generate-program" : "/login"} className="flex items-center font-mono">
                      {isAuthenticated ? "Build Your Program" : "Get Started"}
                      <ArrowRightIcon className="ml-2 size-5" />
                    </Link>
                  </Button>
                  
                  {/* Back to PoseFit Button */}
                  <Button
                    size="lg"
                    variant="outline"
                    className="overflow-hidden border-primary/50 text-primary hover:text-white hover:bg-primary/10 px-8 py-6 text-lg font-medium"
                    onClick={() => {
                      // Use the utility function to handle landing page navigation
                      import('@/lib/auth').then(({ navigateToLandingPage }) => {
                        navigateToLandingPage(isAuthenticated);
                      });
                    }}
                  >
                    <span className="flex items-center font-mono">
                      Back to PoseFit Main
                      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="ml-2"><path d="m12 19-7-7 7-7"></path><path d="M19 12H5"></path></svg>
                    </span>
                  </Button>
                </div>
              </div>

              {/* RIGHT SIDE CONTENT */}
              <div className="lg:col-span-5 relative">
                {/* CORNER PIECES */}
                <div className="absolute -inset-4 pointer-events-none">
                  <div className="absolute top-0 left-0 w-16 h-16 border-l-2 border-t-2 border-border" />
                  <div className="absolute top-0 right-0 w-16 h-16 border-r-2 border-t-2 border-border" />
                  <div className="absolute bottom-0 left-0 w-16 h-16 border-l-2 border-b-2 border-border" />
                  <div className="absolute bottom-0 right-0 w-16 h-16 border-r-2 border-b-2 border-border" />
                </div>

                {/* IMAGE CONTANINER */}
                <div className="relative aspect-square max-w-lg mx-auto">
                  <div className="relative overflow-hidden rounded-lg bg-cyber-black">
                    <img
                      src="/home.png"
                      alt="AI Fitness Coach"
                      className="size-full object-cover object-center"
                    />

                    {/* SCAN LINE */}
                    <div className="absolute inset-0 bg-[linear-gradient(transparent_0%,transparent_calc(50%-1px),var(--cyber-glow-primary)_50%,transparent_calc(50%+1px),transparent_100%)] bg-[length:100%_8px] animate-scanline pointer-events-none" />

                    {/* DECORATIONS ON TOP THE IMAGE */}
                    <div className="absolute inset-0 pointer-events-none">
                     

                      {/* Targeting lines */}
                      <div className="absolute top-1/2 left-0 w-1/4 h-px bg-primary/50" />
                      <div className="absolute top-1/2 right-0 w-1/4 h-px bg-primary/50" />
                      <div className="absolute bottom-0 left-1/2 h-1/4 w-px bg-primary/50" />
                    </div>

                    <div className="absolute inset-0 bg-gradient-to-t from-background via-background/40 to-transparent" />
                  </div>

                  {/* TERMINAL OVERLAY */}
                  <TerminalOverlay />
                </div>
              </div>
            </div>
          </div>
        </section>

        {isAuthenticated && <UserPrograms />}
      </div>
    </>
  );
};

export default HomePage;
