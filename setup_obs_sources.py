"""Create the overlay sources in the current OBS scene (overlay.py also does this)."""
import os

from obs_link import connect, ensure_sources

os.chdir(os.path.dirname(os.path.abspath(__file__)))
client = connect()
scene, created = ensure_sources(client)
if created:
    for name in created:
        print(f"Created '{name}' in scene '{scene}'")
else:
    print(f"Sources already exist in scene '{scene}', nothing to do")
client.disconnect()
