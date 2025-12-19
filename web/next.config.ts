import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Export as static site so it can be served by FastAPI on port 8000
  output: "export",
  // Host under /imh when mounted into another app (port 8000)
  basePath: "/imh",
  assetPrefix: "/imh",
  env: {
    // Used by client code when building absolute URLs (e.g. public assets)
    NEXT_PUBLIC_BASE_PATH: "/imh",
  },
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
