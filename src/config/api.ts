export const ENV = {
  // Centralized API configuration.
  // DO NOT HARDCODE URLs ANYWHERE ELSE IN THE APP.
  
  // Local Emulator Testing:
  // API_BASE_URL: 'http://10.0.2.2:8000/api/v1',
  
  // Local Physical Device Testing (Requires same WiFi and Firewall OFF):
  API_BASE_URL: 'http://192.168.1.35:8000/api/v1',
  
  // Internet Testing via Cloudflare Tunnel (RECOMMENDED):
  // 1. Run `cloudflared tunnel --url http://localhost:8000` on your PC
  // 2. Paste the generated HTTPS URL below and add `/api/v1`
  // API_BASE_URL: 'https://former-asin-rugby-scout.trycloudflare.com/api/v1',
  
  // Production
  // API_BASE_URL: 'https://api.yourdomain.com/api/v1',
};
