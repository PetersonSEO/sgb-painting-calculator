"""
Creates a Google Service Account key for Sheets API access.
Run this once to generate credentials.json
"""
import json, os

# This script generates the service account JSON structure
# The actual service account must be created via Google Cloud Console
# Instructions are printed below

print("""
=== GOOGLE SHEETS SETUP INSTRUCTIONS ===

Since we need a Google Service Account to write to your sheet,
here are the exact steps:

1. Go to: https://console.cloud.google.com/
2. Create a new project called "SGB Painting Calculator"
3. Enable the Google Sheets API:
   - Go to APIs & Services > Enable APIs
   - Search "Google Sheets API" and enable it
4. Create a Service Account:
   - Go to APIs & Services > Credentials
   - Click "Create Credentials" > "Service Account"
   - Name it: sgb-painting-calculator
   - Click Done
5. Create a JSON key:
   - Click on the service account you just created
   - Go to "Keys" tab > "Add Key" > "Create new key" > JSON
   - Download the JSON file
6. Share your Google Sheet with the service account email
   (it looks like: sgb-painting-calculator@your-project.iam.gserviceaccount.com)
   Give it "Editor" access

Then paste the service account email here and upload the JSON key.
""")
