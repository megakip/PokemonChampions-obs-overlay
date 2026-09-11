"""Everything that talks to OBS over WebSocket."""
import base64
import io
import os
import sys

import numpy as np
import obsws_python as obs
from dotenv import load_dotenv
from PIL import Image

from config import (
    OBS_HOST, OBS_PORT,
    OBS_NAME_SOURCE, OBS_POKEMON_SOURCE, OUTPUT_POKEMON,
)


def connect():
    """Connect to OBS. Exits with a clear message if that is not possible."""
    load_dotenv()
    password = os.getenv("OBS_PASSWORD", "")
    try:
        client = obs.ReqClient(host=OBS_HOST, port=OBS_PORT, password=password, timeout=15)
        client.get_version()
    except Exception as e:  # noqa: BLE001
        sys.exit(
            f"Cannot connect to OBS at {OBS_HOST}:{OBS_PORT} ({type(e).__name__}: {e}).\n"
            "Check that OBS is running, that the WebSocket server is enabled\n"
            "(Tools -> WebSocket Server Settings -> Enable WebSocket server)\n"
            "and that OBS_PASSWORD in .env matches the password in that dialog."
        )
    return client


def list_sources(client):
    inputs = [i["inputName"] for i in client.get_input_list().inputs]
    scenes = [s["sceneName"] for s in client.get_scene_list().scenes]
    return inputs, scenes


def grab_frame(client, source):
    """Current picture of an OBS source (or scene) as a BGR numpy array."""
    resp = client.send("GetSourceScreenshot",
                       {"sourceName": source, "imageFormat": "png"}, raw=True)
    data = resp["imageData"].split(",", 1)[1]
    img = Image.open(io.BytesIO(base64.b64decode(data))).convert("RGB")
    return np.array(img)[:, :, ::-1].copy()  # RGB -> BGR


def set_text(client, text):
    client.set_input_settings(name=OBS_NAME_SOURCE, settings={"text": text}, overlay=True)


def refresh_image(client, filepath):
    client.set_input_settings(name=OBS_POKEMON_SOURCE,
                              settings={"file": os.path.abspath(filepath)}, overlay=True)


def ensure_sources(client):
    """Create the two overlay sources in the current scene if they are missing."""
    scene = client.get_current_program_scene().current_program_scene_name
    existing = {i["inputName"] for i in client.get_input_list().inputs}
    canvas_w = client.get_video_settings().base_width
    created = []

    if OBS_NAME_SOURCE not in existing:
        kinds = client.get_input_kind_list(False).input_kinds
        text_kinds = sorted(k for k in kinds if k.startswith("text_gdiplus"))
        text_kind = text_kinds[-1] if text_kinds else "text_ft2_source_v2"
        client.create_input(scene, OBS_NAME_SOURCE, text_kind, {
            "text": "",
            "font": {"face": "Arial", "size": 56, "style": "Bold", "flags": 0},
            "color": 0xFFFFFFFF,
            "outline": True, "outline_size": 4, "outline_color": 0xFF000000,
        }, True)
        item = client.get_scene_item_id(scene, OBS_NAME_SOURCE).scene_item_id
        client.set_scene_item_transform(scene, item, {
            "positionX": 24, "positionY": 24, "alignment": 5,  # top-left
        })
        created.append(f"{OBS_NAME_SOURCE} ({text_kind})")

    if OBS_POKEMON_SOURCE not in existing:
        if not os.path.exists(OUTPUT_POKEMON):
            Image.new("RGBA", (1, 1), (0, 0, 0, 0)).save(OUTPUT_POKEMON)
        client.create_input(scene, OBS_POKEMON_SOURCE, "image_source", {
            "file": os.path.abspath(OUTPUT_POKEMON), "unload": False,
        }, True)
        item = client.get_scene_item_id(scene, OBS_POKEMON_SOURCE).scene_item_id
        client.set_scene_item_transform(scene, item, {
            "positionX": canvas_w - 24, "positionY": 24, "alignment": 6,  # top-right
            "boundsType": "OBS_BOUNDS_SCALE_INNER", "boundsAlignment": 6,
            "boundsWidth": 960, "boundsHeight": 120,
        })
        created.append(f"{OBS_POKEMON_SOURCE} (image_source)")

    return scene, created
