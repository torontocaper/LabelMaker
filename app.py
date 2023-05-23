import datetime
import os
import time

import requests
from dotenv import load_dotenv
from flask import Flask, request
from slack_sdk import WebClient

print(f"{datetime.datetime.now()}: LabelMaker is starting up. Let's make some labels!")

# get the environment variables from .env
load_dotenv()

# get the bot token for authentication and fire up the slack client
bot_token = os.environ.get('BOT_TOKEN')
client = WebClient(token=bot_token)
headers = {"Authorization": "Bearer " + bot_token}

app = Flask(__name__)
event_cache = []
print(f"{datetime.datetime.now()}: Current event cache: {event_cache}.")

@app.route('/slack/events', methods=['POST'])
def slack_event_handler():
    print(f"{datetime.datetime.now()}: Request received. Starting event handler.")
    
    # get the request data in json format
    request_data = request.get_json()
    event_context = request_data["event_context"]
    event_time = request_data["event_time"]
    print(f"{datetime.datetime.now()}: Outer event info: Context: {event_context}; Event Time: {event_time}")

    global event_cache
    
    # authenticate URL
    if "challenge" in request_data:
        challenge_key = request_data["challenge"]
        print(f"{datetime.datetime.now()}: This is an authentication challenge from Slack. The challenge key is {challenge_key}")
        return challenge_key

    else:
        event_id = request_data["event_id"]

        event_data = request_data["event"]
        user_id = event_data["user"]
        reaction_type = event_data["reaction"]
        
        item_data = event_data["item"]
        channel_id = item_data["channel"]
        timestamp = item_data["ts"]      
    
        print(f"{datetime.datetime.now()}: Inner event info: Event: {event_id}; User: {user_id}; Reaction: {reaction_type}; Channel: {channel_id}; Timestamp: {timestamp}.")

        if event_id in event_cache:
            print(f"{datetime.datetime.now()}: Event {event_id} has already been processed. Exiting event handler.")
            return "OK"

        else: 
            print(f"{datetime.datetime.now()}: Event {event_id} has not been processed. Starting event processing.")
            event_cache.append(event_id)

            # handle emoji reactions
            if reaction_type != "label":
                print(f"{datetime.datetime.now()}: Reaction was of type :{reaction_type}:. Exiting event handler.")
                return "OK"
            else:
                conversation = client.conversations_replies(
                    channel=channel_id,
                    ts=timestamp
                )
                messages = conversation.get("messages")
                root_message = messages[0]

                if "files" not in root_message:
                    print(f"{datetime.datetime.now()}: No file found. Exiting event handler.")
                    return "OK"
                else:
                    print(f"{datetime.datetime.now()}: File found. Proceeding with file-handling steps.")
                    file_id = root_message["files"][0]["id"]
                    file_vtt = get_file_info(file_id)
                    save_location = event_id + '.vtt'
                    vtt_file_for_conversion = download_vtt_file(file_vtt, save_location)
                    txt_file_output = event_id + ".txt"
                    finished_txt_file = convert_vtt_to_labels(vtt_file_for_conversion, txt_file_output)
                    print(f"{datetime.datetime.now()}: Uploading labels file to Slack.")
                    client.files_upload_v2(
                    channel=channel_id,
                    thread_ts=timestamp,
                    initial_comment="Thanks for using LabelMaker! Here's your labels file:",
                    file=finished_txt_file
                )
                    os.remove(vtt_file_for_conversion)
                    os.remove(finished_txt_file)
                    print(f"{datetime.datetime.now()}: Temporary files deleted.")


            print(f"{datetime.datetime.now()}: Event {event_id} processed.")

    print(f"{datetime.datetime.now()}: Current event cache: {event_cache}.")
    return "OK"

def get_file_info(file_id):
    print(f"{datetime.datetime.now()}: Attempting to get VTT file from Slack. This may take some time.")
    response = client.files_info(file=file_id)
    while "vtt" not in response["file"]:
        print(f"{datetime.datetime.now()}: Slack has not generated a VTT file yet. Waiting 1 second, then re-trying.")
        time.sleep(1.0)
        response = client.files_info(file=file_id)
    print(f"{datetime.datetime.now()}: Transcript generated, link found. Proceeding with download.")
    vtt_link = response["file"]["vtt"]
    return vtt_link

def download_vtt_file(url, save_path):
    print(f"{datetime.datetime.now()}: Downloading VTT file to to temporary path {save_path}.")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"{datetime.datetime.now()}: VTT file downloaded successfully.")
    else:
        print(f"{datetime.datetime.now()}: Failed to download VTT file. Status code: {response.status_code}")
    return save_path

def convert_vtt_to_labels(vtt_file, labels_file):
    print(f"{datetime.datetime.now()}: Converting VTT file to Audacity labels.")
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

    print(f'{datetime.datetime.now()}: Successfully converted VTT file to Audacity labels format.')
    return labels_file

if __name__ == '__main__':
    app.run(debug=True)