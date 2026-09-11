import os
import sys
import threading

# The EasyOCR download progress bar uses characters the default Windows
# console encoding cannot print. Make stdout UTF-8 before easyocr is imported.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import cv2
import easyocr
import keyboard

from capture_logic import blank_image, compose_pokemon, crop, ocr_name, scale_region
from config import (
    CALIBRATION_FRAME, HOTKEY_CALIBRATE, HOTKEY_CAPTURE, HOTKEY_CLEAR, HOTKEY_QUIT,
    NAME_REGION, OBS_CAPTURE_SOURCE, OCR_LANGUAGES, OCR_UPSCALE, OUTPUT_POKEMON,
    POKEMON_REGIONS, REFERENCE_SIZE,
)
from obs_link import connect, ensure_sources, grab_frame, list_sources, refresh_image, set_text

os.chdir(os.path.dirname(os.path.abspath(__file__)))

client = connect()
print(f"Connected to OBS {client.get_version().obs_version}")

scene, created = ensure_sources(client)
for name in created:
    print(f"Created OBS source '{name}' in scene '{scene}'")

inputs, scenes = list_sources(client)
if OBS_CAPTURE_SOURCE not in inputs and OBS_CAPTURE_SOURCE not in scenes:
    print(f"WARNING: OBS has no source called '{OBS_CAPTURE_SOURCE}'. "
          f"Set OBS_CAPTURE_SOURCE in config.py to one of: {inputs + scenes}")

print("Loading OCR model...")
reader = easyocr.Reader(OCR_LANGUAGES, gpu=False)
print("OCR model ready")


def get_frame():
    try:
        return grab_frame(client, OBS_CAPTURE_SOURCE)
    except Exception as e:  # noqa: BLE001
        print(f"Could not grab a picture from OBS source '{OBS_CAPTURE_SOURCE}': {e}")
        return None


def regions_for(frame):
    size = (frame.shape[1], frame.shape[0])
    name = scale_region(NAME_REGION, size, REFERENCE_SIZE)
    slots = [scale_region(r, size, REFERENCE_SIZE) for r in POKEMON_REGIONS]
    return name, slots


def capture():
    frame = get_frame()
    if frame is None:
        return
    name_region, slot_regions = regions_for(frame)

    name_text = ocr_name(reader, crop(frame, name_region), OCR_UPSCALE)
    set_text(client, name_text)
    print(f"Name: {name_text!r}")

    compose_pokemon([crop(frame, r) for r in slot_regions]).save(OUTPUT_POKEMON)
    refresh_image(client, OUTPUT_POKEMON)
    print("Capture done")


def clear():
    set_text(client, "")
    blank_image().save(OUTPUT_POKEMON)
    refresh_image(client, OUTPUT_POKEMON)
    print("Overlay cleared")


def calibrate():
    frame = get_frame()
    if frame is None:
        return
    cv2.imwrite(CALIBRATION_FRAME, frame)
    print(f"Saved {CALIBRATION_FRAME} ({frame.shape[1]}x{frame.shape[0]}). "
          f"Run coord_picker.py to check or pick the regions.")


task_lock = threading.Lock()


def run_async(func):
    def wrapper():
        if not task_lock.acquire(blocking=False):
            print("Still busy, try again in a moment.")
            return
        try:
            func()
        except Exception as e:  # noqa: BLE001
            print(f"Error: {e}")
        finally:
            task_lock.release()

    threading.Thread(target=wrapper, daemon=True).start()


keyboard.add_hotkey(HOTKEY_CAPTURE, lambda: run_async(capture))
keyboard.add_hotkey(HOTKEY_CLEAR, lambda: run_async(clear))
keyboard.add_hotkey(HOTKEY_CALIBRATE, lambda: run_async(calibrate))

print(f"Ready | {HOTKEY_CAPTURE}: capture | {HOTKEY_CLEAR}: clear | "
      f"{HOTKEY_CALIBRATE}: save calibration picture | {HOTKEY_QUIT}: quit")
keyboard.wait(HOTKEY_QUIT)

client.disconnect()
