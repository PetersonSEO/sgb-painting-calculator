"""
Test Google Sheets API access and set up column headers.
"""
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

SHEET_ID = "110OqlqHTAZ3g8D7LHLAGkSj6ijtefdZ9uGL7-8e_Ono"
SHEET_NAME = "SGB Painting Calculator Leads"
CREDS_FILE = "/home/ubuntu/sgb_calculator/google_credentials.json"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds = service_account.Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
service = build("sheets", "v4", credentials=creds)
sheet = service.spreadsheets()

# First, rename Sheet1 to the correct tab name (if needed)
# Get current sheet names
meta = sheet.get(spreadsheetId=SHEET_ID).execute()
existing_sheets = [s["properties"]["title"] for s in meta["sheets"]]
print("Existing sheets:", existing_sheets)

# Rename first sheet if it's still "Sheet1"
if "Sheet1" in existing_sheets and SHEET_NAME not in existing_sheets:
    sheet_id_to_rename = meta["sheets"][0]["properties"]["sheetId"]
    body = {
        "requests": [{
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id_to_rename,
                    "title": SHEET_NAME
                },
                "fields": "title"
            }
        }]
    }
    sheet.batchUpdate(spreadsheetId=SHEET_ID, body=body).execute()
    print(f"Renamed Sheet1 to '{SHEET_NAME}'")

# Set up headers
headers = [
    "Timestamp", "Name", "Email", "Phone", "Address",
    "Project Type", "Paint Tier", "Home Size",
    "Rooms Selected", "Cabinet Doors", "Cabinet Drawers",
    "Prep Add-Ons", "Estimate Low", "Estimate High",
    "Estimate Range", "Notes", "Source"
]

result = sheet.values().get(
    spreadsheetId=SHEET_ID,
    range=f"{SHEET_NAME}!A1:Q1"
).execute()

existing = result.get("values", [])
if not existing or existing[0][0] != "Timestamp":
    sheet.values().update(
        spreadsheetId=SHEET_ID,
        range=f"{SHEET_NAME}!A1",
        valueInputOption="RAW",
        body={"values": [headers]}
    ).execute()
    print("Headers written successfully!")
else:
    print("Headers already exist:", existing[0])

# Test: write a sample row
import datetime
test_row = [
    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "TEST LEAD - DELETE",
    "test@example.com",
    "555-555-5555",
    "123 Test St, Chico CA",
    "Interior Painting",
    "Better (SW Emerald)",
    "N/A",
    "2x Standard Bedroom, 1x Living Room",
    0, 0,
    "Minor Drywall Repairs",
    1800, 2200,
    "$1,800 - $2,200",
    "This is a test row",
    "SGB Painting Cost Calculator"
]

sheet.values().append(
    spreadsheetId=SHEET_ID,
    range=f"{SHEET_NAME}!A:Q",
    valueInputOption="RAW",
    insertDataOption="INSERT_ROWS",
    body={"values": [test_row]}
).execute()
print("Test row written! Check your Google Sheet.")
print(f"Sheet URL: https://docs.google.com/spreadsheets/d/{SHEET_ID}")
