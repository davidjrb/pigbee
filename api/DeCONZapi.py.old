import json
import argparse
import requests
import toml

# Path to the TOML file
SECRET_FILE_PATH = "../secret.toml"

def fetch_and_parse_json(ip, api_key, payload):
    url = f"http://{ip}/api/{api_key}/{payload}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        data = response.json()
        print(json.dumps(data, indent=4))  # Print in a human-readable format
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and format JSON payload from a DeCONZ API.")
    parser.add_argument("-GET", dest="payload", required=True, help="API payload endpoint, e.g., 'groups'")
    args = parser.parse_args()
    
    # Load config from the specified TOML file
    config = toml.load(SECRET_FILE_PATH)
    ip = config.get("ip")
    api_key = config.get("API_KEY")
    
    if not ip or not api_key:
        print("Error: IP or API key not found in the TOML file.")
    else:
        fetch_and_parse_json(ip, api_key, args.payload)
