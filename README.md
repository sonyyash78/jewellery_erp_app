# Jeweller App (Android)

This repository contains the mobile application for the Jewellery ERP system. It is built using React Native (Expo) and designed to compile into a native Android APK.

**IMPORTANT**: This application communicates exclusively with the existing FastAPI backend. It does not contain its own database.

## Architecture

- **Backend**: Existing FastAPI on your PC (port 8000)
- **Database**: Existing MySQL on your PC (port 3306)
- **Networking**: Cloudflare Tunnel (for remote access over the internet)
- **App**: React Native Android App (communicates with Cloudflare Tunnel URL)

---

## 🚀 Development & Testing Setup (Cloudflare Tunnel)

To test this Android app on a real phone over the internet without exposing your MySQL database, follow these steps:

### 1. Start the Backend
Open a terminal in the existing `jewellery-erp` backend directory and start the server:
```bash
cd ../jewellery-erp/backend
call venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start Cloudflare Tunnel
Download and install `cloudflared` (if you haven't already). Then, open a new terminal and run:
```bash
cloudflared tunnel --url http://localhost:8000
```
*Cloudflare will generate a public HTTPS URL (e.g., `https://random-words.trycloudflare.com`). Note this URL.*

### 3. Configure the App's API URL
Open `src/config/api.ts` in this project and paste the Cloudflare URL into the `API_BASE_URL` constant.
```typescript
export const ENV = {
  // Add '/api/v1' to the end of the cloudflare URL
  API_BASE_URL: 'https://random-words.trycloudflare.com/api/v1',
};
```

### 4. Build and Install the App
Start the Expo development server:
```bash
npm start
```
You can scan the QR code using the "Expo Go" app on your Android phone to test it immediately over the internet (even if you are on 5G mobile data).

---

## 📦 Building the Standalone APK

To build the final standalone APK that you can install on any Android phone without Expo Go:

1. Install EAS CLI (if not installed):
   ```bash
   npm install -g eas-cli
   ```
2. Log in to your Expo account:
   ```bash
   eas login
   ```
3. Build the Android APK locally:
   ```bash
   eas build -p android --profile preview
   ```
   *This will generate a `.apk` file download link when complete.*
4. Download the APK and install it on your Android phone.

---

## 🔒 Security Notes
- **Never expose MySQL**: Do not run a tunnel to port 3306. Only port 8000 (FastAPI) should be exposed.
- **No Secrets**: Never hardcode database passwords or secret keys in this React Native app.
