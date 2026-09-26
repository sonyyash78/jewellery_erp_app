export const ENV = {
  // Centralized Mobile App API configuration.
  // Dedicated App Backend runs on Port 8001 connected to `jeweller_app_db`.
  
  // Local Emulator Testing:
  // API_BASE_URL: 'http://10.0.2.2:8001/api/v1',
  
  // Local Physical Device Testing (Same WiFi):
  // API_BASE_URL: 'http://192.168.1.36:8001/api/v1',
  
  // Internet Cloudflare Tunnel for Port 8001:
  // 1. Double-click `start_app_tunnel.bat`
  API_BASE_URL: 'https://headquarters-operating-fotos-mar.trycloudflare.com/api/v1',
};

