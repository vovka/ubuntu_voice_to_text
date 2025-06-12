#!/bin/bash

# Exit on errors
set -e

# Step 1: Create venv if it doesn't exist
if [ ! -d "$HOME/venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv $HOME/venv
fi

# Step 2: Activate venv
source $HOME/venv/bin/activate

# Step 3: Install dependencies
pip install --upgrade pip
pip install sounddevice vosk pyaudio xdotool keyboard pynput pystray


# sudo setcap cap_net_admin,cap_net_raw+eip $(readlink -f $(which python3))

# Step 4: Run the voice typing script
python3 $HOME/bin/main.py
