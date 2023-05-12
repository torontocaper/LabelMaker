import json
import os
import time

import dotenv
import requests
from flask import Flask, jsonify, request
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# get the bot token for authentication and fire up the slack client
dotenv.load_dotenv()
bot_token = os.environ.get("BOT_TOKEN")
client = WebClient(token=bot_token)
headers = {"Authorization": "Bearer " + bot_token}

app = Flask(__name__)

# initiate global variables
app_id = os.environ.get("APP_ID")
channel_id = file_id = timestamp = message_text = ""
processed_events_list = "processed_events.txt"

@app.route('/slack/events', methods=['POST'])
def slack_event_handler():

    # get the request data in json format
    request_data = request.get_json()
    
    ### DON'T DELETE ###
    # if "challenge" in request_data:
    #    return request_data["challenge"]
    ### DON'T DELETE ###

    # get the event type, id
    event_type = request_data["event"]["type"]
    event_id = request_data["event_id"]

    global message_text
    global channel_id
    global file_id
    global timestamp

    if is_event_processed(event_id):
        print(f"Event ID {event_id} has already been processed.")
    else:        
        # get the timestamp and channel ID from the "message" event
        if event_type == "message":
            channel_id = request_data["event"]["channel"]
            timestamp = request_data["event"]["ts"]
            mark_event_as_processed(event_id)
            print(f"The message with event ID {event_id} has been processed.")

        elif event_type == "file_shared":
            file_id = request_data["event"]["file_id"]
            file_vtt = get_file_info(file_id)
            save_location = event_id + '.vtt'
            vtt_file_for_conversion = download_vtt_file(file_vtt, save_location)
            mark_event_as_processed(event_id)
            print(f"The file with event ID {event_id} has been processed.")
    
    return "OK"
                                            
# download the vtt file
def download_vtt_file(url, save_path):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"VTT file downloaded successfully and saved at: {save_path}")
    else:
        print(f"Failed to download VTT file. Status code: {response.status_code}")
    return file

# get the file info
def get_file_info(file_id):
    response = client.files_info(file=file_id)
    if "vtt" in response["file"]:
        vtt_link = response["file"]["vtt"]
    else:
        time.sleep(1)
        get_file_info(file_id)
    return vtt_link

# send the finished message 
def send_message(channel, message, timestamp):
    client.chat_postMessage(
        text=message,
        channel=channel,
        thread_ts=timestamp
    )
    return "OK"

# check if the event has been handled
def is_event_processed(event_id):
    with open(processed_events_list, "r") as file:
        processed_ids = file.read().splitlines()
        return event_id in processed_ids

# mark event as processed
def mark_event_as_processed(event_id):
    with open(processed_events_list, "a") as file:
        file.write(event_id + "\n")

if __name__ == '__main__':
    app.run(debug=True)