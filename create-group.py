# create-group.py

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

# Function to update secret.toml with existing groups
def update_secret_with_groups(groups):
    config = toml.load(config_file)

    # Prepare groups data
    groups_dict = {}
    for group_id, group_info in groups.items():
        group_name = group_info.get('name', 'Unknown')
        groups_dict[group_name] = group_id

    # Update the config
    config['groups'] = groups_dict

    # Write back to secret.toml
    with open(config_file, 'w') as file:
        toml.dump(config, file)
    print("Updated 'secret.toml' with existing groups.")

# Function to create a new group
def create_group(api_key, ip_address, group_name, device_ids):
    url = f"http://{ip_address}/api/{api_key}/groups"

    data = {
        "name": group_name,
        "lights": device_ids  # Ensure device IDs are strings
    }

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        print(f"API Response: {result}")
        if isinstance(result, list) and 'success' in result[0]:
            group_id = result[0]['success']['id']
            print(f"Group '{group_name}' created with ID: {group_id}")
            return group_id
        else:
            print(f"Failed to create group: {result}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error making request to {url}: {e}")
        return None

# Function to add new group to secret.toml
def add_group_to_secret(group_id, group_name):
    config = toml.load(config_file)

    # Update the groups dictionary
    if 'groups' not in config:
        config['groups'] = {}

    config['groups'][group_name] = group_id

    # Write back to secret.toml
    with open(config_file, 'w') as file:
        toml.dump(config, file)
    print(f"Added new group '{group_name}' with ID '{group_id}' to 'secret.toml'.")

def main():
    # Load configuration
    api_key, ip_address = load_config()

    # Specify the device IDs here
    device_ids = ["1"]  # Replace with your device IDs as strings

    # Prompt the user for the group name
    group_name = input("Enter the name for the new group: ").strip()
    if not group_name:
        print("Group name cannot be empty. Exiting.")
        return

    # Create the new group via API
    group_id = create_group(api_key, ip_address, group_name, device_ids)
    if group_id:
        # Add the new group to secret.toml
        add_group_to_secret(group_id, group_name)

        # Update existing-groups.json with the new group
        # Fetch the latest groups data
        url = f"http://{ip_address}/api/{api_key}/groups"
        groups = fetch_and_save(url, "existing-groups.json")
        # Update secret.toml with the updated groups
        update_secret_with_groups(groups)
    else:
        print("Failed to create the new group.")

if __name__ == "__main__":
    main()
