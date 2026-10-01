# 🌐 Deployment Guide: Handmade Leather Products BDM Dashboard

This guide provides instructions to deploy your Flask + Supabase / SQLite BDM Dashboard to **Vercel** or **Render** connected directly to your **GitHub** repository.

---

## ⚡ Option 1: Deploy on Vercel (Fast & Free)

The project includes pre-configured **[`vercel.json`](file:///vercel.json)** that enables Python serverless routing.

### Step 1: Push your latest code to GitHub
Run in your terminal / PowerShell:
```bash
git add .
git commit -m "Configure Vercel deployment with vercel.json"
git push origin main
```

### Step 2: Connect GitHub Repo to Vercel
1. Go to **[https://vercel.com](https://vercel.com)** and log in with your GitHub account.
2. On your Vercel dashboard, click **"Add New..."** $\rightarrow$ **"Project"**.
3. Under **Import Git Repository**, find your repository (`malavikavenugopal/BDM_Assignment_Group8`) and click **"Import"**.

### Step 3: Configure Project Settings
- **Framework Preset**: Leave as **Other** (or automatic).
- **Root Directory**: `./` (leave default).
- **Environment Variables**:
  - Add `DATABASE_URL`: `postgresql://postgres:[YOUR_PASSWORD]@[YOUR_HOST]:5432/postgres` (from your `.env` file).

### Step 4: Click "Deploy"
Vercel will build the serverless Python environment and assign you a live HTTPS URL (e.g. `https://bdm-assignment-group8.vercel.app`).

---

## 🏆 Option 2: Deploy on Render.com

If you prefer standard long-running server instances:

1. Go to **[https://dashboard.render.com](https://dashboard.render.com)**.
2. Click **New +** $\rightarrow$ **Web Service**.
3. Select your GitHub repository.
4. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn server:app --bind 0.0.0.0:$PORT`
   - **Environment Variables**: Add `DATABASE_URL`
5. Click **Create Web Service**.

---

## 🚂 Option 3: Deploy on Railway

1. Go to **[https://railway.app](https://railway.app)** $\rightarrow$ **New Project** $\rightarrow$ **Deploy from GitHub**.
2. Select repository $\rightarrow$ Add variable `DATABASE_URL`.
3. Railway deploys using the included `Procfile` automatically.
