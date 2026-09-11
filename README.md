# Pokemon Champions OBS Overlay

An OBS overlay tool for live streaming "Pokemon Champions".
Press a hotkey on the team selection screen to instantly show the opponent's player name and 6 Pokemon in OBS.

This is a fork of [Ruprous/PokemonChampions-obs-overlay](https://github.com/Ruprous/PokemonChampions-obs-overlay).
The original reads the picture from a capture card. **This fork takes the picture straight from an OBS source**,
so it also works when the game reaches OBS in another way: AirPlay / phone screen mirroring, a window capture,
a capture card that is already in use by OBS, and so on. No second video device is needed.

## Features

- Reads the opponent's player name with OCR and shows it as a text source in OBS
- Cuts out the opponent's 6 Pokemon slots, puts them side by side, and shows them as an image source in OBS
- One hotkey to capture, one to clear
- Creates the two OBS sources for you on the first run
- Region coordinates scale automatically to the size of your picture, with a picker tool to fine-tune them

## Requirements

- Windows
- OBS Studio 30.0.0+ with the WebSocket server enabled (built in since OBS 28)
- Python 3.12+
- The game visible in an OBS source (AirPlay receiver, capture card, window capture, ...)

## Installation

```bash
git clone https://github.com/megakip/PokemonChampions-obs-overlay.git
cd PokemonChampions-obs-overlay
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

(With [uv](https://docs.astral.sh/uv/): `uv venv .venv --python 3.12` and `uv pip install --python .venv\Scripts\python.exe -r requirements.txt`.)

### Dependencies

| Package | Purpose |
|---|---|
| `obsws-python` | OBS WebSocket communication (grab the picture, update the sources) |
| `opencv-python` | Image processing and the coordinate picker window |
| `numpy` | Image array manipulation |
| `Pillow` | PNG image creation with transparency |
| `keyboard` | Global hotkey detection |
| `python-dotenv` | Load the OBS password from `.env` |
| `easyocr` | OCR for the opponent name (JP/EN/ZH/KO) |

## Setup

### 1. OBS WebSocket

In OBS: **Tools → WebSocket Server Settings**, tick **Enable WebSocket server**, click **OK**.
Keep the port at 4455. Click **Show Connect Info** to see the password.

Copy `.env.example` to `.env` and put that password in it:

```
OBS_PASSWORD=your_password_here
```

Test it:

```bash
.venv\Scripts\python test_connection.py
```

### 2. Pick the source that shows the game

Open `config.py` and set `OBS_CAPTURE_SOURCE` to the exact name of the OBS source that shows the game
(for example `AirPlay Receiver` or `Capture card`). A scene name also works.

### 3. First run

Double-click `start_overlay.bat`. On the first run it:

- creates the sources `pokecham_auto-name` (Text GDI+) and `pokecham_auto-poke` (Image) in the current scene,
  name at the top-left and Pokemon at the top-right. Move and resize them in OBS however you like.
- downloads the OCR model (about 100 MB, once).

### 4. Check the coordinates

The default regions are for a 1920x1080 Nintendo Switch picture and are scaled to your picture size.
If the captured name or Pokemon look cut off:

1. Go to a team selection screen in the game and press `F8`. This saves `calibration_frame.png`.
2. Run `.venv\Scripts\python coord_picker.py`. Blue boxes show the current regions.
3. Click top-left, then bottom-right, for the name (region 1) and the six Pokemon slots (regions 2-7). Press `Q`.
4. Paste the printed block into `config.py` and restart the tool.

## Usage

Double-click `start_overlay.bat`.

| Hotkey | Action |
|---|---|
| `F9` | Capture the current picture and send it to OBS |
| `F10` | Clear the overlay |
| `F8` | Save the current picture to `calibration_frame.png` |
| `Ctrl+Alt+Q` | Quit (closing the window also works) |

Hotkeys are global, so they work while the game or OBS has focus. Change them in `config.py`.

## Example

### Step 1 — Press `F9` on the team selection screen

![Team selection screen](images/ex_select.png)

> The opponent's 6 Pokemon are listed on the right side of the screen.

### Step 2 — The opponent info is shown in OBS

![OBS stream UI sample](images/ex_obs_uisample.png)

> Top-right: the opponent's 6 Pokemon. Top-left: the opponent's name (hidden here for privacy).

### Step 3 — Press `F10` after the battle

## File Structure

```
PokemonChampions-obs-overlay/
├── overlay.py            # Main script (hotkeys, capture, OCR, OBS updates)
├── obs_link.py           # OBS WebSocket: connect, grab picture, create/update sources
├── capture_logic.py      # Cropping, scaling and composing (no OBS code)
├── config.py             # Source name, regions, hotkeys
├── grab_frame.py         # Save the current OBS picture to calibration_frame.png
├── coord_picker.py       # Pick regions on calibration_frame.png
├── setup_obs_sources.py  # Create the two OBS sources (overlay.py does this too)
├── test_connection.py    # Test the OBS WebSocket connection
├── start_overlay.bat     # Windows launcher
├── requirements.txt      # Python dependencies
└── .env.example          # Template for .env
```

## Notes

- Never commit `.env` to Git, it contains your OBS password
- OBS must be running before you start the tool
- The name OCR works best when the picture is at least 720p. `OCR_UPSCALE` in `config.py` enlarges the name crop first.
