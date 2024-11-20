import json
import argparse
import requests
import toml
import re
import sys

# Path to the TOML file (adjust the path if necessary)
SECRET_FILE_PATH = "secret.toml"

def fetch_json(ip, api_key, endpoint):
    url = f"http://{ip}/api/{api_key}/{endpoint}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        sys.exit(1)

def fetch_and_print_json(ip, api_key, endpoint):
    data = fetch_json(ip, api_key, endpoint)
    print(json.dumps(data, indent=4))
    return data

def parse_transition_time(time_str):
    match = re.match(r'^(\d+)([smh])$', time_str.lower())
    if not match:
        print("Error: Time format is invalid. Use format like '10s', '2m', or '1h'.")
        sys.exit(1)
    value, unit = match.groups()
    value = int(value)
    if unit == 's':
        seconds = value
    elif unit == 'm':
        seconds = value * 60
    elif unit == 'h':
        seconds = value * 3600
    else:
        seconds = 0
    if seconds > 3600:
        print("Error: Time value cannot exceed 1 hour.")
        sys.exit(1)
    transition_time = seconds * 10  # Convert to tenths of a second
    return transition_time

def parse_time_in_seconds(time_str):
    return parse_transition_time(time_str) // 10

def build_payload(action, time_value):
    payload = {}
    # Handle 'pairing' action
    if action.lower() == 'pairing':
        seconds = parse_time_in_seconds(time_value) if time_value else 60
        payload["permitjoin"] = seconds
        return payload, 'config'  # Return endpoint as 'config'
    # Handle 'cancel' action
    elif action.lower() == 'cancel':
        payload["permitjoin"] = 0  # Disable pairing mode
        return payload, 'config'  # Return endpoint as 'config'
    # Handle 'group all lights' action
    elif action.lower() == 'group all lights':
        return None, 'group_all_lights'
    # Handle 'on' and 'off'
    elif action.lower() == 'on':
        payload["on"] = True
    elif action.lower() == 'off':
        payload["on"] = False
    # Handle brightness percentage
    elif re.match(r'^\d{1,3}%$', action):
        brightness_percent = int(action[:-1])
        if not 0 <= brightness_percent <= 100:
            print("Error: Brightness percentage must be between 0 and 100.")
            sys.exit(1)
        brightness_value = round((254 / 100) * brightness_percent)
        payload["bri"] = brightness_value
    # Handle 'cool' and 'warm'
    elif action.lower() == 'cool':
        payload["xy"] = [0.33, 0.34]
    elif action.lower() == 'warm':
        payload["xy"] = [0.526, 0.413]
    else:
        print("Error: Invalid action specified.")
        sys.exit(1)

    # Add transition time if specified
    if time_value:
        payload["transitiontime"] = parse_transition_time(time_value)
    return payload, None  # No special endpoint

def send_request(ip, api_key, group_id, payload, endpoint_override=None):
    if endpoint_override == 'config':
        url = f"http://{ip}/api/{api_key}/config"
        try:
            response = requests.put(url, json=payload)
            response.raise_for_status()
            data = response.json()
            print(json.dumps(data, indent=4))
        except requests.exceptions.RequestException as e:
            print(f"Error sending request: {e}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
    elif endpoint_override == 'group_all_lights':
        # Special handling for 'group all lights' action
        # Fetch all lights
        lights_data = fetch_json(ip, api_key, 'lights')
        light_ids = list(lights_data.keys())

        # Update group with all lights
        url = f"http://{ip}/api/{api_key}/groups/{group_id}"
        group_payload = {
            "lights": light_ids
        }
        try:
            response = requests.put(url, json=group_payload)
            response.raise_for_status()
            data = response.json()
            print("Updated group with all lights:")
            print(json.dumps(data, indent=4))
        except requests.exceptions.RequestException as e:
            print(f"Error updating group: {e}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
    else:
        url = f"http://{ip}/api/{api_key}/groups/{group_id}/action"
        try:
            response = requests.put(url, json=payload)
            response.raise_for_status()  # Check for HTTP errors
            data = response.json()
            print(json.dumps(data, indent=4))
        except requests.exceptions.RequestException as e:
            print(f"Error sending request: {e}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Control DeCONZ lights via API.")
    parser.add_argument("-GET", dest="payload", help="API endpoint to GET, e.g., 'groups'.")
    parser.add_argument("-action", help="Action to perform: 'on', 'off', 'cool', 'warm', 'pairing', 'cancel', 'group all lights', or 'X%' for brightness.")
    parser.add_argument("-time", help="Transition time or pairing duration (e.g., '10s', '2m', '1h'). Optional.")
    args = parser.parse_args()

    # Ensure only -GET or -action is used, not both
    if (args.payload and args.action) or (not args.payload and not args.action):
        print("Error: Please specify either -GET or -action, but not both.")
        sys.exit(1)

    # Load config from the specified TOML file
    config = toml.load(SECRET_FILE_PATH)
    ip = config.get("ip")
    api_key = config.get("API_KEY")
    group_id = config.get("groupID")

    if not ip or not api_key or not group_id:
        print("Error: IP, API key, or groupID not found in the TOML file.")
        sys.exit(1)

    if args.payload:
        # Perform GET request
        fetch_and_print_json(ip, api_key, args.payload)
    elif args.action:
        # Build the payload for the action
        payload, endpoint_override = build_payload(args.action, args.time)

        # Send the request
        send_request(ip, api_key, group_id, payload, endpoint_override)
