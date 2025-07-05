import requests
import yaml
import pandas as pd
import time

# Load the YAML API specification
with open("coursera-for-business-api-product.yaml", "r") as file:
    api_spec = yaml.safe_load(file)

# Extract base URL
base_url = api_spec.get("servers", [{}])[0].get("url", "")

# Collect all GET endpoints
paths = api_spec.get("paths", {})
get_endpoints = []

for path, methods in paths.items():
    if "get" in methods:
        get_endpoints.append({
            "path": path,
            "summary": methods["get"].get("summary", ""),
            "description": methods["get"].get("description", "")
        })

# Prepare Excel writer
writer = pd.ExcelWriter("api_scraped_data.xlsx", engine='openpyxl')
collected_data = []

# Iterate over endpoints and make requests
for index, ep in enumerate(get_endpoints, start=1):
    url = f"{base_url}{ep['path']}"
    safe_sheet_name = f"Sheet{index}"[:31]  # Excel sheet names must be <= 31 chars
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Convert JSON to DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            df = pd.json_normalize(data)
        else:
            df = pd.DataFrame([{"response": str(data)}])

        df.to_excel(writer, sheet_name=safe_sheet_name, index=False)

        collected_data.append({
            "Endpoint": url,
            "Status": "Success",
            "Sheet Name": safe_sheet_name,
            "Record Count": len(df)
        })

    except Exception as e:
        collected_data.append({
            "Endpoint": url,
            "Status": f"Error: {e}",
            "Sheet Name": "None",
            "Record Count": 0
        })

    time.sleep(1)

# Save summary sheet
summary_df = pd.DataFrame(collected_data)
summary_df.to_excel(writer, sheet_name="Summary", index=False)
writer.close()

print("✅ Scraping complete. Data saved to 'api_scraped_data.xlsx'") 
