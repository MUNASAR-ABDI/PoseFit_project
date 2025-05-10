/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    // Disable static generation of the _not-found page to avoid URL issues
    disableOptimizedLoading: true,
    serverMinification: false,
  },
  // Explicitly allow importing from outside the src directory
  transpilePackages: ['next-auth'],
  // Control which pages are generated at build time
  output: 'standalone',
  
  // Custom headers to fix potential CSP issues
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self' https://*;",
          },
        ],
      },
    ]
  },
  
  // Manage the URLs that get prerendered during build
  async exportPathMap() {
    // Don't prerender the not-found page
    return {
      '/': { page: '/' },
    }
  }
};

module.exports = nextConfig; 