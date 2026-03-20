"""
SGB Custom Painting - Estimate Email Backend
Vercel Serverless Function
Uses Resend to send:
  1. Lead notification to scott@sgbpainting.com (CC marketing)
  2. Confirmation email to the customer
Also logs lead to Google Sheets.
"""

import os
import json
import datetime
import requests as http_requests
from http.server import BaseHTTPRequestHandler
import resend
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ===== CONFIG =====
RESEND_API_KEY   = os.environ.get("RESEND_API_KEY", "")
FROM_EMAIL       = "SGB Custom Painting <noreply@sgbpainting.com>"
SCOTT_EMAIL      = "scott@sgbpainting.com"
MARKETING_EMAIL  = "marketing@petersonseoconsulting.com"
ZAPIER_WEBHOOK   = os.environ.get("ZAPIER_WEBHOOK_URL", "")

# Google Sheets config
SHEET_ID   = "110OqlqHTAZ3g8D7LHLAGkSj6ijtefdZ9uGL7-8e_Ono"
SHEET_NAME = "SGB Painting Calculator Leads"
GOOGLE_CREDS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON", "")

resend.api_key = RESEND_API_KEY


# ===== GOOGLE SHEETS CLIENT =====
def get_sheets_service():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds_dict = json.loads(GOOGLE_CREDS_JSON)
    creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return build("sheets", "v4", credentials=creds)

def log_to_sheets(data):
    try:
        service = get_sheets_service()
        sheet = service.spreadsheets()
        rooms_text = build_rooms_text(data)
        addons = []
        for key in ["wallpaper", "popcorn", "repairs-minor", "repairs-moderate",
                    "powerwash", "ext-repairs", "deck", "trim-accent",
                    "face-frames", "hardware"]:
            if data.get("addons", {}).get(key):
                addons.append(key.replace("-", " ").title())
        addons_text = ", ".join(addons) if addons else "None"
        row = [
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data.get("name", ""),
            data.get("email", ""),
            data.get("phone", ""),
            data.get("address", ""),
            fmt_project_type(data.get("projectType", "")),
            fmt_tier(data.get("paintTier", "")),
            fmt_size(data.get("homeSize", "")),
            rooms_text,
            data.get("cabDoors", 0),
            data.get("cabDrawers", 0),
            addons_text,
            data.get("estimateLow", 0),
            data.get("estimateHigh", 0),
            f"{fmt_currency(data.get('estimateLow',0))} - {fmt_currency(data.get('estimateHigh',0))}",
            data.get("notes", ""),
            "SGB Painting Cost Calculator"
        ]
        sheet.values().append(
            spreadsheetId=SHEET_ID,
            range=f"{SHEET_NAME}!A:Q",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [row]}
        ).execute()
        return True
    except Exception as e:
        print(f"Google Sheets error: {e}")
        return False


# ===== HELPERS =====
def fmt_currency(n):
    return "${:,.0f}".format(n)

def fmt_project_type(t):
    return {"interior": "Interior Painting", "exterior": "Exterior Painting", "cabinet": "Cabinet Painting"}.get(t, t.title())

def fmt_tier(t):
    return {"good": "Good (Sherwin-Williams SuperPaint/Duration)", "better": "Better (SW Emerald / BM Regal Select)", "best": "Best (BM Aura / Dunn-Edwards Evershield)"}.get(t, t.title())

def fmt_size(s):
    return {"small": "Small Home (under 1,200 sq ft)", "medium": "Medium Home (1,200-1,800 sq ft)", "large": "Large Home (1,800-2,500 sq ft)", "xlarge": "Extra Large Home (2,500+ sq ft)"}.get(s, s)

