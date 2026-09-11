"""Check that the tool can reach OBS."""
from obs_link import connect

client = connect()
version = client.get_version()
print("Connected!")
print(f"OBS version:       {version.obs_version}")
print(f"WebSocket version: {version.obs_web_socket_version}")
client.disconnect()
