# paired-devices.py

import os
import toml
import json
import requests
from datetime import datetime

# Load the configuration file
config_file = "secret.toml"
if not os.path.exists(config_file):
    print(f"Error: Configuration file '{config_file}' does not exist.")
    exit()

# Read the config file
config = toml.load(config_file)
api_key = config.get("API_KEY")
ip_address = config.get("ip")

# Check if API_KEY and ip address exist in the config
if not api_key or not ip_address:
    print("Error: Missing API_KEY or ip address in the configuration file.")
    exit()

# Define the request URL
url = f"http://{ip_address}/api/{api_key}/lights"

# Make the API request
try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    # Format and save the response as a JSON file with a timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"paired-devices_{timestamp}.json"
    with open(filename, "w") as json_file:
        json.dump(data, json_file, indent=4)

    print(f"Data saved to '{filename}'.")

except requests.exceptions.RequestException as e:
    print(f"Error making request: {e}")
