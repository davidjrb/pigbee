## `README.md`

```markdown
# Pigbee

An automation project to control Zigbee devices, specifically designed to implement a wake-up lamp functionality using Zigbee for smart lighting.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Configuration](#configuration)
  - [Running the Scripts](#running-the-scripts)
- [Directory Structure](#directory-structure)
- [License](#license)

## Introduction

**Pigbee** is a collection of Python scripts that interact with Zigbee devices via an API, enabling automated control of smart lights. The primary inspiration for this project was to create a wake-up lamp for personal use.

## Features

- **Automated Wake-Up and Sleep Lighting**: Gradually increase or decrease the brightness and color temperature of your smart lights to simulate sunrise or sunset.
- **Event Scheduling**: Define events in `events.toml` to schedule lighting changes.
- **Group Control**: Manage groups of devices instead of individual lights.
- **Monitoring and Resuming Events**: Monitor ongoing events and resume them if interrupted.
- **Configuration Management**: Securely store sensitive information like API keys and IP addresses using `secret.toml`.

## Installation

### Prerequisites

- deconz
- Python 3.x
- `pip`
- `virtualenv`

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/pigbee.git
   cd pigbee
   ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Configuration**

   - Create a `secret.toml` file in the project root directory.
   - Add your API key, IP address, and group IDs.

     ```toml
     API_KEY = 'your_api_key'
     ip = 'your_ip_address'

     [groups]
     wakeuplamps = 'your_group_id'
     ```

## Usage

### Configuration

- **events.toml**: Define your lighting events in this file. Example events are provided in the file (currently commented out).

### Running the Scripts

- **clock.py**: Main script to initiate scheduled events.

  ```bash
  python clock.py
  ```

- **monitor.py**: Monitors ongoing events and detects interruptions.

  ```bash
  python monitor.py
  ```

- **resume.py**: Attempts to resume any interrupted events.

  ```bash
  python resume.py
  ```

- **create-group.py**: Script to create new groups of devices.

  ```bash
  python create-group.py
  ```

- **add-devices-to-group.py**: Adds devices to existing groups.

  ```bash
  python add-devices-to-group.py
  ```

- **generate_requirements.py**: Generates the `requirements.txt` file.

  ```bash
  python generate_requirements.py
  ```

## Directory Structure

- **add-devices-to-group.py**: Script to add devices to groups.
- **clock.py**: Initiates and manages scheduled lighting events.
- **create-group.py**: Creates new groups in your Zigbee setup.
- **events.toml**: Configuration file where you define your events.
- **generate_requirements.py**: Generates the `requirements.txt` file.
- **get-json.py**: Fetches JSON data from the API.
- **json/**: Directory containing JSON data files (ignored in version control).
- **monitor.py**: Monitors ongoing events for interruptions.
- **prompter.py**: Script to assist with user prompts.
- **requirements.txt**: List of Python package dependencies.
- **resume.py**: Resumes interrupted events.
- **secret.toml**: Configuration file for API keys and IP addresses (ignored in version control).
- **testapi/**: Directory for testing API interactions (ignored in version control).
- **venv/**: Virtual environment directory (ignored in version control).

---

- **Event Configuration**: In `events.toml`, you have several example events commented out. You can uncomment and customize them as needed.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---