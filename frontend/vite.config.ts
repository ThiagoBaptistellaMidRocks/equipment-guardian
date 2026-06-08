import path from "path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "react-map-gl/maplibre": path.resolve(__dirname, "node_modules/react-map-gl/dist/maplibre.js"),
    },
  },
  server: {
    port: 5173,
  },
});
