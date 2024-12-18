from motor.motor_asyncio import AsyncIOMotorClient
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


DATABASE_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")


class Database:
    client: AsyncIOMotorClient = None


db = Database()


async def get_database():
    if db.client is None:
        db.client = AsyncIOMotorClient(DATABASE_URL)
    return db.client[DATABASE_NAME]


async def close_database_connection():
    if db.client is not None:
        db.client.close()
        logger.info("MongoDB connection has closed")


async def check_db_connection():
    try:
        client = AsyncIOMotorClient(DATABASE_URL)
        await client.admin.command("ping")

        # Get the list of available collections in the database
        database = client[DATABASE_NAME]
        collection_names = await database.list_collection_names()

        logger.info("Logging collection names")
        for collection_name in collection_names:
            logger.info(collection_name)

        return True
    except Exception as e:
        logger.error(f"Error connecting to the database: {e}")
        return False


class MongoDBCRUDService:
    def __init__(self, model):
        self.model = model
        self.database = get_database()

    async def create_item(self, item: dict):
        try:
            db = await get_database()
            result = await db[self.model].insert_one(item)
            item_id = result.inserted_id
            # Convert the ObjectId to a string
            item_id_str = str(item_id)
            saved_item = await db[self.model].find_one({"_id": item_id}, {"_id": 0})
            return {**saved_item, "id": item_id_str}  # Include the item_id as a string
        except Exception as e:
            logging.error(f"Error creating item: {str(e)}")
            return None


query_collection = MongoDBCRUDService("query")
