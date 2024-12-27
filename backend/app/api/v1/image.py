from fastapi import APIRouter, UploadFile, File
import httpx
from pydantic import BaseModel
from ...core.config import settings

router = APIRouter(tags=["images"])

class ImageUploadResponse(BaseModel):
    url: str
    
@router.post("/images/upload", status_code=200, response_model=ImageUploadResponse)
async def write_user(
    image: UploadFile = File(...)
):
    """
    Input:
    - image: an image file.
    
    
    
    Output:
    - url: the URL of the uploaded image.
    """
    # check if it is a valid image
    if not image.content_type.startswith("image/"):
        return {"error": "Invalid image type"}
    # send the image to imgbb
    # https://api.imgbb.com/1/upload?key=IMGBB_API_KEY
    # httpx
    response = httpx.post("https://api.imgbb.com/1/upload?key=" + settings.IMGBB_API_KEY, files={"image": (image.filename, image.file, image.content_type)})
    if response.status_code != 200:
        return {"error": "Failed to upload image"}
    image_url = response.json()["data"]["url"]
    return {"url": image_url}
