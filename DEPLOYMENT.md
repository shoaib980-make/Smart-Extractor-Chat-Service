# Deployment Guide: Smart Extractor & Chat Service

Deploy both the React frontend and FastAPI backend **100% free on Vercel** with **NO credit card required**.

---

## Architecture Overview

* **Frontend:** React + Vite (Static build served by Vercel CDN)
* **Backend:** FastAPI Serverless Function (`api/index.py` served by Vercel Python runtime)
* **Routing:** Unified on a single Vercel domain using `vercel.json` rewrites (`/api/*` -> FastAPI serverless, other paths -> React SPA)

---

## 1-Click Free Deployment on Vercel (No Credit Card)

### 1. Push code to GitHub
Make sure all repository changes are pushed:
```bash
git add .
git commit -m "Configure fullstack Vercel deployment with serverless FastAPI"
git push origin main
```

### 2. Configure Vercel Project
1. Go to [Vercel.com](https://vercel.com) and sign in (using GitHub).
2. Select your repository: `Smart-Extractor-Chat-Service`.
3. In the project setup settings:
   - **Root Directory:** Leave as `./` (the root repository directory). *If you previously set it to `frontend`, reset it to `./` in Project Settings > General > Root Directory.*
   - **Framework Preset:** `Other` (or auto-detected; `vercel.json` handles the build).
4. Expand **Environment Variables** and add:
   - `OPENROUTER_API_KEY`: `your_openrouter_api_key`
   - `OPENROUTER_MODEL`: `openrouter/free`
   - `OPENROUTER_INPUT_PRICE_PER_MILLION`: `0`
   - `OPENROUTER_OUTPUT_PRICE_PER_MILLION`: `0`
   - `VERCEL_FORCE_PYTHON_STREAMING`: `1`
5. Click **Deploy**.

---

## Verification

Once deployed, visit your live Vercel URL (e.g., `https://smart-extractor-chat-service-t43b.vercel.app`):
- **Frontend Web App:** `https://your-project.vercel.app/`
- **Backend Health Check:** `https://your-project.vercel.app/api/health`
- **API Swagger Documentation:** `https://your-project.vercel.app/api/docs`

Both the React UI and the FastAPI backend now run on the same HTTPS domain with zero CORS issues and zero credit card requirements.
