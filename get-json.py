# get-json.py

import os
import toml
import json
import requests
from datetime import datetime

# Ensure the JSON output directory exists
json_dir = "json"
os.makedirs(json_dir, exist_ok=True)

# Define the filename for the configuration
config_file = "secret.toml"

# Function to create secret.toml if it doesn't exist
def create_secret():
    if os.path.exists(config_file):
        print(f"The file '{config_file}' already exists.")
        return

    api_key = input("Enter the deCONZ API key: ").strip()
    ip_address = input("Enter the IP address of the Zigbee gateway server: ").strip()

    config_content = {
        "API_KEY": api_key,
        "ip": ip_address
    }

    with open(config_file, "w") as file:
        toml.dump(config_content, file)

    print(f"'{config_file}' has been created with the provided details.")

# Function to load configuration from secret.toml
def load_config():
    if not os.path.exists(config_file):
        print(f"Error: Configuration file '{config_file}' does not exist.")
        create_secret()
    
    config = toml.load(config_file)
    api_key = config.get("API_KEY")
    ip_address = config.get("ip")

    if not api_key or not ip_address:
        print("Error: Missing 'API_KEY' or 'ip' in the configuration file.")
        exit()
    
    return api_key, ip_address

# Function to fetch data from a given URL and save to a file in the JSON directory
def fetch_and_save(url, filename):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        filepath = os.path.join(json_dir, filename)
        with open(filepath, "w") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data saved to '{filepath}'.")

    except requests.exceptions.RequestException as e:
        print(f"Error making request to {url}: {e}")

# Main function to run all API fetch operations
def main():
    # Load configuration
    api_key, ip_address = load_config()

    # Define API URLs for each data type
    urls = {
        "root-api.json": f"http://{ip_address}/api/{api_key}/",
        "paired-devices.json": f"http://{ip_address}/api/{api_key}/lights",
        "existing-groups.json": f"http://{ip_address}/api/{api_key}/groups",
        "existing-schedules.json": f"http://{ip_address}/api/{api_key}/schedules"
    }

    # Fetch data and save each JSON file
    for filename, url in urls.items():
        fetch_and_save(url, filename)

if __name__ == "__main__":
    main()
