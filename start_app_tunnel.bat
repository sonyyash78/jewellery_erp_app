@echo off
title SAIDEEP JEWELLERS - Mobile App Cloudflare Tunnel (Port 8001)
echo ========================================================
echo Starting Cloudflare Tunnel for App Backend (Port 8001)...
echo Copy the generated trycloudflare.com URL and paste into
echo src/config/api.ts -> API_BASE_URL
echo ========================================================
"C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://localhost:8001
pause
