/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  webpack: (config) => {
    config.resolve.alias['@'] = __dirname;
    return config;
  },
}

module.exports = nextConfig