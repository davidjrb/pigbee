# generate_requirements.py

import subprocess
import sys
import os

def generate_requirements():
    try:
        # Check if the script is running inside a virtual environment
        if hasattr(sys, 'real_prefix') or \
           (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("Detected virtual environment.")
        else:
            print("Warning: You are not running inside a virtual environment.")

        # Generate the requirements.txt file
        with open('requirements.txt', 'w') as f:
            subprocess.check_call([sys.executable, '-m', 'pip', 'freeze'], stdout=f)
        print("requirements.txt has been generated successfully.")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while generating requirements.txt: {e}")

if __name__ == '__main__':
    generate_requirements()
