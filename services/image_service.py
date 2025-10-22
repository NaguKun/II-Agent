import base64
import io
from typing import Optional, Tuple
from PIL import Image
from config import settings


class ImageService:
    """Service for handling image uploads and processing"""

    @staticmethod
    def validate_image(image_data: str) -> Tuple[bool, Optional[str]]:
        """
        Validate base64 encoded image data
        Returns (is_valid, error_message)
        """
        try:
            # Check if it's a data URL and extract the base64 part
            if image_data.startswith('data:image'):
                header, encoded = image_data.split(',', 1)
                image_type = header.split(';')[0].split(':')[1]
            else:
                encoded = image_data
                image_type = None

            # Decode base64
            image_bytes = base64.b64decode(encoded)

            # Check file size
            max_size = settings.max_file_size_mb * 1024 * 1024
            if len(image_bytes) > max_size:
                return False, f"Image size exceeds {settings.max_file_size_mb}MB limit"

            # Validate with PIL
            image = Image.open(io.BytesIO(image_bytes))
            image.verify()

            # Check image type if provided
            if image_type:
                allowed_types = settings.allowed_image_types.split(',')
                if image_type not in allowed_types:
                    return False, f"Image type {image_type} not allowed"

            return True, None

        except Exception as e:
            return False, f"Invalid image data: {str(e)}"

    @staticmethod
    def get_image_info(image_data: str) -> dict:
        """Get information about the image"""
        try:
            if image_data.startswith('data:image'):
                _, encoded = image_data.split(',', 1)
            else:
                encoded = image_data

            image_bytes = base64.b64decode(encoded)
            image = Image.open(io.BytesIO(image_bytes))

            return {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode,
                "size_bytes": len(image_bytes)
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def prepare_image_for_api(image_data: str) -> str:
        """
        Prepare image data for Claude API
        Ensures it's in the correct format
        """
        if image_data.startswith('data:image'):
            return image_data

        # If it's raw base64, add the data URL prefix
        # Assume JPEG if format not specified
        return f"data:image/jpeg;base64,{image_data}"
