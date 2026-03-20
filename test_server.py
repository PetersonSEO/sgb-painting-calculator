"""Quick test to verify server.py imports and Sheets integration work correctly."""
import sys
sys.path.insert(0, '/home/ubuntu/sgb_calculator')

# Set dummy env vars for test
import os
os.environ['RESEND_API_KEY'] = 'test_key'

# Test imports
from server import app, log_to_sheets, fmt_currency, fmt_project_type, fmt_tier

print("All imports OK")

# Test Sheets logging with sample data
test_data = {
    "name": "TEST DELETE",
    "email": "test@example.com",
    "phone": "530-555-1234",
    "address": "456 Oak Ave, Chico CA 95928",
    "projectType": "interior",
    "paintTier": "better",
    "homeSize": "",
    "rooms": {"std-bed": 2, "master-bed": 1, "living": 1, "bath-sm": 1},
    "addons": {"repairs-minor": True},
    "cabDoors": 0,
    "cabDrawers": 0,
    "estimateLow": 2400,
    "estimateHigh": 2950,
    "breakdown": [
        {"name": "2x Standard Bedroom", "low": 900, "high": 1100},
        {"name": "1x Master Bedroom", "low": 700, "high": 850},
        {"name": "1x Living Room", "low": 650, "high": 800},
        {"name": "1x Small Bathroom", "low": 150, "high": 200},
    ],
    "notes": "Server integration test - please delete"
}

result = log_to_sheets(test_data)
print(f"Sheets log result: {'SUCCESS' if result else 'FAILED'}")
print("Check your Google Sheet for a second test row.")
