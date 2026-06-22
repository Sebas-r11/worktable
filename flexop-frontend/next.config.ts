import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Django/DRF exigen barra final (/api/auth/login/). Sin esto, Next redirige 308 y rompe POST.
  skipTrailingSlashRedirect: true,
  turbopack: {
    root: __dirname,
  },
  // El proxy /api → Django va en src/middleware.ts (preserva la barra final).
};

export default nextConfig;
