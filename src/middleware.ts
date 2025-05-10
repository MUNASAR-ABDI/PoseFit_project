import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

// Define public routes that don't require authentication
const publicRoutes = createRouteMatcher(["/", "/sign-in", "/sign-up"]);

export default clerkMiddleware({
  // Check if the request is for a public route
  publicRoutes: (req) => publicRoutes(req),
});

export const config = {
  matcher: ["/((?!.+\\.[\\w]+$|_next).*)", "/", "/(api|trpc)(.*)"],
};