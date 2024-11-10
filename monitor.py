# monitor.py

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
STATE_URL = f'{GROUP_URL}'

def get_group_state():
    try:
        response = requests.get(GROUP_URL)
        response.raise_for_status()
        group_info = response.json()
        state = group_info['action']
        return state
    except requests.exceptions.RequestException as e:
        print(f"Failed to get group state. Error: {e}")
        return None

def main():
    events_file = 'events.toml'
    print("Monitoring ongoing events...")
    while True:
        now = datetime.now()

        if os.path.exists(events_file):
            with open(events_file, 'r') as f:
                events = toml.load(f)

            for event_name, event in events.items():
                # Check if the event is currently active
                start_time = event['start_time']
                completion_time = event['completion_time']
                direction = event['direction']
                color_change = event.get('color_change', False)
                color_transition_time = event.get('color_transition_time', 0)
                brightness_transition_time = event.get('brightness_transition_time', 0)
                total_transition_time = color_transition_time + brightness_transition_time

                # Parse times
                start_datetime = datetime.combine(now.date(), datetime.strptime(start_time, '%H:%M').time())
                completion_datetime = datetime.combine(now.date(), datetime.strptime(completion_time, '%H:%M').time())

                # Adjust dates if necessary
                if completion_datetime <= start_datetime:
                    completion_datetime += timedelta(days=1)
                if now >= start_datetime and now <= completion_datetime:
                    # Event is currently active
                    elapsed_time = (now - start_datetime).total_seconds()

                    group_state = get_group_state()
                    if group_state is None:
                        continue

                    issues_detected = False

                    # Check color transition
                    if color_change and elapsed_time <= color_transition_time:
                        # Calculate expected color based on progress
                        progress = elapsed_time / color_transition_time
                        start_x, start_y = event['start_color']
                        end_x, end_y = event['end_color']
                        expected_x = start_x + progress * (end_x - start_x)
                        expected_y = start_y + progress * (end_y - start_y)
                        actual_x = group_state.get('xy', [0, 0])[0]
                        actual_y = group_state.get('xy', [0, 0])[1]

                        # Define a tolerance for color comparison
                        color_tolerance = 0.05  # Adjust as needed

                        if not (abs(expected_x - actual_x) <= color_tolerance and abs(expected_y - actual_y) <= color_tolerance):
                            print(f"Event '{event_name}' color transition may have been interrupted.")
                            print(f"Expected color xy: [{expected_x:.3f}, {expected_y:.3f}], Actual color xy: [{actual_x:.3f}, {actual_y:.3f}]")
                            issues_detected = True
                        else:
                            print(f"Event '{event_name}' color transition is progressing as expected.")
                    elif color_change and elapsed_time > color_transition_time:
                        # Color transition should have completed
                        expected_x, expected_y = event['end_color']
                        actual_x, actual_y = group_state.get('xy', [0, 0])[0], group_state.get('xy', [0, 0])[1]
                        color_tolerance = 0.05

                        if not (abs(expected_x - actual_x) <= color_tolerance and abs(expected_y - actual_y) <= color_tolerance):
                            print(f"Event '{event_name}' color transition may have been interrupted after expected completion.")
                            print(f"Expected color xy: [{expected_x:.3f}, {expected_y:.3f}], Actual color xy: [{actual_x:.3f}, {actual_y:.3f}]")
                            issues_detected = True

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
                        brightness_tolerance = 0.10  # 10%

                        lower_bound = expected_bri * (1 - brightness_tolerance)
                        upper_bound = expected_bri * (1 + brightness_tolerance)

                        if not (lower_bound <= actual_bri <= upper_bound):
                            print(f"Event '{event_name}' brightness transition may have been interrupted.")
                            print(f"Expected brightness: {expected_bri}, Actual brightness: {actual_bri}")
                            issues_detected = True
                        else:
                            print(f"Event '{event_name}' brightness transition is progressing as expected.")
                    elif brightness_elapsed_time > brightness_transition_time:
                        # Brightness transition should have completed
                        if direction == 'ON':
                            expected_bri = 254
                        elif direction == 'OFF':
                            expected_bri = 1

                        actual_bri = group_state.get('bri', 0)
                        if actual_bri != expected_bri:
                            print(f"Event '{event_name}' brightness transition may have been interrupted after expected completion.")
                            print(f"Expected brightness: {expected_bri}, Actual brightness: {actual_bri}")
                            issues_detected = True

                    if not issues_detected:
                        print(f"Event '{event_name}' is progressing as expected.")

                else:
                    continue  # Event not active
        else:
            print(f"{events_file} not found.")

        time.sleep(30)  # Check every 30 seconds

if __name__ == "__main__":
    main()
