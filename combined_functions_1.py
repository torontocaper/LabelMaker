# get the vtt file from Slack

# from pprint import pprint

import os

import dotenv
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

dotenv.load_dotenv()

bot_token = os.environ.get("BOT_TOKEN")

client = WebClient(token=bot_token)

# would be nice to get the file_id from an event listener -- tough in python

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

# download the vtt file
vtt_url = vtt_link
save_location = 'combined_test.vtt'
download_vtt_file(vtt_url, save_location)

# convert to Audacity labels

def convert_vtt_to_labels(vtt_file, labels_file):
    with open(vtt_file, 'r') as vtt:
        vtt_lines = vtt.readlines()

    labels = []
    for line in vtt_lines:
        line_index = vtt_lines.index(line)
        line = line.strip()
        if line.startswith('00:'):  # Assuming timestamp format: hh:mm:ss.sss
            start_time, end_time = line.split(' --> ')
            start_time_hours, start_time_minutes, start_time_seconds = start_time.split(":")
            start_time_audacity = float(start_time_hours)*3600 + float(start_time_minutes)*60 + float(start_time_seconds)
            end_time_hours, end_time_minutes, end_time_seconds = end_time.split(":")
            end_time_audacity = float(end_time_hours)*3600 + float(end_time_minutes)*60 + float(end_time_seconds)
            label_text = vtt_lines[line_index + 1].strip("- ")  # Get the next line as label text
            label = f'{start_time_audacity}\t{end_time_audacity}\t{label_text}'
            labels.append(label)

    with open(labels_file, 'w') as labels_out:
        labels_out.write(''.join(labels))

    print(f'Successfully converted {vtt_file} to Audacity labels format.')

# convert the file
vtt_file = 'combined_test.vtt'
labels_file = 'combined_test_converted.txt'
convert_vtt_to_labels(vtt_file, labels_file)
