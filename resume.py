# resume.py

import toml
from datetime import datetime, timedelta
import time
import requests
import os

# Function to load configuration from secret.toml
def load_config():
    config_file = 'secret.toml'
    if not os.path.exists(config_file):
        print(f"Error: Configuration file '{config_file}' does not exist.")
        exit()
    config = toml.load(config_file)
    api_key = config.get('API_KEY')
    ip_address = config.get('ip')
    if not api_key or not ip_address:
        print("Error: Missing 'API_KEY' or 'ip' in the configuration file.")
        exit()
    return api_key, ip_address

# Function to load group ID from secret.toml
def load_group_id(group_name):
    config_file = 'secret.toml'
    if not os.path.exists(config_file):
        print(f"Error: Configuration file '{config_file}' does not exist.")
        exit()
    config = toml.load(config_file)
    groups = config.get('groups', {})
    group_id = groups.get(group_name)
    if not group_id:
        print(f"Error: Group '{group_name}' not found in 'secret.toml'.")
        exit()
    return group_id

# Load configuration
API_KEY, IP_ADDRESS = load_config()
GROUP_NAME = 'wakeuplamps'
GROUP_ID = load_group_id(GROUP_NAME)
GROUP_URL = f'http://{IP_ADDRESS}/api/{API_KEY}/groups/{GROUP_ID}'
ACTION_URL = f'{GROUP_URL}/action'

MAX_TRANSITION_TIME = 3600  # seconds

def get_group_state():
    try:
        response = requests.get(GROUP_URL)
        response.raise_for_status()
        group_info = response.json()
        state = group_info.get('action', {})
        return state
    except requests.exceptions.RequestException as e:
        print(f"Failed to get group state. Error: {e}")
        return None

def resume_event(event_name, event):
    now = datetime.now()

    start_time = event['start_time']
    completion_time = event['completion_time']
    direction = event['direction']
    color_change = event.get('color_change', False)
    start_color = event.get('start_color', None)
    end_color = event.get('end_color', None)
    color_transition_time = event.get('color_transition_time', 0)
    brightness_transition_time = event.get('brightness_transition_time', 0)

    # Parse times
    start_datetime = datetime.combine(now.date(), datetime.strptime(start_time, '%H:%M').time())
    completion_datetime = datetime.combine(now.date(), datetime.strptime(completion_time, '%H:%M').time())

    # Adjust dates if necessary
    if completion_datetime <= start_datetime:
        completion_datetime += timedelta(days=1)
    if start_datetime <= now <= completion_datetime:
        # Event is currently active
        elapsed_time = (now - start_datetime).total_seconds()
        remaining_total_time = (completion_datetime - now).total_seconds()

        group_state = get_group_state()
        if group_state is None:
            return

        # Resume color transition if applicable
        if color_change:
            if elapsed_time < color_transition_time:
                # Color transition is in progress
                remaining_color_time = color_transition_time - elapsed_time

                # Prepare data for color transition
                current_x, current_y = group_state.get('xy', [0, 0])
                data = {
                    "on": True,
                    "xy": end_color,
                    "transitiontime": int(min(remaining_color_time, MAX_TRANSITION_TIME) * 10)
                }

                try:
                    response = requests.put(ACTION_URL, json=data)
                    response.raise_for_status()
                    print(f"Resumed color transition for event '{event_name}'.")
                except requests.exceptions.RequestException as e:
                    print(f"Failed to resume color transition. Error: {e}")

                # Adjust elapsed time after resuming color transition
                time.sleep(remaining_color_time)
                elapsed_time += remaining_color_time
            else:
                print(f"Color transition for event '{event_name}' should have completed. Skipping color resumption.")
        else:
            elapsed_time = 0  # No color transition, so brightness transition starts from the beginning

        # Resume brightness transition
        brightness_elapsed_time = elapsed_time - color_transition_time
        if brightness_elapsed_time < brightness_transition_time:
            remaining_brightness_time = brightness_transition_time - brightness_elapsed_time

            # Prepare data for brightness transition
            current_bri = group_state.get('bri', 0)
            if direction == 'ON':
                target_bri = 254
                bri_difference = target_bri - current_bri
            elif direction == 'OFF':
                target_bri = 1
                bri_difference = current_bri - target_bri
            else:
                print(f"Unknown direction '{direction}' for event '{event_name}'.")
                return

            if bri_difference <= 0:
                print(f"Group is already at or beyond target brightness for event '{event_name}'.")
                return

            data = {
                "on": True,
                "bri": target_bri,
                "transitiontime": int(min(remaining_brightness_time, MAX_TRANSITION_TIME) * 10)
            }

            try:
                response = requests.put(ACTION_URL, json=data)
                response.raise_for_status()
                print(f"Resumed brightness transition for event '{event_name}'.")
            except requests.exceptions.RequestException as e:
                print(f"Failed to resume brightness transition. Error: {e}")

            # For fade to OFF, ensure group turns off at completion time
            if direction == 'OFF':
                wait_seconds = (completion_datetime - datetime.now()).total_seconds()
                time.sleep(wait_seconds)
                turn_off_group()
        else:
            print(f"Brightness transition for event '{event_name}' should have completed. Skipping brightness resumption.")
    else:
        print(f"Event '{event_name}' is not currently active.")

