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

def schedule_task(run_time, command):
    now = datetime.datetime.now()
    delay = (run_time - now).total_seconds()
    if delay < 0:
        print(f"Scheduled time {run_time} is in the past. Skipping command '{command}'.")
        return
    threading.Timer(delay, execute_command, args=[command]).start()
    print(f"Scheduled command '{command}' to run at {run_time.strftime('%Y-%m-%d %H:%M:%S')}")

def parse_time(time_str):
    # Check for relative time (e.g., "+10s", "+5m")
    relative_time_match = re.match(r'^\+(\d+)([smh])$', time_str)
    if relative_time_match:
        value, unit = relative_time_match.groups()
        value = int(value)
        if unit == 's':
            delta = datetime.timedelta(seconds=value)
        elif unit == 'm':
            delta = datetime.timedelta(minutes=value)
        elif unit == 'h':
            delta = datetime.timedelta(hours=value)
        else:
            delta = datetime.timedelta()
        run_time = datetime.datetime.now() + delta
    else:
        # Absolute time in HH:MM or HH:MM:SS format
        try:
            time_formats = ['%H:%M', '%H:%M:%S']
            for fmt in time_formats:
                try:
                    time_obj = datetime.datetime.strptime(time_str, fmt).time()
                    break
                except ValueError:
                    continue
            else:
                raise ValueError
            now = datetime.datetime.now()
            run_time = datetime.datetime.combine(now.date(), time_obj)
            if run_time < now:
                # If the time has already passed today, schedule for the next day
                run_time += datetime.timedelta(days=1)
        except ValueError:
            print(f"Invalid time format: {time_str}. Expected format HH:MM, HH:MM:SS, or relative time like '+10s', '+5m'.")
            sys.exit(1)
    return run_time

def main():
    parser = argparse.ArgumentParser(description="Routine Scheduler")
    parser.add_argument("-r", "--routine", required=True, help="Name of the routine TOML file without extension")
    args = parser.parse_args()

    routine_file = f"{args.routine}.toml"
    if not os.path.exists(routine_file):
        print(f"Routine file '{routine_file}' not found.")
        sys.exit(1)

    # Load the schedule from the TOML file
    try:
        schedule_data = toml.load(routine_file)
    except toml.TomlDecodeError as e:
        print(f"Error parsing TOML file: {e}")
        sys.exit(1)

    # Get the schedule list
    schedule_list = schedule_data.get('schedule')
    if not schedule_list:
        print("No schedule found in the TOML file.")
        sys.exit(1)

    for task in schedule_list:
        time_str = task.get('time')
        action = task.get('action')
        additional_args = task.get('args', '')

        if not time_str or not action:
            print("Each task must have 'time' and 'action' fields.")
            continue

        run_time = parse_time(time_str)

        # Build the command
        command = f"python3 DeCONZapi.py -action \"{action}\" {additional_args}"

        # Schedule the task
        schedule_task(run_time, command)

    print("All tasks have been scheduled. Waiting for tasks to execute...")
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Routine scheduler terminated by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
