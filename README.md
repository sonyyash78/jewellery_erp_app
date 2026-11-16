# 💎 Jewellery ERP — Complete Showroom Management System

A production-grade, offline-first **Jewellery Showroom Management & Point-of-Sale (POS) ERP** designed specifically for Indian jewellery businesses. Features real-time counter billing, automated GST tax compliance, live bullion market tickers, inventory barcoding, old metal exchange ledgers, dual-company isolation, and zero-dependency portable deployment.

---

## 🌟 Key Features & Capabilities

### ⚡ 1. Point of Sale & Counter Billing
- **Interactive Metal Calculator**: Real-time pricing for **Gold** (24K, 22K, 20K, 18K, 14K), **Silver** (Fine, 92.5 Sterling, 70% Common), and **Diamonds**.
- **Wastage & Touch Precision**: Enforces strict Wastage ($\ge 0$ grams) and Touch purity point validation.
- **Flexible Making Charges**: Supports Percentage (`%`), Per Gram (`₹/g`), and Flat (`₹`) calculations.
- **Hallmark & Miscellaneous Charges**: Seamless tracking of BIS hallmark fees and custom charges.
- **Keyboard-First Design**: Optimized for rapid counter operations (`F12` Checkout, `Enter` Navigation, `Alt+1`/`Alt+2` Company Switch).

### 🏛️ 2. Dual-Company Multi-Store Architecture
- **Normal Retail Co. vs. GST Tax Invoice Co.**: Instant 1-click toggle between non-GST counter estimates and official GST Tax Invoices.
- **Isolated Sequences & Prefixes**: Strict company separation with independent invoice number generators (`INV-` vs `SJ-`).
- **Independent Business Profiles**: Custom shop names, GSTIN, PAN, addresses, contact numbers, and invoice headers per operating firm.

### 🧾 3. Indian Jewellery GST Engine
- **Separate HSN-Wise Tax Breakdown**:
  - **Gold Jewellery**: HSN `711319` (3% GST $\rightarrow$ 1.5% CGST + 1.5% SGST)
  - **Silver Jewellery**: HSN `711311` (3% GST $\rightarrow$ 1.5% CGST + 1.5% SGST)
- **Automatic Inter-State / Intra-State Detection**: Switches between CGST+SGST and IGST automatically based on customer state code.
- **B2B & B2C Compliant Printouts**: Full compatibility with thermal receipt printers and standard A4/A5 laser invoices.

### 📈 4. Always-Live Metal Rates & Custom Showroom Rates
- **Real-Time Bullion Feed**: Live international spot prices (Gold XAU/USD & Silver XAG/USD) converted to ₹/10g and ₹/kg with currency exchange conversion.
- **60-Second Auto-Sync**: Background polling keeps counter billing and dashboard widgets continuously in sync.
- **Offline Cache Resilience**: Automatically falls back to SQLite cached rates if internet connectivity drops.
- **Custom Showroom Rates**: Add and manage custom showroom rates (e.g., *22K Showroom Rate*, *Chandi Payal Special*) alongside the live market ticker.

### 🔄 5. Old Metal Exchange & Scrap Purchases
- **Fine Weight Calculation**: Accurate pure metal weight calculation from Gross Weight, Touch, and Tanch deductions.
- **Flexible Settlement**: Settle balances to Cash Due, Customer Metal Ledger, or combined hybrid settlement.
- **Full Audit Trail**: Generates itemized Exchange Vouchers and Purchase receipts with digital signatures.

### 📦 6. Inventory & Barcoding
- Track stock by Metal, Category, Purity, Gross Weight, Net Weight, and Stone Weight.
- In-app QR Code and Barcode generation for instant item lookup at the billing counter.

### 👥 7. Customer & Supplier Khata (Ledgers)
- Dual-ledger tracking: **Cash Balance** and **Pure Metal (Fine Weight) Balance**.
- Customer transaction history, payment receipts, and automated account statements.

### 💾 8. Hardware-Level Zero-Loss USB Auto-Mirror
- **Primary Fast Storage**: Local SQLite database in WAL (Write-Ahead Logging) mode at `%USERPROFILE%\JewelleryERP_Data`.
- **Automatic Pendrive Sync**: Continuously detects removable drives; automatically checkpoints and mirrors the database and archived invoice PDFs upon USB insertion or application exit.