def turn_off_group():
    # Send the "off" command to the group
    data = {
        "on": False
    }
    try:
        response = requests.put(ACTION_URL, json=data)
        response.raise_for_status()
        print("Group turned off completely.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to turn off group. Error: {e}")

def main():
    events_file = 'events.toml'
    print("Resumption script started. Monitoring for interrupted events...")
    while True:
        now = datetime.now()

        if os.path.exists(events_file):
            with open(events_file, 'r') as f:
                events = toml.load(f)

            for event_name, event in events.items():
                # Check if the event is currently active
                start_time = event['start_time']
                completion_time = event['completion_time']

                # Parse times
                start_datetime = datetime.combine(now.date(), datetime.strptime(start_time, '%H:%M').time())
                completion_datetime = datetime.combine(now.date(), datetime.strptime(completion_time, '%H:%M').time())

                # Adjust dates if necessary
                if completion_datetime <= start_datetime:
                    completion_datetime += timedelta(days=1)
                if start_datetime <= now <= completion_datetime:
                    # Event is currently active
                    # Check if event needs resumption
                    # Use logic from monitor.py to detect interruptions
                    group_state = get_group_state()
                    if group_state is None:
                        continue

                    direction = event['direction']
                    color_change = event.get('color_change', False)
                    color_transition_time = event.get('color_transition_time', 0)
                    brightness_transition_time = event.get('brightness_transition_time', 0)
                    total_transition_time = color_transition_time + brightness_transition_time
                    elapsed_time = (now - start_datetime).total_seconds()

                    issues_detected = False

                    # Check color transition
                    if color_change and elapsed_time <= color_transition_time:
                        progress = elapsed_time / color_transition_time
                        start_x, start_y = event['start_color']
                        end_x, end_y = event['end_color']
                        expected_x = start_x + progress * (end_x - start_x)
                        expected_y = start_y + progress * (end_y - start_y)
                        actual_x, actual_y = group_state.get('xy', [0, 0])

                        color_tolerance = 0.05

                        if not (abs(expected_x - actual_x) <= color_tolerance and abs(expected_y - actual_y) <= color_tolerance):
                            print(f"Event '{event_name}' color transition appears interrupted. Attempting to resume.")
                            resume_event(event_name, event)
                            continue
                    elif color_change and elapsed_time > color_transition_time:
                        # Color transition should have completed
                        pass  # No action needed

                    # Check brightness transition
                    brightness_elapsed_time = max(0, elapsed_time - color_transition_time)
                    if brightness_elapsed_time <= brightness_transition_time:
                        progress = brightness_elapsed_time / brightness_transition_time
                        if direction == 'ON':
                            expected_bri = int(progress * 254)
                        elif direction == 'OFF':
                            expected_bri = 254 - int(progress * 253)
                        else:
                            continue

                        actual_bri = group_state.get('bri', 0)
                        brightness_tolerance = 0.10

                        lower_bound = expected_bri * (1 - brightness_tolerance)
                        upper_bound = expected_bri * (1 + brightness_tolerance)

                        if not (lower_bound <= actual_bri <= upper_bound):
                            print(f"Event '{event_name}' brightness transition appears interrupted. Attempting to resume.")
                            resume_event(event_name, event)
                            continue
                    elif brightness_elapsed_time > brightness_transition_time:
                        # Brightness transition should have completed
                        pass  # No action needed

                else:
                    continue  # Event not active
        else:
            print(f"{events_file} not found.")

        time.sleep(30)  # Check every 30 seconds

if __name__ == "__main__":
    main()
