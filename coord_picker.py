"""Pick regions on calibration_frame.png (make one with F8 or grab_frame.py).

Blue boxes = regions from config.py, scaled to this picture.
Click top-left, then bottom-right, to define a new region (red).
Region 1 = name, regions 2-7 = the six Pokemon slots.
Press Q when done: a block to paste into config.py is printed.
"""
import os
import sys

import cv2

from capture_logic import scale_region
from config import CALIBRATION_FRAME, NAME_REGION, POKEMON_REGIONS, REFERENCE_SIZE

os.chdir(os.path.dirname(os.path.abspath(__file__)))
frame = cv2.imread(CALIBRATION_FRAME)
if frame is None:
    sys.exit(f"{CALIBRATION_FRAME} not found. Press F8 while the overlay runs, "
             "or run grab_frame.py, on the team selection screen first.")

h, w = frame.shape[:2]
view_scale = min(1.0, 1600 / w, 900 / h)
size = (w, h)
current = [scale_region(NAME_REGION, size, REFERENCE_SIZE)] + \
          [scale_region(r, size, REFERENCE_SIZE) for r in POKEMON_REGIONS]

regions = []
state = {'pos': (0, 0), 'p1': None}


def on_mouse(event, x, y, flags, param):
    x, y = int(x / view_scale), int(y / view_scale)
    if event == cv2.EVENT_MOUSEMOVE:
        param['pos'] = (x, y)
    if event == cv2.EVENT_LBUTTONDOWN:
        if param['p1'] is None:
            param['p1'] = (x, y)
            print(f"Top-left: ({x}, {y})  -> now click bottom-right")
        else:
            x1, y1 = param['p1']
            region = (min(x1, x), min(y1, y), max(x1, x), max(y1, y))
            regions.append(region)
            print(f"Region {len(regions)}: {region}  "
                  f"size {region[2] - region[0]}x{region[3] - region[1]}")
            param['p1'] = None


cv2.namedWindow("Coord Picker")
cv2.setMouseCallback("Coord Picker", on_mouse, state)
print(f"Picture {w}x{h}. Blue = current config. Click twice per region. Q = done.")

while True:
    display = frame.copy()
    x, y = state['pos']
    for i, (x1, y1, x2, y2) in enumerate(current):
        cv2.rectangle(display, (x1, y1), (x2, y2), (255, 128, 0), 2)
        cv2.putText(display, "name" if i == 0 else f"poke{i}", (x1 + 4, y1 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 128, 0), 2)
    for i, (x1, y1, x2, y2) in enumerate(regions):
        cv2.rectangle(display, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(display, f"#{i + 1}", (x1 + 4, y1 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    if state['p1'] is not None:
        px, py = state['p1']
        cv2.rectangle(display, (px, py), (x, y), (0, 255, 0), 2)
    cv2.drawMarker(display, (x, y), (0, 255, 0), cv2.MARKER_CROSS, 20, 2)
    cv2.putText(display, f"({x}, {y})", (x + 10, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    if view_scale < 1.0:
        display = cv2.resize(display, None, fx=view_scale, fy=view_scale)
    cv2.imshow("Coord Picker", display)
    if cv2.waitKey(16) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

if regions:
    print("\nPaste this into config.py:\n")
    print(f"REFERENCE_SIZE = ({w}, {h})")
    print(f"NAME_REGION = {regions[0]}")
    if len(regions) > 1:
        print("POKEMON_REGIONS = [")
        for r in regions[1:7]:
            print(f"    {r},")
        print("]")
