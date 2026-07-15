# Gescon Vercel Deployment Guide

This guide explains how to deploy the Gescon Reflex frontend on Vercel while keeping the **Desktop OS Control** functional via your local Python environment.

---

## 1. Architecture Design (Hybrid Client-Local Model)

* **Vercel Frontend:** Hosts the user interface, setup pages, and the **live browser camera demo** (which tracks hand landmarks directly on-device in the visitor's browser using MediaPipe WebAssembly).
* **Local Backend:** When the visitor clicks "Launch OS Controller", the website connects to `http://localhost:8000`. If you have the Gescon Python backend running locally, it launches the desktop controller (`Project.py`) to steer your cursor.

---

## 2. Deploying to Vercel (Recommended CLI Method)

Because Vercel's build servers run only Node.js (and do not have Python/Reflex installed), the easiest way to deploy is to compile the site locally and push the static build directly to Vercel.

### Prerequisites
Make sure you have [Node.js](https://nodejs.org/) installed and the Vercel CLI:
```bash
npm install -g vercel
```

### Steps:
1. **Compile the App:**
   Double-click the `build-frontend.bat` script in the root directory (or run `python -m reflex export --frontend-only`). This creates the `.web/build/client` directory and the `frontend.zip` backup file.
2. **Deploy to Vercel:**
   Open your terminal in the project root and run the following command to deploy the static build:
   ```bash
   vercel deploy --prod .web/build/client
   ```
3. Follow the Vercel prompts to log in (if not already logged in) and set up your project. Vercel will deploy the site and give you a public URL (e.g., `gescon.vercel.app`).

---

## 3. Alternative: Deploying via GitHub Actions

If you want automated deployments every time you push to GitHub, you can use a GitHub Actions workflow.

Create a `.github/workflows/deploy.yml` file with these steps:
1. Setup Python & Node.js.
2. Install Python requirements (`pip install -r requirements.txt`).
3. Run `python -m reflex export --frontend-only`.
4. Deploy the `.web/build/client` directory to Vercel using the [Vercel Action](https://github.com/marketplace/actions/vercel-action).

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
