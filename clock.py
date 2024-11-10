# clock.py

import toml
from datetime import datetime, timedelta
import time
import requests
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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
URL = f'http://{IP_ADDRESS}/api/{API_KEY}/groups/{GROUP_ID}/action'

# Maximum transition time in seconds (1 hour)
MAX_TRANSITION_TIME = 3600

def adjust_transition_time(transition_time):
    if transition_time > MAX_TRANSITION_TIME:
        print(f"Transition time {transition_time} exceeds maximum allowed. Adjusting to {MAX_TRANSITION_TIME} seconds.")
        return MAX_TRANSITION_TIME
    return transition_time

class EventHandler(FileSystemEventHandler):
    def __init__(self, load_events_callback):
        self.load_events_callback = load_events_callback

    def on_modified(self, event):
        if event.src_path.endswith('events.toml'):
            print("events.toml has been modified. Reloading events...")
            self.load_events_callback()

def should_execute_today(recurrence, today):
    if recurrence == 'everyday':
        return True
    elif recurrence == 'weekdays':
        return today.weekday() < 5  # Monday=0, Sunday=6
    elif recurrence == 'weekends':
        return today.weekday() >= 5
    elif isinstance(recurrence, list):
        day_name = today.strftime('%A')
        return day_name in recurrence
    else:  # 'once'
        return True

def main():
    events_file = 'events.toml'
    events = {}

    def load_events():
        nonlocal events
        if os.path.exists(events_file):
            with open(events_file, 'r') as f:
                events = toml.load(f)
        else:
            events = {}
        print("Events reloaded.")

    load_events()

    # Set up watchdog observer
    event_handler = EventHandler(load_events)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    print("Clock started. Monitoring events...")
    try:
        while True:
            now = datetime.now()
            current_time_str = now.strftime('%H:%M')
            today = now.date()

            if events:
                for event_name, event in events.items():
                    # Check if event should execute today based on recurrence
                    recurrence = event.get('recurrence', 'once')
                    if not should_execute_today(recurrence, now):
                        continue

                    # Check if event is scheduled for current time
                    if event['start_time'] == current_time_str:
                        last_executed = event.get('last_executed', '')
                        if last_executed != str(today):
                            print(f"Initiating event '{event_name}'")
                            initiate_event(event, event_name)
                            # Update last_executed date
                            event['last_executed'] = str(today)
                            # Write back to events.toml
                            with open(events_file, 'w') as f:
                                toml.dump(events, f)
                        else:
                            print(f"Event '{event_name}' has already been executed today.")
            else:
                print("No events found.")

            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def initiate_event(event, event_name):
    direction = event['direction']
    total_duration = event['duration']
    completion_time = event['completion_time']
    color_change = event.get('color_change', False)
    start_color = event.get('start_color', None)
    end_color = event.get('end_color', None)
    color_transition_time = event.get('color_transition_time', 0)
    brightness_transition_time = event.get('brightness_transition_time', total_duration)

    # Ensure transition times do not exceed maximum allowed
    color_transition_time = min(color_transition_time, MAX_TRANSITION_TIME)
    brightness_transition_time = min(brightness_transition_time, MAX_TRANSITION_TIME)

    # Calculate when to start brightness fade if color change is included
    if color_change:
        # Start color change now
        initiate_color_change(start_color, end_color, color_transition_time)
        # Schedule brightness fade after color change
        time.sleep(color_transition_time)
        initiate_brightness_fade(direction, brightness_transition_time)
    else:
        # Initiate brightness fade immediately
        initiate_brightness_fade(direction, brightness_transition_time)

    # Schedule turning off the lamp if fading to OFF
    if direction == 'OFF':
        total_wait_time = color_transition_time + brightness_transition_time
        # Calculate time to wait until completion_time
        now = datetime.now()
        completion_datetime = datetime.combine(now.date(), datetime.strptime(completion_time, '%H:%M').time())
        if completion_datetime < now:
            completion_datetime += timedelta(days=1)
        wait_seconds = (completion_datetime - now).total_seconds()
        # Adjust wait time if necessary
        if wait_seconds > total_wait_time:
            wait_seconds = total_wait_time
        time.sleep(wait_seconds)
        turn_off_lamp()

def initiate_color_change(start_color, end_color, transition_time):
    print(f"Initiating color change from {start_color} to {end_color} over {transition_time} seconds.")
    data = {
        "on": True,
        "xy": end_color,
        "transitiontime": int(transition_time * 10)
    }
    try:
        response = requests.put(URL, json=data)
        response.raise_for_status()
        print("Color change initiated successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to initiate color change. Error: {e}")

def initiate_brightness_fade(direction, transition_time):
    print(f"Initiating fade {direction} over {transition_time} seconds.")
    transition_time_units = int(transition_time * 10)
    if direction == 'ON':
        data = {
            "on": True,
            "bri": 254,
            "transitiontime": transition_time_units
        }
    elif direction == 'OFF':
        data = {
            "on": True,  # Ensure the group is on to execute the fade
            "bri": 1,
            "transitiontime": transition_time_units
        }
    else:
        print(f"Unknown direction: {direction}")
        return

    try:
        response = requests.put(URL, json=data)
        response.raise_for_status()
        print(f"Brightness fade initiated successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to initiate brightness fade. Error: {e}")

def turn_off_lamp():
    # Send the "off" command to the group
    data = {
        "on": False
    }
    try:
        response = requests.put(URL, json=data)
        response.raise_for_status()
        print("Group turned off completely.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to turn off group. Error: {e}")

if __name__ == "__main__":
    main()
