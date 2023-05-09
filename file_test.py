# file_test.py
import os
from pprint import pprint

import dotenv
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

dotenv.load_dotenv()

bot_token = os.environ.get("BOT_USER_TOKEN")
user_token = os.environ.get("USER_TOKEN")

# link to file: https://torontocaper.slack.com/files/U039LV1CHT8/F056EM1PXPU/clip-amb-1.mp3
# member id: U039LV1CHT8

client = WebClient(token=bot_token)

file_id = "F056EM1PXPU"

file_info = client.files_info(file=file_id)

vtt_link = file_info["file"]["vtt"]

headers = {"Authorization": "Bearer " + bot_token}

def download_vtt_file(url, save_path):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"VTT file downloaded successfully and saved at: {save_path}")
    else:
        print(f"Failed to download VTT file. Status code: {response.status_code}")

# Example usage
vtt_url = vtt_link
save_location = 'file_test.vtt'
download_vtt_file(vtt_url, save_location)
