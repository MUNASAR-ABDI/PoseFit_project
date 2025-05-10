const repoName = 'PoseFit_project';
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  basePath: '/PoseFit_project',
  assetPrefix: '/PoseFit_project/',
  images: { unoptimized: true },
  reactStrictMode: true,
  webpack: (config) => {
    config.module.rules.push({
      test: /\.css$/,
      use: ['style-loader', 'css-loader', 'postcss-loader'],
    });
    return config;
  },
};

module.exports = nextConfig; 