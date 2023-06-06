import requests
import time
import re
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Your Ngrok token
ngrok_token = os.getenv('NGROK_TOKEN')
# SSH config file path
config_path = os.getenv('CONFIG_PATH')
# Tunnel name to track
tunnel_name = os.getenv('TUNNEL_NAME')

def get_tunnel_info():
    try:
        # Fetch the tunnel details from Ngrok API
        response = requests.get('https://api.ngrok.com/tunnels', headers={'Authorization': f'Bearer {ngrok_token}', 'ngrok-version': '2' })
        response.raise_for_status()
        data = response.json()

        print(str(data))

        for tunnel in data['tunnels']:
            #tunnel doesn't have a name & we only have one tunnel...
            #if tunnel['name'] == tunnel_name:
            return tunnel['public_url'].split('//')[1].split(':')

    except requests.exceptions.RequestException as e:
        print(f"Error getting tunnel info: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return None, None

def update_config_file(hostname, port):
    try:
        # Read the original file
        with open(config_path, 'r') as file:
            lines = file.readlines()

        # Update the necessary line
        for i, line in enumerate(lines):
            if 'HostName' in line and tunnel_name in lines[i-1]:
                lines[i] = f'  HostName {hostname}\n'
            elif 'Port' in line and tunnel_name in lines[i-2]:
                lines[i] = f'  Port {port}\n'

        # Write the updated content back to the file
        with open(config_path, 'w') as file:
            file.writelines(lines)

    except Exception as e:
        print(f"Error updating config file: {e}")

prev_hostname, prev_port = None, None

while True:
    hostname, port = get_tunnel_info()
    
    if hostname and port and (hostname != prev_hostname or port != prev_port):
        update_config_file(hostname, port)
        print(f'Tunnel {tunnel_name} info updated. New HostName is {hostname} and new Port is {port}.')
    else:
        print(f'No updates necessary')

    prev_hostname, prev_port = hostname, port

    # Wait for 5 minutes (or any desired period) before checking again
    time.sleep(5 * 60)
    