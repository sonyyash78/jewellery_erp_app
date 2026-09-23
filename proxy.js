const http = require('http');

const PORT = 8082;
const BACKEND_URL = 'http://127.0.0.1:8000';

const server = http.createServer((clientReq, clientRes) => {
  console.log(`[PROXY] Incoming request from ${clientReq.socket.remoteAddress} -> ${clientReq.method} ${clientReq.url}`);

  const options = {
    hostname: '127.0.0.1',
    port: 8000,
    path: clientReq.url,
    method: clientReq.method,
    headers: clientReq.headers
  };

  const proxyReq = http.request(options, (proxyRes) => {
    clientRes.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(clientRes, { end: true });
  });

  proxyReq.on('error', (e) => {
    console.error(`[PROXY ERROR] ${e.message}`);
    clientRes.writeHead(500);
    clientRes.end('Proxy Error');
  });

  clientReq.pipe(proxyReq, { end: true });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`Node Proxy started on port ${PORT}`);
  console.log(`Forwarding all traffic to ${BACKEND_URL}`);
});
