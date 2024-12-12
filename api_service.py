from fastapi import HTTPException, status
from pydantic import BaseModel
from slack import slack_services
from typing import Optional
import httpx
import traceback




class RatingModel(BaseModel):
    rate: float
    count: int

class ProductModel(BaseModel):
    name: str
    price: float
    description: str
    rating: RatingModel

class FilterModel(BaseModel):
    rating_number: Optional[int] = 1
    sort: Optional[bool] = False
    limit: Optional[int] = 1
    price_range: Optional[str] = "100-200"




def convert_product(product: ProductModel, cheap=False) -> str:
    message = f"""
- Name: {product["name"]} \n\n
- Price: {product["price"]} \n\n
- Description: {product["description"]} \n
"""
    if cheap:
        message += "\n\n. This is the cheapest product within this price range"
    return message


async def get_products_service(filter_params: FilterModel, say = None):
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
                "rating": product["rating"]
            }
            for product in products
        ]

        # Optionally filter or limit results
        if filter_params.price_range:
            min_price, max_price = map(float, filter_params.price_range.split("-"))
            transformed_products = [
                product
                for product in transformed_products
                if min_price <= product["price"] <= max_price
            ]

        if filter_params.limit:
            transformed_products = transformed_products[:filter_params.limit]

        

        rated_products = sorted(transformed_products, key= lambda product: product["rating"]["rate"], reverse=filter_params.sort)[:filter_params.rating_number]
        

        # get the product with the smallest price
        cheapest_product = min(
            transformed_products, key=lambda product: product["price"]
        )

        if say:
            product_message = convert_product(cheapest_product, cheap=True)
            await slack_services.send_slack_message(
                channel="D0843NDTRL6", text=product_message
            )
        return rated_products

    except httpx.HTTPStatusError as e:
        print(traceback.format_exc())
        print(e)
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    



