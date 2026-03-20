# SGB Custom Painting Calculator — Setup & Deployment Guide

**Built by Peterson SEO** | [petersonseoconsulting.com](https://www.petersonseoconsulting.com)

---

## Files in This Package

| File | Purpose |
|------|---------|
| `index.html` | The calculator itself — this is the iframe file for Snapps |
| `server.py` | Email backend (Flask + Resend) — deployed to Railway |
| `admin.html` | Admin panel to update pricing without touching code |
| `email-preview.html` | Preview of both customer and lead notification emails |
| `verify.html` | Math verification sheet — check all pricing scenarios |
| `scotts-numbers-checklist.html` | Printable checklist to collect Scott's actual prices |

---

## Step 1: Set Up Resend (Email Sending)

1. Go to [resend.com](https://resend.com) and create a free account
2. Click **"Add Domain"** and enter: `sgbpainting.com`
3. Resend will give you 2-3 DNS records (TXT + CNAME values)
4. Log in to wherever sgbpainting.com's DNS is managed (likely Snapps or GoDaddy)
5. Add those DNS records exactly as shown
6. Wait 5-15 minutes, then click **"Verify"** in Resend
7. Once verified, go to **API Keys** and click **"Create API Key"**
8. Copy the key (starts with `re_`) — you will need it in Step 3

> **Note:** The free Resend plan allows 3,000 emails/month and 100/day. More than enough for lead generation.

---

## Step 2: Deploy the Email Backend to Railway (Free)

1. Go to [railway.app](https://railway.app) and sign up with GitHub (free)
2. Click **"New Project"** → **"Deploy from GitHub repo"**
   - Or use **"Deploy from template"** → select Python/Flask
3. Upload the `server.py` file to the project
4. Railway will auto-detect it as a Python app and deploy it
5. Once deployed, Railway gives you a public URL like:
   `https://sgb-calculator-production.up.railway.app`
6. Copy that URL — you will need it in Step 3

**Alternative (even simpler):** Use [Render.com](https://render.com) free tier:
1. Create account → New Web Service → Upload `server.py`
2. Set Start Command to: `python server.py`
3. Deploy and copy the public URL

---

## Step 3: Add the Resend API Key to the Backend

Once your backend is deployed on Railway or Render:

1. In Railway/Render dashboard, go to **Environment Variables**
2. Add a new variable:
   - **Name:** `RESEND_API_KEY`
   - **Value:** `re_xxxxxxxxxxxxxxxxx` (your key from Step 1)
3. Save and redeploy

---

## Step 4: Connect the Calculator to the Backend

Open `index.html` in a text editor and find this line (around line 1391):

```
const response = await fetch('BACKEND_URL_PLACEHOLDER/send-estimate', {
```

Replace `BACKEND_URL_PLACEHOLDER` with your Railway/Render URL:

```
const response = await fetch('https://sgb-calculator-production.up.railway.app/send-estimate', {
```

Save the file.

---

## Step 5: Embed on Snapps Website

1. In Snapps, add a new page (e.g., "Painting Cost Estimator")
2. Add an **HTML/Embed block** to the page
3. Paste this iframe code:

```html
<iframe
  src="URL_WHERE_YOU_HOST_INDEX.HTML"
  width="100%"
  height="900"
  frameborder="0"
  scrolling="auto"
  style="border:none; max-width:860px; display:block; margin:0 auto;">
</iframe>
```

**Where to host `index.html`:**
- Upload it to the same Railway/Render server (add a static file route)
- Or host it on any static host: Netlify (free), GitHub Pages (free), or Cloudflare Pages (free)
- The simplest option: upload `index.html` directly to Snapps as a custom file and reference it

---

## Step 6: Update Pricing with Scott's Numbers

**Option A — Admin Panel (no coding):**
1. Open `admin.html` in a browser
2. Password: `sgbadmin2024` (change this before sharing with Scott)
3. Update all prices in the form
4. Click "Generate Code" and copy the output
5. Paste it into `index.html` replacing the existing pricing block

**Option B — Direct edit:**
Open `index.html` and find the section starting with `// ===== PRICING TABLES =====`
Update the numbers directly. Each room/item has three values: `good`, `better`, `best`.

---

## Email Configuration

Both emails (customer confirmation and Scott's lead notification) are sent automatically when a customer submits the form.

To change email addresses, open `server.py` and update these lines near the top:

```python
SCOTT_EMAIL      = "scott@sgbpainting.com"       # Lead notifications go here
MARKETING_EMAIL  = "marketing@petersonseoconsulting.com"  # CC on all leads
FROM_EMAIL       = "SGB Custom Painting <noreply@sgbpainting.com>"
```

---

## Testing Checklist

- [ ] Resend domain verified for sgbpainting.com
- [ ] Backend deployed and running (test: visit `YOUR_URL/health` — should return `{"status":"ok"}`)
- [ ] `BACKEND_URL_PLACEHOLDER` replaced in `index.html`
- [ ] Test submission with your own email — confirm both emails arrive
- [ ] Pricing updated with Scott's actual numbers
- [ ] iframe embedded on Snapps page
- [ ] Mobile view tested on phone

---

## Support

Questions or updates? Contact Peterson SEO at [petersonseoconsulting.com](https://www.petersonseoconsulting.com)
