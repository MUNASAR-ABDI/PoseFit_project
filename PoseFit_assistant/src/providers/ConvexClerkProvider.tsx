"use client";

import { ClerkProvider, useAuth } from "@clerk/nextjs";
import { ConvexReactClient } from "convex/react";
import { ConvexProviderWithClerk } from "convex/react-clerk";

// Use fallback empty string to prevent build errors when env variable is missing
const convexUrl = process.env.NEXT_PUBLIC_CONVEX_URL || "";
const convex = new ConvexReactClient(convexUrl);

function ConvexClerkProvider({ children }: { children: React.ReactNode }) {
  // Use fallback for clerk key too
  const clerkKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY || "";
  
  return (
    <ClerkProvider publishableKey={clerkKey}>
      <ConvexProviderWithClerk client={convex} useAuth={useAuth}>
        {children}
      </ConvexProviderWithClerk>
    </ClerkProvider>
  );
}

export default ConvexClerkProvider;
