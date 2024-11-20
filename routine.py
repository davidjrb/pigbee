import argparse
import toml
import time
import datetime
import subprocess
import threading
import sys
import os
import re

def execute_command(command):
    try:
        # Run the command as a subprocess
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def schedule_task(delay, command, timers_list):
    if delay < 0:
        print(f"Delay {delay} seconds is negative. Skipping command '{command}'.")
        return
    timer = threading.Timer(delay, execute_command, args=[command])
    timer.start()
    timers_list.append(timer)
    run_time = datetime.datetime.now() + datetime.timedelta(seconds=delay)
    print(f"Scheduled command '{command}' to run at {run_time.strftime('%Y-%m-%d %H:%M:%S')}")

def parse_relative_time(time_str):
    # Match patterns like '+5s', '+10m', '+1h'
    relative_time_match = re.match(r'^\+(\d+)([smh])$', time_str)
    if not relative_time_match:
        print(f"Invalid time format: {time_str}. Expected relative time like '+10s', '+5m', '+1h'.")
        sys.exit(1)
    value, unit = relative_time_match.groups()
    value = int(value)
    if unit == 's':
        delta = value
    elif unit == 'm':
        delta = value * 60
    elif unit == 'h':
        delta = value * 3600
    else:
        delta = 0
    return delta

def wait_until(start_time_str):
    try:
        start_time = datetime.datetime.strptime(start_time_str, '%H:%M:%S').time()
    except ValueError:
        print(f"Invalid start_time format: {start_time_str}. Expected format hh:mm:ss")
        sys.exit(1)
    
    now = datetime.datetime.now()
    today_start = datetime.datetime.combine(now.date(), start_time)
    if today_start < now:
        # If the start time has already passed today, schedule for tomorrow
        today_start += datetime.timedelta(days=1)
    delay = (today_start - now).total_seconds()
    print(f"Routine will start at {today_start.strftime('%Y-%m-%d %H:%M:%S')} (in {int(delay)} seconds).")
    if delay > 0:
        time.sleep(delay)

def main():
    parser = argparse.ArgumentParser(description="Routine Scheduler")
    parser.add_argument("-r", "--routine", required=True, help="Name of the routine to execute")
    args = parser.parse_args()

    routine_file = "routines.toml"  # Hardcoded to always read routines.toml
    if not os.path.exists(routine_file):
        print(f"Routine file '{routine_file}' not found.")
        sys.exit(1)

    # Load the routines from the TOML file
    try:
        routines_data = toml.load(routine_file)
    except toml.TomlDecodeError as e:
        print(f"Error parsing TOML file: {e}")
        sys.exit(1)

    # Get the list of routines
    routines_list = routines_data.get('routines')
    if not routines_list:
        print("No routines found in the TOML file.")
        sys.exit(1)

    # Find the specified routine
    selected_routine = None
    for routine in routines_list:
        if routine.get('name') == args.routine:
            selected_routine = routine
            break

    if not selected_routine:
        print(f"Routine '{args.routine}' not found in '{routine_file}'.")
        sys.exit(1)

    # Check for optional start_time
    start_time_str = selected_routine.get('start_time')
    if start_time_str:
        wait_until(start_time_str)

    # Get the schedule list
    schedule_list = selected_routine.get('schedule')
    if not schedule_list:
        print(f"No schedule found for routine '{args.routine}'.")
        sys.exit(1)

    # List to keep track of all timers
    scheduled_timers = []

    # Schedule each task
    for task in schedule_list:
        time_str = task.get('time')
        action = task.get('action')
        additional_args = task.get('args', '')

        if not time_str or not action:
            print("Each task must have 'time' and 'action' fields.")
            continue

        delay = parse_relative_time(time_str)

        # Build the command
        # Enclose action in quotes to handle actions with spaces
        command = f'python3 DeCONZapi.py -action "{action}" {additional_args}'

        # Schedule the task
        schedule_task(delay, command, scheduled_timers)

    print("All tasks have been scheduled. Waiting for tasks to execute...")

    # Wait for all scheduled tasks to complete
    for timer in scheduled_timers:
        timer.join()

    print("All tasks have been executed. Exiting.")

if __name__ == "__main__":
    main()
