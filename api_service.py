from fastapi import HTTPException, status
from pydantic import BaseModel
from slack import slack_services
from typing import Dict
import httpx


class ProductModel(BaseModel):
    name: str
    price: float
    description: str


def convert_product(product: ProductModel, cheap=False) -> str:
    message = f"""
- Name: {product["name"]} \n\n
- Price: {product["price"]} \n\n
- Description: {product["description"]} \n
"""
    if cheap:
        message += "\n\n. This is the cheapest product within this price range"
    return message


async def get_products_service(price_range: str = None, limit: int = None, say=False):
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
                "description": product["description"],
            }
            for product in products
        ]

        # Optionally filter or limit results
        if price_range:
            min_price, max_price = map(float, price_range.split("-"))
            transformed_products = [
                product
                for product in transformed_products
                if min_price <= product["price"] <= max_price
            ]
        if limit:
            transformed_products = transformed_products[:limit]

        # get the product with the smallest price
        cheapest_product = min(
            transformed_products, key=lambda product: product["price"]
        )

        if say:
            product_message = convert_product(cheapest_product, cheap=True)
            await slack_services.send_slack_message(
                channel="D0843NDTRL6", text=product_message
            )
        return transformed_products

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
