"""Save the current picture of the capture source to calibration_frame.png.

Usage: python grab_frame.py [source name]
"""
import os
import sys

import cv2

from config import CALIBRATION_FRAME, OBS_CAPTURE_SOURCE
from obs_link import connect, grab_frame, list_sources

os.chdir(os.path.dirname(os.path.abspath(__file__)))
source = sys.argv[1] if len(sys.argv) > 1 else OBS_CAPTURE_SOURCE

client = connect()
try:
    frame = grab_frame(client, source)
except Exception as e:  # noqa: BLE001
    inputs, scenes = list_sources(client)
    sys.exit(f"Could not grab '{source}': {e}\nSources: {inputs}\nScenes: {scenes}")
cv2.imwrite(CALIBRATION_FRAME, frame)
print(f"Saved {CALIBRATION_FRAME} ({frame.shape[1]}x{frame.shape[0]}) from '{source}'")
client.disconnect()
