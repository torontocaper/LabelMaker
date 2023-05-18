import os
import time

import requests
from dotenv import load_dotenv
from flask import Flask, request
from slack_sdk import WebClient

# from slack_sdk.errors import SlackApiError

load_dotenv()

# get the bot token for authentication and fire up the slack client
bot_token = os.environ.get('BOT_TOKEN')
client = WebClient(token=bot_token)
headers = {"Authorization": "Bearer " + bot_token}

# initiate global variables
app_id = os.environ.get('APP_ID')
channel_id = file_id = timestamp = message_text = ""

app = Flask(__name__)
@app.route('/slack/events', methods=['POST'])
def slack_event_handler():

    # get the request data in json format
    request_data = request.get_json()

    # authenticate URL
    if "challenge" in request_data:
        return request_data["challenge"]

    # get the event id
    event_id = request_data["event_id"]

    global message_text
    global channel_id
    global file_id
    global timestamp

    # handle emoji reactions
    reaction_type = request_data["event"]["reaction"]
    if reaction_type != "label":
        print(f"Can't compute :{reaction_type}: reaction!")
    else:        
        channel_id = request_data["event"]["item"]["channel"]
        timestamp = request_data["event"]["item"]["ts"]
        conversation = client.conversations_replies(
            channel=channel_id,
            ts=timestamp
        )
        messages = conversation.get("messages")
        root_message = messages[0]

        if "files" in root_message:   
            file_id = root_message["files"][0]["id"]
            file_vtt = get_file_info(file_id)
            save_location = event_id + '.vtt'
            vtt_file_for_conversion = download_vtt_file(file_vtt, save_location)
            txt_file_output = event_id + ".txt"
            finished_txt_file = convert_vtt_to_labels(vtt_file_for_conversion, txt_file_output)
            client.files_upload_v2(
            channel=channel_id,
            thread_ts=timestamp,
            initial_comment="Thanks for using LabelMaker! Here's your labels file:",
            file=finished_txt_file
        )
            os.remove(vtt_file_for_conversion)
            os.remove(finished_txt_file)

    return "OK"

def convert_vtt_to_labels(vtt_file, labels_file):
    with open(vtt_file, 'r') as vtt:
        vtt_lines = vtt.readlines()

    labels = []
    for line in vtt_lines:
        line_index = vtt_lines.index(line)
        line = line.strip()
        if line.startswith('00:'):
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
    return labels_file

def download_vtt_file(url, save_path):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"VTT file downloaded successfully and saved at: {save_path}")
    else:
        print(f"Failed to download VTT file. Status code: {response.status_code}")
    return save_path

def get_file_info(file_id):
    response = client.files_info(file=file_id)
    if "vtt" in response["file"]:
        vtt_link = response["file"]["vtt"]
    else:
        time.sleep(1)
        get_file_info(file_id)
    return vtt_link

if __name__ == '__main__':
    app.run(debug=True)