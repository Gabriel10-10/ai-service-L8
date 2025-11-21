from fastapi import FastAPI, status
from routers.description_generator import description
from routers.image_generator import image
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

app = FastAPI(version=os.environ.get("APP_VERSION", "0.1.0"))

# Register routers
app.include_router(description)
app.include_router(image)

# Allow CORS for all origins (same as before)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/health", summary="check if server is healthy", operation_id="health")
async def get_health():
    """
    Health check endpoint.
    Since Azure OpenAI is no longer used, this service
    always supports both description and image generation.
    """
    capabilities = ["description", "image"]

    print("Generative AI capabilities: ", ", ".join(capabilities))
    return JSONResponse(
        content={"status": "ok", "version": app.version, "capabilities": capabilities},
        status_code=status.HTTP_200_OK
    )
