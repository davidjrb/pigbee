# prompter.py

import toml
from datetime import datetime, timedelta
import os
import re

# Maximum transition time in seconds (1 hour)
MAX_TRANSITION_TIME = 3600  # seconds

# Color coordinates for warm and cool light
COLOR_WARM = [0.526, 0.413]  # Example values for warm light
COLOR_COOL = [0.33, 0.34]    # Example values for cool light

def calculate_transition_times(duration_seconds):
    # Ideal ratios
    ideal_color_ratio = 0.25
    ideal_brightness_ratio = 0.75

    # Calculate ideal transition times
    ideal_color_time = duration_seconds * ideal_color_ratio
    ideal_brightness_time = duration_seconds * ideal_brightness_ratio

    # Cap the brightness transition time
    brightness_transition_time = min(ideal_brightness_time, MAX_TRANSITION_TIME)

    # Calculate the color transition time based on the remaining duration
    color_transition_time = duration_seconds - brightness_transition_time

    # Cap the color transition time
    color_transition_time = min(color_transition_time, MAX_TRANSITION_TIME)

    # Ensure color_transition_time is not negative
    if color_transition_time < 0:
        color_transition_time = 0

    return color_transition_time, brightness_transition_time

def main():
    events_file = 'events.toml'
    if os.path.exists(events_file):
        with open(events_file, 'r') as f:
            events = toml.load(f)
    else:
        events = {}

    # Prompt for Fade Direction
    direction = ''
    while direction not in ['ON', 'OFF']:
        direction = input("Would you like the light to fade to ON or OFF? [ON/OFF]: ").strip().upper()

    # Select Time Unit
    time_unit = ''
    while time_unit not in ['s', 'm', 'h']:
        time_unit = input("Select the time unit for fade duration: s/m/h (seconds, minutes, hours): ").strip().lower()

    # Input Duration
    while True:
        duration_input = input(f"Input fade duration in [{ 'seconds' if time_unit=='s' else 'minutes' if time_unit=='m' else 'hours' }]. For example, 1.5 minutes should be entered as 1.5: ").strip()
        try:
            duration = float(duration_input)
            break
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

    # Convert duration to seconds
    if time_unit == 's':
        duration_seconds = duration
    elif time_unit == 'm':
        duration_seconds = duration * 60
    elif time_unit == 'h':
        duration_seconds = duration * 3600
    else:
        duration_seconds = duration  # Should not reach here

    # Input Completion Time
    time_pattern = re.compile(r'^\d{1,2}:\d{2}$')
    while True:
        completion_time_input = input("Please enter the desired fade completion time in 24-hour format (e.g., 21:45): ").strip()
        if time_pattern.match(completion_time_input):
            try:
                completion_time = datetime.strptime(completion_time_input, '%H:%M')
                break
            except ValueError:
                print("Invalid time format. Please try again.")
        else:
            print("Invalid time format. Please use HH:MM format.")

    # Calculate start_time
    start_time = (datetime.combine(datetime.today(), completion_time.time()) - timedelta(seconds=duration_seconds)).time()
    start_time_str = start_time.strftime('%H:%M')
    completion_time_str = completion_time.strftime('%H:%M')

    # Prompt for Color Change
    color_change = ''
    while color_change not in ['Y', 'N']:
        color_change = input("Would you like to include a color change? [Y/N]: ").strip().upper()

    if color_change == 'Y':
        # Ask for color transition direction
        color_direction = ''
        while color_direction not in ['WARM_TO_COOL', 'COOL_TO_WARM']:
            color_input = input("Select color change direction: Warm to Cool or Cool to Warm? [Warm/Cool]: ").strip().upper()
            if color_input == 'WARM':
                color_direction = 'COOL_TO_WARM'
            elif color_input == 'COOL':
                color_direction = 'WARM_TO_COOL'

        # Set start and end colors based on direction
        if color_direction == 'WARM_TO_COOL':
            start_color = COLOR_WARM
            end_color = COLOR_COOL
        else:
            start_color = COLOR_COOL
            end_color = COLOR_WARM

        # Calculate transition times
        color_transition_time, brightness_transition_time = calculate_transition_times(duration_seconds)

        # Check and adjust total transition time if necessary
        total_transition_time = color_transition_time + brightness_transition_time
        if total_transition_time > 2 * MAX_TRANSITION_TIME:
            print(f"Total transition time exceeds maximum allowed ({2 * MAX_TRANSITION_TIME} seconds). Adjusting transition times.")
            color_transition_time = MAX_TRANSITION_TIME
            brightness_transition_time = MAX_TRANSITION_TIME
    else:
        color_change = False
        start_color = None
        end_color = None
        color_transition_time = 0
        brightness_transition_time = min(duration_seconds, MAX_TRANSITION_TIME)
        duration_seconds = brightness_transition_time  # Adjust duration to actual transition time
        if duration_seconds < brightness_transition_time:
            print(f"Adjusted duration to {duration_seconds / 60} minutes due to maximum transition time limits.")

    # Recurrence Prompt
    print("Select the recurrence pattern for the event:")
    print("1. Once")
    print("2. Every day")
    print("3. Weekdays (Monday to Friday)")
    print("4. Specific days")
    while True:
        recurrence_choice = input("Enter your choice (1-4): ").strip()
        if recurrence_choice in ['1', '2', '3', '4']:
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

    if recurrence_choice == '1':
        recurrence = 'once'
    elif recurrence_choice == '2':
        recurrence = 'everyday'
    elif recurrence_choice == '3':
        recurrence = 'weekdays'
    elif recurrence_choice == '4':
        # Prompt for specific days
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        selected_days = []
        print("Enter the days of the week when the event should occur (type 'done' when finished):")
        while True:
            day = input("Day (e.g., Monday): ").strip().capitalize()
            if day.lower() == 'done':
                break
            elif day in days_of_week:
                if day not in selected_days:
                    selected_days.append(day)
                else:
                    print(f"{day} is already selected.")
            else:
                print("Invalid day. Please enter a valid day of the week.")
        recurrence = selected_days

    # Name the Event
    if events:
        print("Existing events:")
        for event_name in events.keys():
            print(f"- {event_name}")
    else:
        print("No existing events.")

    event_name = input("Enter a name for the new event. If this name already exists, a number will be added automatically: ").strip()
    original_event_name = event_name
    counter = 1
    while event_name in events:
        event_name = f"{original_event_name}_{counter}"
        counter += 1

    # Create event data
    event_data = {
        'direction': direction,
        'time_unit': time_unit,
        'duration': int(duration_seconds),
        'completion_time': completion_time_str,
        'start_time': start_time_str,
        'recurrence': recurrence,
        'last_executed': '',
        'color_change': color_change == 'Y',
        'color_direction': color_direction if color_change == 'Y' else '',
        'start_color': start_color,
        'end_color': end_color,
        'color_transition_time': int(color_transition_time),
        'brightness_transition_time': int(brightness_transition_time)
    }

    # Add event to events
    events[event_name] = event_data

    # Write to events.toml
    with open(events_file, 'w') as f:
        toml.dump(events, f)

    print(f"Event '{event_name}' has been saved to {events_file}.")

if __name__ == "__main__":
    main()
