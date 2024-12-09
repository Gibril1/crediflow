from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from typing import List
from slack_service import slack_services
import httpx

# Init app
app = FastAPI()

class ProductModel(BaseModel):
    name: str
    price: float
    description: str

@app.get('/products', status_code=status.HTTP_200_OK, response_model=List[ProductModel])
async def get_products(price_range:str = None,  limit: int = None):
    try:
        # Create an instance of AsyncClient
        async with httpx.AsyncClient() as client:
            response = await client.get("https://fakestoreapi.com/products")
            response.raise_for_status()  

        # Deserialize the response JSON
        products = response.json()

        # Transform the API response to match ProductModel
        transformed_products = [
            {
                "name": product["title"], 
                "price": product["price"],
                "description": product["description"]
            }
            for product in products
        ]

        # Optionally filter or limit results
        if price_range:
            min_price, max_price = map(float, price_range.split('-'))
            transformed_products = [
                product for product in transformed_products
                if min_price <= product["price"] <= max_price
            ]
        if limit:
            transformed_products = transformed_products[:limit]

        # get the product with the smallest price
        cheapest_product = min(transformed_products, key=lambda product: product["price"])

        print(cheapest_product)
        return transformed_products

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@app.get('/slack_users', status_code=status.HTTP_200_OK)
async def get_slack_users():
    return await slack_services.get_all_slack_users()

@app.get('/send_message', status_code=status.HTTP_200_OK)
async def send_message(channel_id: str, text: str):
    return await slack_services.send_slack_message(channel_id, text)
