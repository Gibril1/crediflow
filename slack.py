import os
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SlackServices:
    def __init__(self):
        # Initialize the Slack client with the bot token
        self.slack_token = os.getenv("SLACK_BOT_TOKEN")
        if not self.slack_token:
            raise ValueError("SLACK_BOT_TOKEN is not set in the environment variables.")
        self.client = AsyncWebClient(token=self.slack_token)

    async def send_slack_message(self, channel, text):
        """Sends a message to a Slack channel."""
        try:
            response = await self.client.chat_postMessage(channel=channel, text=text)
            logger.info(f"Message sent to {channel}: {text}")
            return response
        except SlackApiError as e:
            logger.error(f"Error sending message to Slack: {e.response['error']}")
            raise e


slack_services = SlackServices()
