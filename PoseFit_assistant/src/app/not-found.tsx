'use client';

import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] p-8">
      <div className="bg-card border border-border rounded-lg p-8 shadow-lg w-full max-w-md">
        <h1 className="text-3xl font-bold mb-4 text-center">404 - Page Not Found</h1>
        <p className="text-muted-foreground text-center mb-6">
          The page you are looking for does not exist or has been moved.
        </p>
        <div className="flex justify-center">
          <Link
            href="/"
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
          >
            Return Home
          </Link>
        </div>
      </div>
    </div>
  );
} 