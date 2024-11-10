# add-devices-to-group.py

import os
import toml
import json
import requests

# Define the filename for the configuration
config_file = "secret.toml"
json_dir = "json"
os.makedirs(json_dir, exist_ok=True)

# Function to load configuration from secret.toml
def load_config():
    if not os.path.exists(config_file):
        print(f"Error: Configuration file '{config_file}' does not exist.")
        exit()
    
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
        return data

    except requests.exceptions.RequestException as e:
        print(f"Error making request to {url}: {e}")
        return None

# Function to read existing groups and list them
def list_existing_groups(groups):
    print("\nExisting Groups:")
    for group_id, group_info in groups.items():
        group_name = group_info.get('name', 'Unknown')
        print(f"ID: {group_id}, Name: {group_name}")

# Function to read paired devices and list them
def list_paired_devices(devices):
    print("\nPaired Devices:")
    for device_id, device_info in devices.items():
        device_name = device_info.get('name', 'Unknown')
        print(f"ID: {device_id}, Name: {device_name}")

# Function to add devices to a group
def add_devices_to_group(api_key, ip_address, group_id, device_ids):
    url = f"http://{ip_address}/api/{api_key}/groups/{group_id}"

    # Fetch current group data
    try:
        response = requests.get(url)
        response.raise_for_status()
        group_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching group data from {url}: {e}")
        return False

    # Get current list of lights in the group
    current_lights = group_data.get('lights', [])
    # Add new device IDs to the list, avoiding duplicates
    updated_lights = list(set(current_lights + device_ids))

    data = {
        "lights": updated_lights
    }

    try:
        response = requests.put(url, json=data)
        response.raise_for_status()
        result = response.json()
        print(f"API Response: {result}")
        print(f"Devices {device_ids} have been added to group ID {group_id}.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error making request to {url}: {e}")
        return False

def main():
    # Load configuration
    api_key, ip_address = load_config()

    # Fetch latest data
    print("Fetching latest data...")
    urls = {
        "existing-groups.json": f"http://{ip_address}/api/{api_key}/groups",
        "paired-devices.json": f"http://{ip_address}/api/{api_key}/lights"
    }
    groups = fetch_and_save(urls["existing-groups.json"], "existing-groups.json")
    devices = fetch_and_save(urls["paired-devices.json"], "paired-devices.json")

    if not groups or not devices:
        print("Failed to fetch necessary data. Exiting.")
        return

    # List existing groups
    list_existing_groups(groups)

    # List paired devices
    list_paired_devices(devices)

    # Ask user to select a group
    group_id = input("\nEnter the ID of the group to which you want to add devices: ").strip()
    if group_id not in groups:
        print(f"Group ID '{group_id}' does not exist. Exiting.")
        return

    # Ask user for devices to add to the group
    device_ids_input = input("Enter the IDs of the devices to add to the group (comma-separated): ").split(',')

    # Clean up the device IDs and validate them
    device_ids = []
    for device_id in device_ids_input:
        device_id = device_id.strip()
        if device_id in devices:
            device_ids.append(device_id)
        else:
            print(f"Device ID '{device_id}' is not valid and will be ignored.")

    if not device_ids:
        print("No valid device IDs entered. Exiting.")
        return

    # Add devices to the group via API
    success = add_devices_to_group(api_key, ip_address, group_id, device_ids)
    if success:
        # Fetch the latest group data and save
        url = f"http://{ip_address}/api/{api_key}/groups"
        fetch_and_save(url, "existing-groups.json")
    else:
        print("Failed to add devices to the group.")

if __name__ == "__main__":
    main()
