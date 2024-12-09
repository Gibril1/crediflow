from fastapi import FastAPI, status, HTTPException
import uvicorn
from pydantic import BaseModel
from typing import List
from api_service import get_products_api
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
import asyncio
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
import re

load_dotenv()


# Initializes your app with your bot token and socket mode handler
slack_app = AsyncApp(token=os.getenv("SLACK_BOT_TOKEN"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    slack_handler = AsyncSocketModeHandler(slack_app, os.getenv("SLACK_APP_TOKEN"))

    slack_handler_task = asyncio.create_task(slack_handler.start_async())

    try:
        yield  # The app is running here
    finally:
        slack_handler_task.cancel()
        try:
            await slack_handler_task
        except asyncio.CancelledError:
            pass


# Init app
app = FastAPI(lifespan=lifespan)


class ProductModel(BaseModel):
    name: str
    price: float
    description: str


@app.get("/products", status_code=status.HTTP_200_OK, response_model=List[ProductModel])
async def get_products(price_range: str = None, limit: int = None):
    return await get_products_api(price_range, limit, say=True)


@slack_app.message(r"^query\s*-\s*(\d+)-(\d+)\s*-\s*(\d+)$")
async def query_data(message, say):
    text = message["text"]

    # Extract the range and number from the message using regex
    match = re.match(r"^query\s*-\s*(\d+)-(\d+)\s*-\s*(\d+)$", text)
    if match:
        range_start, range_end, limit = map(int, match.groups())
        price_range = f"{range_start}-{range_end}"

        try:
            # Call the get_products_api function with extracted parameters
            products = await get_products_api(price_range=price_range, limit=limit)

            # Construct a Slack message to display the result
            response = (
                f"Here are the top {limit} products in the price range {price_range}:\n"
            )
            for product in products:
                response += f"- {product['name']} (${product['price']}): {product['description']}\n\n"

            await say(response)
        except HTTPException as e:
            await say(f"Error fetching products: {e.detail}")
        except Exception as e:
            await say(f"An unexpected error occurred: {str(e)}")
    else:
        await say(
            "Invalid format. Please use `query - range (e.g., 100-200) - number (e.g., 5)`."
        )


def run_uvicorn():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    asyncio.run(run_uvicorn())
