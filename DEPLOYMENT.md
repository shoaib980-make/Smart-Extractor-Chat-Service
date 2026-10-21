# Deployment Guide: Smart Extractor & Chat Service

This guide provides simple, free instructions to deploy the FastAPI backend and React frontend live to the web.

---

## Architecture Overview

* **Backend:** FastAPI + Uvicorn + Pydantic (Deployable on Render, Railway, or Fly.io)
* **Frontend:** React + Vite (Deployable on Vercel or Netlify)

---

## 1. Deploy the Backend (FastAPI on Render.com)

1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Complete Week 2 project deliverables"
   git push origin main
   ```
2. Log into [Render.com](https://render.com) and click **New + > Web Service**.
3. Connect your GitHub repository: `Smart-Extractor-Chat-Service`.
4. Configure the Web Service settings:
   - **Name:** `smart-extractor-api`
   - **Root Directory:** `python_lab`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python -m uvicorn main:app --host 0.0.0.0 --port 10000`
5. Under **Environment Variables**, add:
   - `OPENROUTER_API_KEY`: `your_openrouter_api_key`
   - `OPENROUTER_MODEL`: `openrouter/free`
   - `OPENROUTER_INPUT_PRICE_PER_MILLION`: `0`
   - `OPENROUTER_OUTPUT_PRICE_PER_MILLION`: `0`
6. Click **Deploy Web Service**.
7. Copy your live backend URL (e.g. `https://smart-extractor-api.onrender.com`).

---

## 2. Deploy the Frontend (React / Vite on Vercel)

1. Log into [Vercel.com](https://vercel.com) and click **Add New > Project**.
2. Select your repository `Smart-Extractor-Chat-Service`.
3. Configure the Project:
   - **Framework Preset:** `Vite`
   - **Root Directory:** Click edit and select `frontend`.
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. In `frontend/src/App.jsx`, update the `API` constant to your live Render backend URL:
   ```javascript
   const API = import.meta.env.VITE_API_URL || "https://smart-extractor-api.onrender.com";
   ```
5. Click **Deploy**.
6. Your frontend is now live with a public URL!

---

## 3. Verify Live Deployment

Test the live public URLs:
- **API Swagger Docs:** `https://your-backend.onrender.com/docs`
- **Health Check:** `https://your-backend.onrender.com/health`
- **Frontend Live App:** `https://your-frontend.vercel.app`
