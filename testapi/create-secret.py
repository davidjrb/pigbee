# create-secret.py

import os

# Define the filename
filename = "secret.toml"

# Check if secret.toml already exists
if os.path.exists(filename):
    print("The file 'secret.toml' already exists.")
    exit()

# Prompt user for API key and IP address
api_key = input("Enter the deCONZ API key: ").strip()
ip_address = input("Enter the IP address of the Zigbee gateway server: ").strip()

# Create the file contents as a formatted string with comments
config_content = f"""
# secret.toml

# deCONZ authentication token
API_KEY = '{api_key}'

# IP address of Zigbee gateway server
ip = "{ip_address}"

# Group details
# [[groups]] # no groups added yet
"""

# Write the content to secret.toml
with open(filename, "w") as file:
    file.write(config_content.strip())

print(f"'{filename}' has been created with the provided details.")