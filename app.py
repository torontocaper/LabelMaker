import datetime
import os
import time

import requests
from dotenv import load_dotenv
from flask import Flask, request
from flask_caching import Cache
from slack_sdk import WebClient

print(f"{datetime.datetime.now()}: This is printed from outside any function.")

# get the environment variables from .env
load_dotenv()

# get the bot token for authentication and fire up the slack client
bot_token = os.environ.get('BOT_TOKEN')
client = WebClient(token=bot_token)
headers = {"Authorization": "Bearer " + bot_token}

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/slack/events', methods=['POST'])
def slack_event_handler():
    print(f"{datetime.datetime.now()}: Request received. Starting event handler.")

    # get the request data in json format
    request_data = request.get_json()
    
    # authenticate URL
    if "challenge" in request_data:
        return request_data["challenge"]

    else:
        event_id = request_data["event_id"]

        event_data = request_data["event"]
        user_id = event_data["user"]
        reaction_type = event_data["reaction"]
        
        item_data = event_data["item"]
        channel_id = item_data["channel"]
        timestamp = item_data["ts"]      
    
        print(f"{datetime.datetime.now()}: Event: {event_id}; User: {user_id}; Rxn: {reaction_type}; Chan: {channel_id}; TS: {timestamp}.")

        if cache.get(event_id) is None:
            print(f"{datetime.datetime.now()}: Event not processed. Starting event processing.")
            
            # handle emoji reactions
            if reaction_type != "label":
                print(f"{datetime.datetime.now()}: Reaction was of type :{reaction_type}:. Ignoring.")
            else:
                
                conversation = client.conversations_replies(
                    channel=channel_id,
                    ts=timestamp
                )
                messages = conversation.get("messages")
                root_message = messages[0]

                if "files" in root_message:
                    print(f"{datetime.datetime.now()}: File found.")
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
                    print(f"{datetime.datetime.now()}: Temporary files deleted.")
                else:
                    print(f"{datetime.datetime.now()}: No file found.")
            cache.set(event_id, True)
            print(f"{datetime.datetime.now()}: Event processed.")

        else:
            print(f"{datetime.datetime.now()}: Event has already been processed.")

    return "OK"

def get_file_info(file_id):
    print(f"{datetime.datetime.now()}: Attempting to get VTT file from Slack.")
    response = client.files_info(file=file_id)
    if "vtt" not in response["file"]:
        print(f"{datetime.datetime.now()}: Slack has not generated a VTT file yet. Trying again in 10 seconds.")
        time.sleep(10.0)
        get_file_info(file_id)
    else: 
        print(f"{datetime.datetime.now()}: Transcript generated, link found.")
        vtt_link = response["file"]["vtt"]
    return vtt_link

def download_vtt_file(url, save_path):
    print(f"{datetime.datetime.now()}: Downloading VTT file.")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"{datetime.datetime.now()}: VTT file downloaded successfully and saved at: {save_path}")
    else:
        print(f"{datetime.datetime.now()}: Failed to download VTT file. Status code: {response.status_code}")
    return save_path

def convert_vtt_to_labels(vtt_file, labels_file):
    print(f"{datetime.datetime.now()}: Converting VTT to labels.")
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

    print(f'{datetime.datetime.now()}: Successfully converted {vtt_file} to Audacity labels format.')
    return labels_file

if __name__ == '__main__':
    app.run(debug=True)