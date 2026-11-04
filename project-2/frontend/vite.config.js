import { defineConfig } from 'vite';
import { readFileSync } from 'node:fs';

function certificateDownload(server) {
  server.middlewares.use((req, res, next) => {
    if (req.url?.split('?')[0] === '/voice-link-ca.cer') {
      res.setHeader('Content-Type', 'application/pkix-cert');
      res.setHeader('Content-Disposition', 'attachment; filename="voice-link-ca.cer"');
    }
    next();
  });
}

export default defineConfig(({ mode }) => ({
  plugins: [{ name: 'certificate-download', configureServer: certificateDownload, configurePreviewServer: certificateDownload }],
  server: {
    port: 5173,
    strictPort: true,
    https: mode === 'https' ? {
      key: readFileSync(new URL('../.certs/server-key.pem', import.meta.url)),
      cert: readFileSync(new URL('../.certs/server.pem', import.meta.url)),
    } : undefined,
    fs: { deny: ['.env', '.env.*', '*.{crt,pem}', '**/.git/**', '**/.certs/**'] },
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/ws': { target: 'ws://127.0.0.1:8000', ws: true },
    },
  },
}));
