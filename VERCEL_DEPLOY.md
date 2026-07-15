# Gescon Vercel Deployment Guide

This guide explains how to deploy the Gescon Reflex frontend on Vercel while keeping the **Desktop OS Control** functional via your local Python environment.

---

## 1. Architecture Design (Hybrid Client-Local Model)

* **Vercel Frontend:** Hosts the user interface, setup pages, and the **live browser camera demo** (which tracks hand landmarks directly on-device in the visitor's browser using MediaPipe WebAssembly).
* **Local Backend:** When the visitor clicks "Launch OS Controller", the website connects to `http://localhost:8000`. If you have the Gescon Python backend running locally, it launches the desktop controller (`Project.py`) to steer your cursor.

---

## 2. Option A: GitHub Git-Push Deployment (Recommended & Automatic)

We have configured the repository's `.gitignore` rules so that the final compiled static build folder (`.web/build/client/`) is committed and pushed to GitHub. This enables Vercel's automatic deployment on every push!

### Steps to set up Vercel:
1. Go to your [Vercel Dashboard](https://vercel.com/dashboard) and click **Add New > Project**.
2. Import your GitHub repository: `sarthak-allawadhi/Gescon`.
3. In the **Configure Project** settings, expand the **Build and Development Settings** and configure the following:
   * **Root Directory:** Click "Edit" and select `.web/build/client` (or type `.web/build/client`).
   * **Build Command:** Leave it empty (or toggled Off) so Vercel doesn't attempt to run a build command.
   * **Output Directory:** Leave it empty (or toggled Off).
4. Click **Deploy**.
5. Vercel will serve your pre-compiled HTML and Javascript files directly at the root, and the site will render perfectly (no blank page!).

*Note: Whenever you make changes locally, run the local compilation (`build-frontend.bat` or `reflex export --frontend-only`) and push the changes to GitHub to trigger Vercel updates automatically.*

---

## 3. Option B: Deploying via Vercel CLI (Manual)

If you don't want to use GitHub and prefer deploying directly from your terminal:

### Prerequisites
Make sure you have [Node.js](https://nodejs.org/) installed and the Vercel CLI:
```bash
npm install -g vercel
```

### Steps:
1. Run `build-frontend.bat` (or `python -m reflex export --frontend-only`) to compile.
2. Run the deployment command in your terminal from the project root:
   ```bash
   vercel deploy --prod .web/build/client
   ```
3. Follow the Vercel prompts to deploy.

---

## 4. How to Use Desktop OS Control

Once your website is deployed on Vercel:
1. Visit your Vercel URL in your browser.
2. The browser-based webcam sandbox works out of the box.
3. To control your operating system mouse cursor:
   * Start your local backend server:
     ```bash
     venv\Scripts\activate
     reflex run
     ```
   * Open the **Live Demo** tab on your Vercel site. The status badge will change from **DISCONNECTED** to **ACTIVE (OS Control)**.
   * Click **Launch OS Controller** to start the native tracking script!
