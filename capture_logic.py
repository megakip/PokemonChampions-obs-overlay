"""Pure image functions. No OBS or hotkey code in here, so it is easy to test."""
import cv2
import numpy as np
from PIL import Image


def scale_region(region, frame_size, reference_size):
    """Scale a (x1, y1, x2, y2) region from reference_size to frame_size."""
    fw, fh = frame_size
    rw, rh = reference_size
    if (fw, fh) == (rw, rh):
        return tuple(region)
    sx, sy = fw / rw, fh / rh
    x1, y1, x2, y2 = region
    return (int(round(x1 * sx)), int(round(y1 * sy)),
            int(round(x2 * sx)), int(round(y2 * sy)))


def crop(frame, region):
    x1, y1, x2, y2 = region
    h, w = frame.shape[:2]
    x1, x2 = max(0, min(x1, w)), max(0, min(x2, w))
    y1, y2 = max(0, min(y1, h)), max(0, min(y2, h))
    return frame[y1:y2, x1:x2]


def ocr_name(reader, img_bgr, upscale=1):
    """Read text from a BGR crop with an easyocr.Reader."""
    if img_bgr.size == 0:
        return ''
    if upscale and upscale > 1:
        img_bgr = cv2.resize(img_bgr, None, fx=upscale, fy=upscale,
                             interpolation=cv2.INTER_CUBIC)
    results = reader.readtext(img_bgr)
    return ' '.join(r[1] for r in results) if results else ''


def compose_pokemon(slots, margin=20):
    """Put the 6 BGR slot crops next to each other on a transparent RGBA image."""
    slots = [s for s in slots if s.size > 0]
    if not slots:
        return blank_image()
    h = max(s.shape[0] for s in slots)
    w_total = sum(s.shape[1] for s in slots) + margin * (len(slots) - 1)
    combined = np.zeros((h, w_total, 4), dtype=np.uint8)
    x = 0
    for s in slots:
        rgb = cv2.cvtColor(s, cv2.COLOR_BGR2RGB)
        combined[:s.shape[0], x:x + s.shape[1], :3] = rgb
        combined[:s.shape[0], x:x + s.shape[1], 3] = 255
        x += s.shape[1] + margin
    return Image.fromarray(combined, "RGBA")


def blank_image():
    return Image.new("RGBA", (1, 1), (0, 0, 0, 0))
