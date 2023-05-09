# Enable debug logging
import logging
import sys

logging.basicConfig(level=logging.DEBUG)
# Verify it works
from slack_sdk import WebClient

client = WebClient()
api_response = client.api_test()