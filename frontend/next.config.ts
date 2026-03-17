import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",  // necessário para deploy no Render/Docker
};

export default nextConfig;
