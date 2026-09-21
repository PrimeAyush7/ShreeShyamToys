# Shree Shyam Toys — B2B Wholesale Catalogue & WhatsApp Enquiry Platform

A complete, production-ready, responsive B2B wholesale soft-toy catalogue and enquiry engine for **Shree Shyam Toys**.

This platform is engineered specifically for B2B manufacturers and wholesale distributors supplying retail chains, toy gift shops, and corporate buyers. Instead of retail cart/checkout gateways, it features an **Add to Enquiry** workflow, item-level **Minimum Order Quantity (MOQ)** validation, database-first enquiry persistence, customer snapshot isolation, dynamic admin CMS, and automated WhatsApp Business enquiry generation.

---

## Table of Contents
1. [Core Features & Architecture](#core-features--architecture)
2. [Prerequisites & System Requirements](#prerequisites--system-requirements)
3. [Quick Start / Local Setup](#quick-start--local-setup)
4. [Environment Variables Reference](#environment-variables-reference)
5. [Supabase PostgreSQL Setup & Migrations](#supabase-postgresql-setup--migrations)
6. [Google OAuth 2.0 Configuration](#google-oauth-20-configuration)
7. [Admin Authorization & Allowlist System](#admin-authorization--allowlist-system)
8. [Persistent Media Storage Setup](#persistent-media-storage-setup)
9. [WhatsApp Business Integration](#whatsapp-business-integration)
10. [Data Backup & Export System](#data-backup--export-system)
11. [Production Deployment to Render](#production-deployment-to-render)
12. [Running Automated Tests](#running-automated-tests)
13. [Manual Production Verification](#manual-production-verification)
14. [Troubleshooting & FAQ](#troubleshooting--faq)

---

## 1. Core Features & Architecture

- **B2B Wholesale Model**: No public retail prices are displayed anywhere on the website (adhering to B2B pricing discretion: "Enquire for Wholesale Details").
- **Google OAuth Only**: Customers and admins sign in securely via Google OAuth 2.0. Mobile numbers are mandatory before submitting enquiries.
- **Strict MOQ Validation**: Every product and variant has an independently defined Minimum Order Quantity (e.g. 20, 50, 100 pcs). Submitting a quantity below MOQ is strictly rejected with explicit guidance.
- **Fail-Safe Database-First WhatsApp Flow**: Enquiries and product snapshots (product name, SKU, size, colour, quantity, MOQ) are archived in the PostgreSQL database **first**. Only after confirmed database persistence is the structured WhatsApp Business message generated and opened. If WhatsApp fails to open or is blocked by browser pop-up guards, the enquiry is safely preserved in the database with reference numbers (e.g., `SST-ENQ-2026-0001`).
- **Admin Control System (CMS)**: Two authorized administrators can manage all aspects without modifying code:
  - Products CRUD (variants, image galleries, zoom, soft-archive/restore, duplication)
  - Categories CRUD (display order, slug, active status, SEO meta)
  - Customer Accounts (search, inspect enquiries, toggle active status)
  - Enquiries Management (workflow status: New, Contacted, Quotation Sent, Confirmed, Completed, Cancelled)
  - Homepage CMS (Hero banner, Why Choose Us, How it Works, Bulk CTA banner, About text)
  - Global Website Settings (brand title, WhatsApp number, phone, email, address, announcement bar, footer)
  - FAQs and Dynamic Social Links
  - Comprehensive Audit Trail logging
- **Export & Backup Engine**: Export any table to styled Excel (`.xlsx`) or CSV. Download the complete system backup as a single ZIP (`Shree-Shyam-Toys-Backup-YYYY-MM-DD.zip`) containing formatted `.xlsx` workbooks for all datasets and the media manifest.
- **Responsive & Accessible**: Custom-styled for 320px ultra-small smartphones through 1920px+ desktop monitors with zero horizontal overflow, touch-friendly image zoom gallery, and mobile filter drawers.

---

## 2. Prerequisites & System Requirements

- **Python**: 3.10, 3.11, or 3.12
- **Database**: 
  - *Production*: Supabase PostgreSQL 15+ (strictly required in production; SQLite is blocked in production mode)
  - *Local Development / Offline Testing*: Persistent SQLite database (automatically used when `DATABASE_URL` is omitted and `ENVIRONMENT!=production`)
- **Google Cloud Console Account**: For Google OAuth Client ID & Secret
- **WhatsApp Business Phone Number**: International format without '+' (e.g., `91XXXXXXXXXX`)

---

## 3. Quick Start / Local Setup

### Step 1: Clone or Extract the Project
```bash
cd shree_shyam_toys
```

### Step 2: Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Local Environment
```bash
cp .env.example .env
```
Edit `.env` as needed. If you leave `DATABASE_URL` empty in development mode, the system automatically initializes an embedded SQLite database with complete seed products, categories, and settings.

### Step 5: Start the Development Server
```bash
python run_server.py
```
Open [http://localhost:8000](http://localhost:8000) in your web browser.

---

## 4. Environment Variables Reference

| Variable | Description | Example / Default |
| :--- | :--- | :--- |
| `APP_NAME` | Name of the platform | `Shree Shyam Toys` |
| `APP_URL` | Base public URL | `http://localhost:8000` or `https://shreeshyamtoys.onrender.com` |
| `ENVIRONMENT` | Environment mode | `development` or `production` |
| `DEBUG` | Debugging mode (keep false in production) | `false` |
| `SECRET_KEY` | HMAC key for signing encrypted session cookies | 32+ character random string |
| `DATABASE_URL` | Supabase PostgreSQL connection string | `postgresql://postgres:pwd@db.xxx.supabase.co:5432/postgres` |
| `SUPABASE_URL` | Supabase project URL (optional API access) | `https://xyzproject.supabase.co` |
| `SUPABASE_ANON_KEY` | Supabase public anon key | `eyJhbGciOiJIUzI1NiIsIn...` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase private service key for Storage | `eyJhbGciOiJIUzI1NiIsIn...` |
| `GOOGLE_CLIENT_ID` | Google Cloud OAuth Client ID | `123456789-abc.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Google Cloud OAuth Client Secret | `GOCSPX-xxxxxxxxxxxxxx` |
| `GOOGLE_REDIRECT_URI` | Authorized OAuth Redirect URI | `http://localhost:8000/auth/google/callback` |
| `ADMIN_EMAILS` | Comma-separated allowlist of authorized admin Google emails | `admin@shreeshyamtoys.com,owner@shreeshyamtoys.com` |
| `WHATSAPP_NUMBER` | Default primary WhatsApp Business number | `91XXXXXXXXXX` (digits only) |
| `STORAGE_BACKEND` | Storage backend (`supabase` or `local`) | `supabase` (prod), `local` (dev) |
| `SUPABASE_STORAGE_BUCKET` | Storage bucket name for product images | `product-media` |

---

## 5. Supabase PostgreSQL Setup & Migrations

Shree Shyam Toys is designed to run on Supabase PostgreSQL for production.

### Setting up Supabase:
1. Sign up or log in at [supabase.com](https://supabase.com).
2. Click **New Project** and name it `shree-shyam-toys`.
3. Choose a secure database password and select a region close to your target buyers (e.g., `South Asia - Mumbai`).
4. Once provisioned, navigate to **Project Settings** &rarr; **Database**:
   - Copy the **Connection URI** (Connection pooling mode or Direct mode).
   - In `.env` or Render environment settings, set:
     ```env
     DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres?sslmode=require"
     ```
5. Apply SQL Migrations:
   - Navigate to the **SQL Editor** in your Supabase dashboard.
   - Run the contents of `migrations/001_initial_schema.sql`.
   - Run the contents of `migrations/002_seed_data.sql`.
   *(Alternatively, on first application start, the built-in migration runner will automatically apply missing tables and seed data!)*

---

## 6. Google OAuth 2.0 Configuration

Customer and administrator logins exclusively use Google OAuth 2.0.

### Creating Google OAuth Credentials:
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project named `Shree Shyam Toys Wholesale`.
3. Go to **APIs & Services** &rarr; **OAuth consent screen**:
   - User Type: **External**
   - App Name: `Shree Shyam Toys`
   - User support email: `your-email@gmail.com`
   - Developer contact email: `your-email@gmail.com`
   - Scopes: select `.../auth/userinfo.email` and `.../auth/userinfo.profile`.
4. Go to **APIs & Services** &rarr; **Credentials**:
   - Click **Create Credentials** &rarr; **OAuth client ID**.
   - Application type: **Web application**.
   - Name: `Shree Shyam Toys Web Client`.
   - **Authorized JavaScript origins**:
     - `http://localhost:8000`
     - `https://shreeshyamtoys.onrender.com`
   - **Authorized redirect URIs**:
     - `http://localhost:8000/auth/google/callback`
     - `https://shreeshyamtoys.onrender.com/auth/google/callback`
5. Copy the generated **Client ID** and **Client Secret** into your `.env`:
   ```env
   GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
   GOOGLE_CLIENT_SECRET="your-client-secret"
   GOOGLE_REDIRECT_URI="https://shreeshyamtoys.onrender.com/auth/google/callback"
   ```

---

## 7. Admin Authorization & Allowlist System

To safeguard business data and prevent unauthorized administrative access:
1. There are **NO public default passwords** (e.g., `admin/admin`).
2. Only Google accounts whose emails are explicitly listed in the `ADMIN_EMAILS` environment variable can access `/admin`.
3. Example configuration in `.env`:
   ```env
   ADMIN_EMAILS="partner1@gmail.com,partner2@shreeshyamtoys.com"
   ```
4. When an authorized user signs in via Google OAuth, the system verifies their email address against this allowlist and grants access to the admin dashboard. Any unauthorized Google account attempting to view `/admin` routes receives a strict **403 Forbidden** response.

---

## 8. Persistent Media Storage Setup

Render's disk is ephemeral and resets on every redeploy. To ensure product photos persist permanently across restarts and redeploys:

### Setting up Supabase Storage:
1. In your Supabase Dashboard, navigate to **Storage**.
2. Click **New Bucket** and name it `product-media`.
3. Toggle **Public Bucket** to ON (so uploaded product images can be served publicly).
4. In `.env`, set:
   ```env
   STORAGE_BACKEND="supabase"
   SUPABASE_STORAGE_BUCKET="product-media"
   SUPABASE_URL="https://[PROJECT-REF].supabase.co"
   SUPABASE_SERVICE_ROLE_KEY="[YOUR-SERVICE-ROLE-KEY]"
   ```
5. Every upload automatically records an entry in the `media_manifest` table containing the public URL, filename, file size, MIME type, and associated product ID.

---

## 9. WhatsApp Business Integration

The website generates structured, URL-encoded WhatsApp messages.
1. The primary WhatsApp number is configured under **Website Settings** in the Admin Portal (or via `WHATSAPP_NUMBER` in `.env`).
2. Ensure the number uses country code without leading zeroes or plus signs (e.g., `91XXXXXXXXXX` for India).
3. The generated message structure sent to the sales desk:
   ```text
   Hello Shree Shyam Toys,
   I would like to enquire about the following wholesale products:

   • Heritage Cuddle Teddy Bear
     SKU: SST-TB-101
     Size: 60 CM
     Colour: Classic Brown
     Quantity: 50 pcs (MOQ: 30)

   • Gentle Giant Panda Plush
     SKU: SST-WL-301
     Size: 35 CM
     Colour: Black & White Natural
     Quantity: 25 pcs (MOQ: 25)

   Customer Details:
   Name: Rajesh Kumar
   Mobile: +91 99999 88888
   Email: wholesale_buyer@toyhub.in
   Notes: Bulk order quotation required for 3 branches.

   Please share availability and wholesale quotation.
   Thank you.
   ```
4. **Critical Safety**: The enquiry is saved in the database **before** launching WhatsApp. If pop-ups are blocked, a modal stays open on the screen showing the enquiry reference and a direct button to open WhatsApp.

---

## 10. Data Backup & Export System

Under `/admin/exports`, administrators can:
1. Download **Individual Tables** in both **Excel (`.xlsx`)** and **CSV** formats:
   - Products
   - Enquiries
   - Enquiry Items Snapshot
   - Customer Accounts
   - Categories
   - Website Settings
   - Wholesale FAQs
   - Dynamic Social Links
   - Media Manifest
2. **Export Everything**:
   Clicking **Download Complete Backup ZIP** compiles `Shree-Shyam-Toys-Backup-YYYY-MM-DD.zip` containing 9 styled Excel workbooks with column autofit, bold headers, and timestamps.

---

## 11. Production Deployment to Render

This repository includes `render.yaml` and `Procfile` ready for zero-downtime deployment.

### Steps to Deploy:
1. Push this repository to GitHub or GitLab.
2. Sign in to [render.com](https://render.com) and click **New** &rarr; **Blueprint** (or **New** &rarr; **Web Service**).
3. Connect your repository.
4. Render will read `render.yaml` and configure:
   - **Environment**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Set the required environment variables in the Render Dashboard:
   - `DATABASE_URL` (Supabase PostgreSQL connection string)
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `GOOGLE_REDIRECT_URI` (`https://<your-service>.onrender.com/auth/google/callback`)
   - `ADMIN_EMAILS` (`admin1@gmail.com,admin2@gmail.com`)
   - `SECRET_KEY` (Generate a secure random string)
   - `WHATSAPP_NUMBER` (`91XXXXXXXXXX`)
   - `STORAGE_BACKEND` (`supabase`)
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `SUPABASE_STORAGE_BUCKET` (`product-media`)
6. Deploy! Render will build and launch your production catalogue.

---

## 12. Running Automated Tests

A comprehensive end-to-end test suite validates all critical paths:
```bash
python run_tests.py
```
This runs automated tests verifying:
- Public catalogue and SEO pages
- Pricing privacy policy & fake claims removal (no currency prices or unverified claims)
- Customer login and profile updates
- Item-level MOQ validation and DB-first enquiry creation
- Snapshot preservation of historical enquiries
- Admin authorization allowlist and 403 blocks
- Admin Product CRUD, duplication, archive, and restore
- Excel XLSX and full backup ZIP generation
- HTTP security headers and Schema.org Breadcrumb/Product SEO JSON-LD

---

---

## 13. Manual Production Verification

> **Important Security Notice**: The `/auth/test-login` endpoint is **strictly disabled in production** (`ENVIRONMENT=production` or Render environment). It exists solely as an offline developer and automated test harness. Automated unit tests use this endpoint to test internal RBAC and session signing; **they do NOT test real Google OAuth**. In production, real Google OAuth 2.0 with cryptographic state validation and Google's token servers is strictly required.

Follow these step-by-step instructions to manually verify production authentication and permissions on your live deployment:

### Step 1: Customer Google Login
1. Open your live deployment URL (e.g. `https://<your-service>.onrender.com`).
2. Click **Google Login** in the top navigation or from the catalogue page.
3. You will be redirected to Google's official OAuth consent screen (`accounts.google.com`).
4. Select or enter any standard Google account.
5. Upon successful consent, Google redirects back to `/auth/google/callback`.
6. Confirm that the top navigation now shows your Google name and avatar, with access to **Track Enquiries** and **Profile**.

### Step 2: Customer Profile & Mobile Number Entry
1. Navigate to `/customer/profile` from the user menu.
2. Verify that your Google account Name and Email are pre-filled and read-only.
3. Enter your 10-digit mobile number in the **WhatsApp Business / Mobile Number** field and click **Update Profile**.
4. Verify the success banner appears and the mobile number remains saved across page refreshes.

### Step 3: Customer Wholesale Enquiry & Mobile Flow
1. Go to `/catalogue`, select a product (e.g., Heritage Cuddle Teddy Bear).
2. Ensure quantity meets the displayed MOQ (e.g., 30 pcs). Click **+ Add to Enquiry**.
3. Open the Enquiry Drawer and click **Submit Enquiry to WhatsApp**.
4. Confirm:
   - The enquiry is committed to Supabase PostgreSQL first.
   - A unique reference (e.g., `SST-ENQ-2026-0001`) is generated.
   - If WhatsApp Business number is configured, WhatsApp opens with the formatted itemized payload.
   - If WhatsApp is not yet configured, the system gracefully confirms that the enquiry was saved and displays an informational message.
5. Visit `/customer/enquiries` to confirm the submitted enquiry appears with its timestamp, status ("New"), and item details.

### Step 4: Admin Google Login (Authorized Accounts)
1. Ensure the Google email you plan to use is added to the `ADMIN_EMAILS` environment variable on Render (e.g., `ADMIN_EMAILS="admin1@gmail.com,owner@gmail.com"`).
2. Log in with that authorized Google account.
3. Navigate directly to `/admin`.
4. Confirm you are granted access to the **Admin Operational Overview** dashboard showing live metrics, enquiries, products, CMS editors, and export tools.

### Step 5: Unauthorized Google Account Rejection
1. Sign out by clicking **Sign Out** or navigating to `/auth/logout`.
2. Sign in with a different, personal Google account that is **NOT** listed in `ADMIN_EMAILS`.
3. Try navigating directly to `/admin` in the browser address bar.
4. Verify that access is strictly denied with an **HTTP 403 Forbidden** error page stating that your email is not authorized for administrative access.

---

## 14. Troubleshooting & FAQ

**Q: Why does the app fail to start in production with a database error?**  
A: To guarantee that business data is not lost when Render restarts, the application strictly requires `DATABASE_URL` pointing to Supabase PostgreSQL when running in production (`ENVIRONMENT=production`). SQLite is intentionally prohibited in production.

**Q: Why do I see a 403 when trying to access `/admin`?**  
A: Your signed-in Google email is not listed in `ADMIN_EMAILS`. Update your `.env` or Render environment settings to include your email address.

**Q: Why didn't WhatsApp open automatically after clicking submit?**  
A: Mobile browsers or pop-up blockers may block automated tab opening. When this occurs, the confirmation dialog displays a green **Open WhatsApp Business Chat** button so you can proceed without losing any data.

**Q: How do I change the website announcement or phone number without touching code?**  
A: Log in as an administrator, navigate to `/admin/settings`, modify the values, and click **Save Global Settings**. The changes apply immediately across the public website.

---
© 2026 Shree Shyam Toys. All rights reserved.
