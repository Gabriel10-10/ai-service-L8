from typing import Any, List, Dict
from fastapi import APIRouter, Request, status
from fastapi.responses import Response, JSONResponse
import os
import httpx

# URL of the internal GPT service (in AKS)
GPT_SERVICE_URL = os.getenv("GPT_SERVICE_URL", "http://gpt-service/generate")
USE_AZURE_OPENAI = os.getenv("USE_AZURE_OPENAI", "True").lower() == "true"

# Define the description API router
description: APIRouter = APIRouter(prefix="/generate", tags=["generate"])


# Define the Product class
class Product:
    def __init__(self, product: Dict[str, List]) -> None:
        self.name: str = product["name"]
        self.tags: List[str] = product["tags"]


# Define the post_description endpoint
@description.post("/description", summary="Get description for a product", operation_id="getDescription")
async def post_description(request: Request) -> JSONResponse:
    try:
        # Parse the request body and create a Product object
        body: dict = await request.json()
        product: Product = Product(body)
        name: str = product.name
        tags: List[str] = ",".join(product.tags)

        # Build the prompt (same idea as before)
        prompt = (
            "Describe this pet store product using joyful, playful, and enticing language.\n"
            f"Product name: {name}\n"
            f"tags: {tags}\n"
            'description:"'
        )

        if USE_AZURE_OPENAI:
            # In this lab setup, we’re not using Azure OpenAI anymore
            return JSONResponse(
                content={"error": "Azure OpenAI path is disabled in this lab setup."},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Call the internal gpt-service (FastAPI service you deployed on AKS)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GPT_SERVICE_URL,
                json={"prompt": prompt, "max_tokens": 128},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()  # expected: { "text": "..." }

        result = data.get("text", "")

        # Optional cleanup similar to your original logic
        result = result.replace("\n", "").strip()

        # Return the description as a JSON response
        return JSONResponse(content={"description": result}, status_code=status.HTTP_200_OK)

    except Exception as e:
        # Return an error message as a JSON response
        return JSONResponse(content={"error": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
