from fastapi import FastAPI, status, HTTPException
import uvicorn
from typing import List, Optional
from api_service import get_products_service, convert_product, ProductModel, FilterModel
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
import asyncio
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
import re
from mongodb import check_db_connection, close_database_connection,query_collection
import logging

load_dotenv()

logger = logging.getLogger(__name__)


# Initializes your app with your bot token and socket mode handler
slack_app = AsyncApp(token=os.getenv("SLACK_BOT_TOKEN"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongodb = await check_db_connection()
    if not mongodb:
        import logging

        logging.error("MongoDB connection failed. Exiting the app.")
        import sys

        sys.exit(1)
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

        await close_database_connection()


# Init app
app = FastAPI(lifespan=lifespan)

@app.get('/', status_code=status.HTTP_200_OK)
def root():
    return {
        "status": True,
        "message": "Crediflow Technical Assesment"
    }

@app.get("/products", status_code=status.HTTP_200_OK, response_model=List[ProductModel])
async def get_products(price_range: str = None, limit: int = None):
    filter_model = FilterModel(price_range=price_range, limit=limit)
    return await get_products_service(filter_model, say=True)

@app.get("/rated_products", status_code=status.HTTP_200_OK, response_model=List[ProductModel])
async def get_top_rated_products(price_range: str = None, limit: int = None, rating_number:int = None):
    filter_model = FilterModel(price_range=price_range, limit=limit, rating_number=rating_number)
    return await get_products_service(filter_model, say=True)


@slack_app.message(r"^query\s*-\s*(\d+)-(\d+)\s*-\s*(\d+)$")
async def query_data(message, say):
    text = message["text"]
    user = message["user"]

    # Extract the range and number from the message using regex
    match = re.match(r"^query\s*-\s*(\d+)-(\d+)\s*-\s*(\d+)$", text)
    if match:
        range_start, range_end, limit = map(int, match.groups())
        price_range = f"{range_start}-{range_end}"

        try:
            # Call the get_products_api function with extracted parameters
            products = await get_products_service(price_range=price_range, limit=limit)

            # Construct a Slack message to display the result
            response = (
                f"Here are the top {limit} products in the price range {price_range}:\n"
            )
            for product in products:
                response += convert_product(product) + "\n\n"
            # add the queries to the database
            query = {"user": user, "query": text}
            await query_collection.create_item(query)
            logger.info("Query has been persisted in the database")
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
