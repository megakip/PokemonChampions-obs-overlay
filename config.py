# ---------------------------------------------------------------------------
# OBS connection
# ---------------------------------------------------------------------------
OBS_HOST = "localhost"
OBS_PORT = 4455
# The WebSocket password is read from the .env file (OBS_PASSWORD=...).

# The OBS source (or scene) that shows the game. The tool takes its picture
# straight from OBS, so anything OBS can show works: AirPlay / phone mirroring,
# a capture card, a window capture, ... Use the exact name from the Sources list.
OBS_CAPTURE_SOURCE = "AirPlay Receiver"

# ---------------------------------------------------------------------------
# Regions on the game picture (x1, y1, x2, y2)
# ---------------------------------------------------------------------------
# The numbers below are for a 1920x1080 picture (Nintendo Switch capture).
# They are scaled automatically to the real size of the captured picture.
# If they do not line up on your setup: press F8 on the team selection screen
# and run coord_picker.py to pick new ones (it prints a block to paste here).
REFERENCE_SIZE = (1920, 1080)

# Opponent player name
NAME_REGION = (1563, 95, 1845, 141)

# Opponent Pokemon, 6 slots top to bottom
POKEMON_REGIONS = [
    (1603, 156, 1844, 264),
    (1603, 282, 1844, 390),
    (1603, 408, 1844, 516),
    (1603, 534, 1844, 642),
    (1603, 660, 1844, 768),
    (1603, 786, 1844, 894),
]

# ---------------------------------------------------------------------------
# Output files (relative to this folder)
# ---------------------------------------------------------------------------
OUTPUT_POKEMON = "output_pokemon.png"
CALIBRATION_FRAME = "calibration_frame.png"

# ---------------------------------------------------------------------------
# OBS sources that show the result. They are created automatically on the
# first run if they do not exist yet.
# ---------------------------------------------------------------------------
OBS_NAME_SOURCE    = "pokecham_auto-name"  # Text (GDI+) source
OBS_POKEMON_SOURCE = "pokecham_auto-poke"  # Image source

# ---------------------------------------------------------------------------
# OCR (reading the opponent name)
# ---------------------------------------------------------------------------
# Languages: 'en' plus at most one of 'ja', 'ch_tra', 'ch_sim', 'ko'
OCR_LANGUAGES = ['ja', 'en']
# Enlarge the name crop before OCR. Helps a lot with small (phone) pictures.
OCR_UPSCALE = 2

# ---------------------------------------------------------------------------
# Hotkeys (global, they work while the game or OBS has focus)
# ---------------------------------------------------------------------------
HOTKEY_CAPTURE   = "F9"          # read the opponent and show it in OBS
HOTKEY_CLEAR     = "F10"         # hide the overlay again
HOTKEY_CALIBRATE = "F8"          # save the current picture to calibration_frame.png
HOTKEY_QUIT      = "ctrl+alt+q"  # stop the tool (closing the window also works)
