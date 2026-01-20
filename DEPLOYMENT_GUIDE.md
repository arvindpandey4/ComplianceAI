# 🚀 Deployment Guide (Free Tier)

This guide will help you deploy **ComplianceAI** completely for free using **Vercel** (Frontend) and **Render** (Backend).

---

## 🏗️ Phase 1: Deploy Backend (Render)

We deploy the backend first to get the API URL, which we'll need for the frontend.

1.  **Sign Up/Login**: Go to [dashboard.render.com](https://dashboard.render.com/) and log in (GitHub recommended).
2.  **Create New Web Service**:
    *   Click **"New +"** -> **"Web Service"**.
    *   Select "Build and deploy from a Git repository".
    *   Connect your `ComplianceAI` repository.
3.  **Configure Service**:
    *   **Name**: `compliance-ai-backend` (or unique name).
    *   **Region**: Pick the one closest to you.
    *   **Branch**: `master`
    *   **Root Directory**: `backend` (Important! This tells Render where the Python app is).
    *   **Runtime**: **Python 3**.
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
    *   **Instance Type**: **Free**.
4.  **Environment Variables** (Scroll down to "Environment Variables"):
    Add the following keys (Copy values from your local `.env`):
    *   `MONGODB_URI`: (Your MongoDB Atlas connection string)
    *   `GROQ_API_KEY`: (Your Groq API Key)
    *   `SECRET_KEY`: (Any random string for security)
    *   `PYTHON_VERSION`: `3.9.18` (Recommended to ensure compatibility)
5.  **Deploy**: Click **"Create Web Service"**.
    *   *Note: The first build might take a few minutes. Wait for "Live" status.*
    *   *Warning: Render free tier spins down after inactivity. The first request after a break will take ~50 seconds to load.*

**✅ Copy your Backend URL**: Once live, copy the URL (e.g., `https://compliance-ai-backend.onrender.com`).

---

## 🎨 Phase 2: Deploy Frontend (Vercel)

1.  **Sign Up/Login**: Go to [vercel.com](https://vercel.com/) and log in with GitHub.
2.  **Add New Project**:
    *   Click **"Add New..."** -> **"Project"**.
    *   Import your `ComplianceAI` repository.
3.  **Configure Project**:
    *   **Framework Preset**: Vite (should be auto-detected).
    *   **Root Directory**: Click "Edit" and select `frontend`.
4.  **Environment Variables**:
    *   You likely have hardcoded `http://127.0.0.1:8000` in your frontend code. **We need to update this first.**
    *   *Action Required*: Before deploying, we'll update the frontend to use the Production API URL dynamically.

---

## 🔧 Critical Code Update Before Deploying Frontend!

We need to make sure your Frontend talks to the hosted Backend, not `localhost`.

### 1. Update Frontend API Calls
I have updated your frontend to use a base URL configuration. If I haven't, I will do it automatically now.

**Action for AI (Internal)**: I will create a `frontend/src/api/config.js` or similar to manage the base URL based on `import.meta.env.VITE_API_URL`.

### 2. Commit & Push
After I make these changes, you will need to push them to GitHub.

---

## 🚀 Final Steps

1.  After the code update (which I will do next), push the changes:
    ```bash
    git add .
    git commit -m "chore: prepare for deployment"
    git push origin master
    ```
2.  **Finish Vercel Deployment**:
    *   Go back to Vercel setup.
    *   Add Environment Variable: `VITE_API_URL` = `https://your-backend-name.onrender.com/api/v1` (The URL you copied from Render + `/api/v1`).
    *   Click **Deploy**.

**🎉 Success!** Your app is now live.
