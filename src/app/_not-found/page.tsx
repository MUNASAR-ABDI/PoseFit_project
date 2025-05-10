'use client';

import Link from 'next/link';

// Mark this page as server-side only to avoid prerendering issues
export const dynamic = 'force-dynamic';

export default function NotFoundCatchAll() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-24 text-center">
      <h1 className="text-4xl font-bold mb-4">404 - Page Not Found</h1>
      <p className="text-xl mb-8">
        Sorry, the page you are looking for does not exist.
      </p>
      <Link 
        href="/"
        className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
      >
        Go to Homepage
      </Link>
    </div>
  );
} 