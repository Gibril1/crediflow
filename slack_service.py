import os
import aiohttp
from fastapi import status, HTTPException
from dotenv import load_dotenv
from slack import WebClient
from slack_sdk.errors import SlackApiError
import logging

load_dotenv

SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

logger = logging.getLogger(__name__)

class SlackServices:
    def __init__(self):
        # SLACK_APP_TOKEN
        self.slack_token = SLACK_APP_TOKEN
        self.client = WebClient(token=self.slack_token)
    
    async def send_slack_message(self, channel, text):
        try:
            response = self.client.chat_postMessage(channel=channel, text=text)
            return {"ok": True, "message": "Message has been sent"}
        except SlackApiError as e:
            logger.error(f"Error sending message: {e.response.get('error', 'Unknown error')}")
            # Extract relevant error details
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": e.response.get("error", "Unknown error")}
            )
        
    
    async def get_all_slack_users(self):
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.slack_token}"}
                async with session.get(
                    "https://slack.com/api/users.list", headers=headers
                ) as response:
                    response.raise_for_status()  # Raise an error for non-2xx responses
                    data = await response.json()

                    users = data.get("members", [])

                    for user in users:
                        user_id = user.get("id")
                        try:
                            profile_response = await self.get_user_profile(
                                user_id, self.slack_token
                            )

                            if profile_response:
                                user["email"] = profile_response.get("email", "")
                        except Exception as profile_error:
                            # Handle error while getting user profile
                            logger.error(
                                f"Error getting user profile for user {user_id}: {str(profile_error)}"
                            )

                    return users
        except Exception as e:
            # Handle error for the main request
            logger.error(f"Error getting Slack users: ", e)
            return e
        
    async def get_user_profile(self, user_id, slack_token):
        try:
            headers = {"Authorization": f"Bearer {slack_token}"}
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://slack.com/api/users.profile.get?user={user_id}",
                    headers=headers,
                ) as profile_response:
                    profile_response.raise_for_status()  # Raise an error for non-2xx responses
                    profile_data = await profile_response.json()
                    return profile_data.get("profile", {})

        except Exception as e:
            # Handle error while getting user profile
            logging.error(f"Error getting user profile for user {user_id}: ", e)
            return e
        
    async def get_all_slack_channels(self):
        try:
            channels = []
            cursor = None

            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.slack_token}"}
                params = {
                    "types": "public_channel,private_channel",
                    "limit": 1000,
                }  # Include both public and private channels

                while True:
                    if cursor:
                        params["cursor"] = cursor

                    async with session.get(
                        "https://slack.com/api/conversations.list",
                        headers=headers,
                        params=params,
                    ) as response:
                        data = await response.json()
                        channels.extend(data.get("channels", []))

                        cursor = data.get("response_metadata", {}).get("next_cursor")
                        if not cursor:
                            break

            return channels
        except Exception as e:
            # Handle error while getting user profile
            logging.error(f"Error getting slack channels: ", e)
            return e


slack_services = SlackServices()