### 🚀 9. Zero-Dependency Portable Distribution
- Bundled standalone Python backend (`jewellery-backend.exe` via PyInstaller).
- Can be copied to any new Windows PC/laptop and launched immediately **without installing Python, Node.js, or any third-party dependencies**.

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Desktop Shell** | Electron 30, PyInstaller Standalone Runtime, Node.js |
| **Frontend UI** | React 19, TypeScript, Vite, Tailwind CSS, Zustand, Lucide Icons |
| **Backend API** | Python 3.13, FastAPI, SQLAlchemy ORM, Uvicorn, Pydantic v2 |
| **Database** | SQLite 3 with WAL Mode (or PostgreSQL for Cloud Multi-User) |
| **PDF & Printing** | Chromium In-Process PDF Bridge (`/render-pdf`) + ReportLab Fallback |

---

## 📂 Project Structure

```text
jeweller-app/
├── backend/                        # FastAPI Backend Application
│   ├── app/
│   │   ├── api/v1/                 # Endpoints (billing, invoices, metal_rates, stock, etc.)
│   │   ├── models/                 # SQLAlchemy Database Models
│   │   ├── schemas/                # Pydantic Request/Response Schemas
│   │   ├── services/               # Core business services (gst_engine, live_rate, calc)
│   │   └── main.py                 # FastAPI Application Initialization
│   ├── jewellery-backend.spec      # PyInstaller build specification
│   ├── requirements.txt            # Python dependencies
│   └── run_server.py               # Backend startup script & entrypoint
│
├── frontend/                       # React 19 + Vite Frontend Application
│   ├── src/
│   │   ├── api/                    # Axios API Clients & Endpoints
│   │   ├── components/             # Reusable UI widgets, modals, layout
│   │   ├── pages/                  # Billing, Inventory, Invoices, Exchange, CRM
│   │   ├── store/                  # Zustand Global State (billingStore, companyStore)
│   │   ├── utils/                  # GST calculations, PDF generators, shortcuts
│   │   └── App.tsx                 # HashRouter & View Routing
│   └── package.json
│
├── desktop/                        # Electron Desktop Packaging
│   ├── src/
│   │   ├── main.js                 # Electron process manager, USB watcher, PDF bridge
│   │   └── preload.js              # IPC Bridge
│   └── package.json
│
├── scripts/                        # Automation & Synchronization Utilities
│   ├── sync_portable_distribution.py   # Synchronizes dist, ASAR, & standalone backend
│   └── sync_to_saideep_mirror.py       # Mirrors code to Saideep git repository
│
└── README.md                       # Master Documentation
```

---

## ⌨️ Counter Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `F12` | Instant Checkout / Generate Bill |
| `F4` | Navigate directly to Billing Counter |
| `F8` | Navigate directly to Invoices History |
| `Alt + 1` | Switch to **Company 1 (Normal Retail / Non-GST)** |
| `Alt + 2` | Switch to **Company 2 (GST Tax Invoice)** |
| `Enter` | Focus next input field automatically |
| `Esc` | Close active modal / Exit preview |

---

## 🚀 Running the Project

### Option A: Portable Version (Recommended for Production)
1. Extract `Jewellery_ERP_Desktop_Portable.zip` on your Windows PC.
2. Double-click `Jewellery ERP Desktop.exe`.
3. *No Python, database setup, or terminal commands required.*

### Option B: Development Setup

#### 1. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run_server.py
```
*Backend will start on `http://127.0.0.1:8000`.*

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*Frontend dev server will start on `http://localhost:5173`.*

#### 3. Desktop Shell (Electron)
```bash
cd desktop
npm install
npm run dev
```

---

## 🔒 Security & Data Safety

- **Local Storage Path**: SQLite database is stored at `%USERPROFILE%\JewelleryERP_Data\jewellery_erp.db`.
- **Multi-Tenant JWT**: Strong token-based authentication with role-based access control (Admin, Manager, Staff).
- **Offline Integrity**: Runs completely offline with zero telemetry or external server tracking.
- **Automated USB Vault**: Auto-mirrors SQLite database and encrypted invoice PDF archives to inserted USB storage drives.

---

## 📄 License & Ownership
Proprietary software developed for **SJ Jewellers / Saideep Jewellers**. All rights reserved.
