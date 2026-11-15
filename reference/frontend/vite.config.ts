import react from "@vitejs/plugin-react";
import { defineConfig, type Plugin } from "vite";

function fixtureSession(): Plugin {
  return {
    name: "fixture-session",
    configurePreviewServer(server) {
      const tenant = process.env.REFERENCE_UI_TENANT;
      const token = process.env.REFERENCE_UI_AUTHORIZATION;
      if (!tenant || !token) {
        throw new Error(
          "Synthetic preview session must be supplied by the test harness",
        );
      }
      server.middlewares.use("/session", (request, response) => {
        if (request.method !== "GET" || request.url !== "/") {
          response.writeHead(404).end();
          return;
        }
        response
          .writeHead(200, {
            "Content-Type": "application/json",
            "Cache-Control": "no-store",
          })
          .end(JSON.stringify({ tenant_id: tenant }));
      });
    },
  };
}

const api = process.env.REFERENCE_UI_API;
const authorization = process.env.REFERENCE_UI_AUTHORIZATION;

if (api && !/^http:\/\/127\.0\.0\.1:\d+$/.test(api)) {
  throw new Error("The reference API must be a disposable loopback fixture");
}

export default defineConfig({
  plugins: [react(), fixtureSession()],
  preview: {
    host: "127.0.0.1",
    strictPort: true,
    proxy:
      api && authorization
        ? {
            "^/api/customers(?:\\?|$)": {
              target: api,
              rewrite: (path) => path.replace(/^\/api/, ""),
              headers: { Authorization: authorization },
            },
          }
        : undefined,
  },
});
