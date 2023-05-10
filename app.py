import json
import os

import dotenv
import requests
from flask import Flask, jsonify, request
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

dotenv.load_dotenv()

bot_token = os.environ.get("BOT_TOKEN")

client = WebClient(token=bot_token)
app = Flask(__name__)

@app.route('/slack/events', methods=['POST'])
def slack_event_handler():
    request_data = request.get_json()
    event_type = request_data["event"]["type"]
    channel = ""
    file_id = ""
    timestamp = ""
    message_text = ""
    
    if request_data["event"]["type"] == "message":
        channel = request_data["event"]["channel"]
        timestamp = request_data["event"]["ts"]
        message_text = f"This is a message. Its channel ID is {channel} and its TS is {timestamp}."

        client.chat_postMessage(
            channel=channel,
            text=message_text,
            thread_ts=timestamp
        )

    elif request_data["event"]["type"] == "file_public":
        file_id = request_data["event"]["file_id"]
        message_text = f"This is a file_public. The file ID is {file_id}."
        
    elif request_data["event"]["type"] == "file_shared":
        file_id = request_data["event"]["file_id"]
        channel = request_data["event"]["channel_id"]
        message_text = f"This is a file_shared. The file id is {file_id} and the channel is {channel}."

        client.chat_postMessage(
            channel=channel,
            text=message_text
        )
    
    return "OK"
    
    """ print(request_data)
    if request_data["event"]["type"] == "file_shared": # request_data["event"]["type"] == "file_public" or 
        channel_id = request_data["event"]["channel_id"]
        event_ts = request_data["ts"]
        file_id = request_data["event"]["file_id"]
        
        try:
            result = client.chat_postMessage(
            channel=channel_id,
            thread_ts=event_ts,
            text=f"Thanks for uploading a file! Your file id is {file_id}"
        )
            print(result)
        
        except SlackApiError as e:
        
            print(f"Error posting message: {e}")

        # file_info = client.files_info(file=file_id)
        # data = file_info.data
        # file_data = data["file"]
        # vtt_link = file_data["vtt"]
        # print(vtt_link)
        # user_id = request_data["event"]["user_id"]
        return "File uploaded and processed"
    else:
        return "No file uploaded" """

if __name__ == '__main__':
    app.run(debug=True)

