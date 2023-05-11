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

app = Flask(__name__)

# initiate global variables
app_id = os.environ.get("APP_ID")
channel_id = ""
file_id = ""
timestamp = ""
# might not need this // has_file = False
message_text = f"Thanks for the message."

@app.route('/slack/events', methods=['POST'])
def slack_event_handler():
    # get the request data in json format
    request_data = request.get_json()
    print(request_data)
    # get the event type
    event_type = request_data["event"]["type"]
    global message_text
    global channel_id
    global file_id
    global timestamp
           
    # get the timestamp and channel ID from the "message" event
    if event_type == "message":
        channel_id = request_data["event"]["channel"]
        timestamp = request_data["event"]["ts"]

    elif event_type == "file_public" or event_type == "file_shared":
        file_id = request_data["event"]["file_id"]
        file_vtt = get_file_info(file_id)
        message_text = f"Your file id is {file_id} and your vtt file is at {file_vtt}."
    
    # avoid infinite loop
    if "bot_id" not in request_data["event"]:
        send_message(channel_id, message_text, timestamp)
        
    return "OK"
    
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

if __name__ == '__main__':
    app.run(debug=True)


### THE BELOW CODE HANDLES VERIFICATION REQUESTS -- DON'T DELETE ###

""" if "challenge" in request_data:
    return request_data["challenge"] """