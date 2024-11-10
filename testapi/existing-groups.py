# existing-groups.py

import requests
import json
import datetime
import toml

def main():
    # Load IP_ADDRESS and API_KEY from secret.toml
    try:
        secrets = toml.load('secret.toml')
        IP_ADDRESS = secrets.get('ip')
        API_KEY = secrets.get('API_KEY')

        if not IP_ADDRESS or not API_KEY:
            print("Error: Missing 'ip' or 'API_KEY' in 'secret.toml'.")
            return
    except FileNotFoundError:
        print("Error: 'secret.toml' file not found.")
        return

    URL = f'http://{IP_ADDRESS}/api/{API_KEY}/groups'

    try:
        response = requests.get(URL)
        response.raise_for_status()
        groups = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching groups: {e}")
        return

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"existing-groups_{timestamp}.json"

    try:
        with open(filename, 'w') as f:
            json.dump(groups, f, indent=4)
        print(f"Groups have been saved to {filename}")
    except IOError as e:
        print(f"Error writing to file: {e}")

if __name__ == "__main__":
    main()
