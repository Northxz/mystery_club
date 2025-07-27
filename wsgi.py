#!/usr/bin/python3.10

import sys
import os

# Add your project directory to the sys.path
path = '/home/yourusername/mystery_club'
if path not in sys.path:
    sys.path.insert(0, path)

# Set the working directory
os.chdir(path)

from app import app as application

if __name__ == "__main__":
    application.run()