def build_rooms_text(data):
    room_labels = {
        "small-bed": "Small Bedroom", "std-bed": "Standard Bedroom",
        "master-bed": "Master Bedroom", "living": "Living Room",
        "dining": "Dining Room", "kitchen": "Kitchen",
        "bath-sm": "Small Bathroom", "bath-master": "Master Bathroom",
        "hallway": "Hallway / Entry", "office": "Office / Den",
        "stair": "Stairwell / Landing"
    }
    lines = []
    for key, label in room_labels.items():
        qty = data.get("rooms", {}).get(key, 0)
        if qty > 0:
            lines.append(f"{qty}x {label}")
    return ", ".join(lines) if lines else "N/A"

def build_breakdown_html(items):
    rows = ""
    for item in items:
        rows += f"""
        <tr>
          <td style="padding:8px 12px;border-bottom:1px solid #e8edf2;font-size:14px;color:#333;">{item['name']}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #e8edf2;font-size:14px;font-weight:600;color:#052D5C;text-align:right;">{fmt_currency(item['low'])} - {fmt_currency(item['high'])}</td>
        </tr>"""
    return rows


# ===== SCOTT LEAD EMAIL =====
def build_scott_email(data):
    breakdown_rows = build_breakdown_html(data.get("breakdown", []))
    rooms_html = ""
    if data.get("projectType") == "interior":
        room_labels = {
            "small-bed": "Small Bedroom", "std-bed": "Standard Bedroom",
            "master-bed": "Master Bedroom", "living": "Living Room",
            "dining": "Dining Room", "kitchen": "Kitchen",
            "bath-sm": "Small Bathroom", "bath-master": "Master Bathroom",
            "hallway": "Hallway / Entry", "office": "Office / Den",
            "stair": "Stairwell / Landing"
        }
        for key, label in room_labels.items():
            qty = data.get("rooms", {}).get(key, 0)
            if qty > 0:
                rooms_html += f"<li>{qty}x {label}</li>"

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"/></head>
<body style="margin:0;padding:0;background:#f0f4f8;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f4f8;padding:30px 0;">
  <tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(5,45,92,0.10);">
      <tr><td style="background:#052D5C;padding:24px 28px;">
        <h1 style="color:#ffffff;font-size:20px;margin:0;">New Painting Estimate Lead</h1>
        <p style="color:rgba(255,255,255,0.75);font-size:13px;margin:6px 0 0;">SGB Custom Painting - Cost Calculator</p>
      </td></tr>
      <tr><td style="background:#D91D23;padding:12px 28px;">
        <p style="color:#ffffff;font-size:14px;font-weight:600;margin:0;">Action Required: New lead submitted - follow up within 24 hours</p>
      </td></tr>
      <tr><td style="padding:24px 28px 0;">
        <h2 style="color:#052D5C;font-size:16px;margin:0 0 14px;border-bottom:2px solid #052D5C;padding-bottom:8px;">Contact Information</h2>
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr><td style="padding:6px 0;font-size:14px;color:#5a6a7e;width:130px;">Name</td><td style="padding:6px 0;font-size:14px;font-weight:600;color:#1a1a2e;">{data.get('name','N/A')}</td></tr>
          <tr><td style="padding:6px 0;font-size:14px;color:#5a6a7e;">Phone</td><td style="padding:6px 0;font-size:14px;font-weight:600;color:#1a1a2e;">{data.get('phone','N/A')}</td></tr>
          <tr><td style="padding:6px 0;font-size:14px;color:#5a6a7e;">Email</td><td style="padding:6px 0;font-size:14px;font-weight:600;color:#1a1a2e;">{data.get('email','N/A')}</td></tr>
          <tr><td style="padding:6px 0;font-size:14px;color:#5a6a7e;">Address</td><td style="padding:6px 0;font-size:14px;color:#1a1a2e;">{data.get('address','Not provided')}</td></tr>
        </table>
      </td></tr>
      <tr><td style="padding:20px 28px 0;">
        <h2 style="color:#052D5C;font-size:16px;margin:0 0 14px;border-bottom:2px solid #052D5C;padding-bottom:8px;">Project Details</h2>
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr><td style="padding:6px 0;font-size:14px;color:#5a6a7e;width:130px;">Project Type</td><td style="padding:6px 0;font-size:14px;font-weight:600;color:#1a1a2e;">{fmt_project_type(data.get('projectType',''))}</td></tr>
          <tr><td style="padding:6px 0;font-size:14px;color:#5a6a7e;">Paint Tier</td><td style="padding:6px 0;font-size:14px;color:#1a1a2e;">{fmt_tier(data.get('paintTier',''))}</td></tr>
          {f'<tr><td style="padding:6px 0;font-size:14px;color:#5a6a7e;">Home Size</td><td style="padding:6px 0;font-size:14px;color:#1a1a2e;">{fmt_size(data.get("homeSize",""))}</td></tr>' if data.get("homeSize") else ""}
          {f'<tr><td style="padding:6px 0;font-size:14px;color:#5a6a7e;">Cabinet Doors</td><td style="padding:6px 0;font-size:14px;color:#1a1a2e;">{data.get("cabDoors",0)}</td></tr>' if data.get("projectType")=="cabinet" else ""}
          {f'<tr><td style="padding:6px 0;font-size:14px;color:#5a6a7e;">Drawer Faces</td><td style="padding:6px 0;font-size:14px;color:#1a1a2e;">{data.get("cabDrawers",0)}</td></tr>' if data.get("projectType")=="cabinet" else ""}
        </table>
        {f'<p style="font-size:13px;color:#5a6a7e;margin:10px 0 0;">Rooms selected:</p><ul style="font-size:13px;color:#1a1a2e;margin:4px 0 0;padding-left:18px;">{rooms_html}</ul>' if rooms_html else ""}
      </td></tr>
      <tr><td style="padding:20px 28px 0;">
        <h2 style="color:#052D5C;font-size:16px;margin:0 0 14px;border-bottom:2px solid #052D5C;padding-bottom:8px;">Estimate Shown to Customer</h2>
        <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e8edf2;border-radius:8px;overflow:hidden;">
          <thead><tr style="background:#052D5C;">
            <th style="padding:10px 12px;text-align:left;color:#fff;font-size:13px;">Line Item</th>
            <th style="padding:10px 12px;text-align:right;color:#fff;font-size:13px;">Range</th>
          </tr></thead>
          <tbody>
            {breakdown_rows}
            <tr style="background:#EEF4FB;">
              <td style="padding:10px 12px;font-size:14px;font-weight:700;color:#052D5C;">TOTAL ESTIMATE</td>
              <td style="padding:10px 12px;font-size:14px;font-weight:700;color:#052D5C;text-align:right;">{fmt_currency(data.get('estimateLow',0))} - {fmt_currency(data.get('estimateHigh',0))}</td>
            </tr>
          </tbody>
        </table>
      </td></tr>
      {f'<tr><td style="padding:16px 28px 0;"><h2 style="color:#052D5C;font-size:16px;margin:0 0 10px;">Customer Notes</h2><p style="font-size:14px;color:#333;background:#f5f7fa;padding:12px;border-radius:8px;border-left:3px solid #2D71AE;">{data.get("notes","")}</p></td></tr>' if data.get("notes") else ""}
      <tr><td style="padding:20px 28px 24px;">
        <p style="font-size:12px;color:#999;margin:0;text-align:center;">Lead generated via the SGB Custom Painting Cost Calculator. Built by <a href="https://www.petersonseoconsulting.com" style="color:#2D71AE;">Peterson SEO</a>.</p>
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>"""


# ===== CUSTOMER CONFIRMATION EMAIL =====
def build_customer_email(data):
    breakdown_rows = build_breakdown_html(data.get("breakdown", []))
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"/></head>
<body style="margin:0;padding:0;background:#f0f4f8;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f4f8;padding:30px 0;">
  <tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(5,45,92,0.10);">
      <tr><td style="background:#052D5C;padding:28px 28px 22px;text-align:center;">
        <h1 style="color:#ffffff;font-size:22px;margin:0 0 6px;">Your Painting Estimate is Ready!</h1>
        <p style="color:rgba(255,255,255,0.78);font-size:14px;margin:0;">SGB Custom Painting | Chico, CA | 530-924-4109</p>
      </td></tr>
      <tr><td style="padding:26px 28px 0;">
        <p style="font-size:15px;color:#1a1a2e;margin:0 0 12px;">Hi {data.get('name','there')},</p>
        <p style="font-size:14px;color:#333;line-height:1.6;margin:0 0 12px;">Thank you for using the SGB Custom Painting cost estimator! Based on the details you provided, here is your personalized estimate range for your <strong>{fmt_project_type(data.get('projectType',''))}</strong> project.</p>
        <p style="font-size:14px;color:#333;line-height:1.6;margin:0;">A member of our team will be reaching out to you shortly to discuss your project in more detail and provide you with an accurate, no-surprise written quote.</p>
      </td></tr>
      <tr><td style="padding:20px 28px 0;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background:linear-gradient(135deg,#052D5C,#0a4a8c);border-radius:10px;overflow:hidden;">
          <tr><td style="padding:20px;text-align:center;">
            <p style="color:rgba(255,255,255,0.8);font-size:13px;margin:0 0 6px;">Your Estimated Project Range</p>
            <p style="color:#ffffff;font-size:28px;font-weight:800;margin:0;">{fmt_currency(data.get('estimateLow',0))} - {fmt_currency(data.get('estimateHigh',0))}</p>
            <p style="color:rgba(255,255,255,0.65);font-size:12px;margin:8px 0 0;">Based on current Northern California market rates</p>
          </td></tr>
        </table>
      </td></tr>
      <tr><td style="padding:20px 28px 0;">
        <h2 style="color:#052D5C;font-size:16px;margin:0 0 12px;border-bottom:2px solid #052D5C;padding-bottom:8px;">Estimate Breakdown</h2>
        <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e8edf2;border-radius:8px;overflow:hidden;">
          <thead><tr style="background:#052D5C;">
            <th style="padding:10px 12px;text-align:left;color:#fff;font-size:13px;">Line Item</th>
            <th style="padding:10px 12px;text-align:right;color:#fff;font-size:13px;">Range</th>
          </tr></thead>
          <tbody>
            {breakdown_rows}
            <tr style="background:#EEF4FB;">
              <td style="padding:10px 12px;font-size:14px;font-weight:700;color:#052D5C;">TOTAL ESTIMATE</td>
              <td style="padding:10px 12px;font-size:14px;font-weight:700;color:#052D5C;text-align:right;">{fmt_currency(data.get('estimateLow',0))} - {fmt_currency(data.get('estimateHigh',0))}</td>
            </tr>
          </tbody>
        </table>
      </td></tr>
      <tr><td style="padding:16px 28px 0;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#FFF8E1;border:1px solid #FFE082;border-radius:8px;">
          <tr><td style="padding:14px 16px;">
            <p style="font-size:13px;color:#5D4037;margin:0;line-height:1.6;"><strong>Please note: THIS IS ONLY AN ESTIMATE and not a formal quote.</strong> Pricing may vary based on project conditions, surface prep requirements, and material selection. Contact SGB Custom Painting for a formal, no-obligation quote.</p>
          </td></tr>
        </table>
      </td></tr>
      <tr><td style="padding:20px 28px 0;">
        <h2 style="color:#052D5C;font-size:16px;margin:0 0 12px;">Why Choose SGB Custom Painting?</h2>
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr><td style="padding:6px 0;font-size:14px;color:#333;">&#10003; &nbsp;25+ Years of Experience in Chico and Northern California</td></tr>
          <tr><td style="padding:6px 0;font-size:14px;color:#333;">&#10003; &nbsp;Licensed, Insured and EPA Lead Safe Certified</td></tr>
          <tr><td style="padding:6px 0;font-size:14px;color:#333;">&#10003; &nbsp;PDCA Accredited - Professional Painting Standards</td></tr>
          <tr><td style="padding:6px 0;font-size:14px;color:#333;">&#10003; &nbsp;No-Surprise Estimates and Transparent Pricing</td></tr>
          <tr><td style="padding:6px 0;font-size:14px;color:#333;">&#10003; &nbsp;Premium Paints from Sherwin-Williams, Benjamin Moore and Dunn-Edwards</td></tr>
        </table>
      </td></tr>
      <tr><td style="padding:22px 28px 0;text-align:center;">
        <a href="tel:5309244109" style="display:inline-block;background:#D91D23;color:#ffffff;text-decoration:none;padding:13px 32px;border-radius:7px;font-weight:700;font-size:15px;">Call Us: 530-924-4109</a>
        &nbsp;&nbsp;
        <a href="https://www.sgbpainting.com" style="display:inline-block;background:#052D5C;color:#ffffff;text-decoration:none;padding:13px 32px;border-radius:7px;font-weight:700;font-size:15px;">Visit Our Website</a>
      </td></tr>
      <tr><td style="padding:22px 28px 24px;border-top:1px solid #e8edf2;margin-top:20px;">
        <p style="font-size:12px;color:#999;margin:0;text-align:center;line-height:1.6;">SGB Custom Painting | Chico, CA | <a href="tel:5309244109" style="color:#2D71AE;">530-924-4109</a> | <a href="https://www.sgbpainting.com" style="color:#2D71AE;">sgbpainting.com</a><br/>
        Estimate calculator built by <a href="https://www.petersonseoconsulting.com" style="color:#2D71AE;">Peterson SEO</a></p>
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>"""


