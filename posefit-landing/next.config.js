const repoName = 'PoseFit_project';
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  basePath: '/PoseFit_project',
  assetPrefix: '/PoseFit_project/',
  images: { unoptimized: true },
  reactStrictMode: true,
};

module.exports = nextConfig; 