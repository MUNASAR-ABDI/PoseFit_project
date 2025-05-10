/**
 * Application configuration with safe defaults for URLs
 */

// The base URL for the application itself (this Next.js app)
export const APP_URL = process.env.NEXT_PUBLIC_APP_URL || 'https://posefit-app.vercel.app';

// The base URL for the backend API
export const BACKEND_URL = process.env.BACKEND_URL || 'https://posefit-api.example.com';

// The URL for the landing page
export const LANDING_URL = process.env.NEXT_PUBLIC_LANDING_URL || 'https://posefit.example.com';

// The URL for the Convex backend (if applicable)
export const CONVEX_URL = process.env.NEXT_PUBLIC_CONVEX_URL || 'https://example-123.convex.cloud';

// Clerk publishable key (if applicable)
export const CLERK_PUBLISHABLE_KEY = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY || '';

// VAPI configuration (if applicable)
export const VAPI_API_KEY = process.env.NEXT_PUBLIC_VAPI_API_KEY || '';
export const VAPI_WORKFLOW_ID = process.env.NEXT_PUBLIC_VAPI_WORKFLOW_ID || ''; 