# ===== VERCEL HANDLER =====
class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        data = json.loads(body)

        errors = []

        # 1. Send lead notification to Scott (CC marketing)
        try:
            resend.Emails.send({
                "from": FROM_EMAIL,
                "to": [SCOTT_EMAIL],
                "cc": [MARKETING_EMAIL],
                "subject": f"New Painting Lead: {data.get('name','Unknown')} - {fmt_project_type(data.get('projectType',''))} ({fmt_currency(data.get('estimateLow',0))}-{fmt_currency(data.get('estimateHigh',0))})",
                "html": build_scott_email(data)
            })
        except Exception as e:
            errors.append(f"Scott email failed: {str(e)}")

        # 2. Send confirmation to customer
        try:
            customer_email = data.get("email")
            if customer_email:
                resend.Emails.send({
                    "from": FROM_EMAIL,
                    "to": [customer_email],
                    "subject": f"Your SGB Custom Painting Estimate: {fmt_currency(data.get('estimateLow',0))} - {fmt_currency(data.get('estimateHigh',0))}",
                    "html": build_customer_email(data)
                })
        except Exception as e:
            errors.append(f"Customer email failed: {str(e)}")

        # 3. Log lead to Google Sheet
        try:
            log_to_sheets(data)
        except Exception as e:
            errors.append(f"Google Sheets logging failed: {str(e)}")

        # 4. Fire Zapier webhook (if configured)
        if ZAPIER_WEBHOOK:
            try:
                zapier_payload = {
                    "name": data.get("name", ""),
                    "email": data.get("email", ""),
                    "phone": data.get("phone", ""),
                    "address": data.get("address", ""),
                    "project_type": fmt_project_type(data.get("projectType", "")),
                    "paint_tier": fmt_tier(data.get("paintTier", "")),
                    "home_size": fmt_size(data.get("homeSize", "")),
                    "estimate_low": data.get("estimateLow", 0),
                    "estimate_high": data.get("estimateHigh", 0),
                    "estimate_range": f"{fmt_currency(data.get('estimateLow',0))} - {fmt_currency(data.get('estimateHigh',0))}",
                    "rooms_summary": build_rooms_text(data),
                    "source": "SGB Painting Cost Calculator"
                }
                http_requests.post(ZAPIER_WEBHOOK, json=zapier_payload, timeout=5)
            except Exception as e:
                errors.append(f"Zapier webhook failed: {str(e)}")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        if errors:
            self.wfile.write(json.dumps({"ok": False, "errors": errors}).encode())
        else:
            self.wfile.write(json.dumps({"ok": True}).encode())
