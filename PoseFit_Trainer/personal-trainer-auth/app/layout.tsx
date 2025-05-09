import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { MainNav } from "@/components/main-nav"
import { getCurrentUser } from "@/lib/actions/auth"
import { cookies } from "next/headers"
import { SessionManager } from "@/components/session-manager"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "PoseFit-Trainer",
  description: "Your personal AI-powered fitness trainer",
}

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // Get the current path to check if we're on the home page
  const cookieStore = cookies();
  const url = cookieStore.get("next-url")?.value;
  const isHomePage = !url || url === "/" || url === "/home";
  
  // If we're on the home page, don't try to get the user unless they have a valid session
  // This ensures the home page always shows the non-authenticated UI by default
  const hasSession = !!cookieStore.get("session")?.value;
  
  // Try to get the current user, but handle potential errors
  let user = null;
  if (!isHomePage || hasSession) {
    try {
      user = await getCurrentUser();
      // Remove the console.log message to avoid clutter
    } catch (error) {
      // Continue rendering without user data, but don't log to console
    }
  }
  
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider 
          attribute="class" 
          defaultTheme="system" 
          enableSystem
          disableTransitionOnChange
          suppressHydrationWarning
        >
          <div className="flex min-h-screen flex-col">
            {/* Always show MainNav, even on the home page */}
            <MainNav user={user} />
            <main className="flex-1">{children}</main>
          </div>
          {/* Session management component */}
          <SessionManager user={user} hasSession={hasSession} />
        </ThemeProvider>
      </body>
    </html>
  )
}
