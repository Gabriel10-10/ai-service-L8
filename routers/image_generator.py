from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from typing import Any, List, Dict
import os
import httpx  # Use httpx for async HTTP calls

# URL of the internal DALL-E service (running in AKS)
DALLE_SERVICE_URL = os.getenv("DALLE_SERVICE_URL", "http://dalle-service/generate-image")
USE_AZURE_OPENAI = os.getenv("USE_AZURE_OPENAI", "True").lower() == "true"

# Define the image API router
image: APIRouter = APIRouter(prefix="/generate", tags=["generate"])


# Define the Product class
class Product:
    def __init__(self, product: Dict[str, List]) -> None:
        self.name: str = product["name"]
        self.description: List[str] = product["description"]


# Define the post_image endpoint
@image.post("/image", summary="Get image for a product", operation_id="getImage")
async def post_image(request: Request) -> JSONResponse:
    try:
        # Parse the request body and create a Product object
        body: dict = await request.json()
        product: Product = Product(body)
        name: str = product.name
        description: List[str] = product.description

        if USE_AZURE_OPENAI:
            # In this lab, we are not using Azure OpenAI anymore
            return JSONResponse(
                content={"error": "Azure OpenAI path is disabled in this lab setup."},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        print("Calling internal dalle-service")

        # Build the prompt similar to the original one
        prompt = (
            "Generate a cute photo realistic image of a product in its packaging in front "
            "of a plain background for a product called "
            f"<{name}> with a description <{description}> to be sold in an online pet supply store"
        )

        # Call the internal dalle-service (FastAPI service on AKS)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                DALLE_SERVICE_URL,
                json={
                    "prompt": prompt,
                    "n": 1,
                    "size": "512x512",
                },
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()  # expected: { "urls": ["..."] }

        image_url = data["urls"][0]

        # Return the image as a JSON response (same key as before: "image")
        return JSONResponse(
            content={"image": image_url},
            status_code=status.HTTP_200_OK,
        )

    except Exception as e:
        # Return an error message as a JSON response
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
