import asyncio
from datetime import datetime
from pathlib import Path

from task._models.custom_content import Attachment
from task._utils.constants import API_KEY, DIAL_URL, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role

class Size:
    """
    The size of the generated image.
    """
    square: str = '1024x1024'
    height_rectangle: str = '1024x1792'
    width_rectangle: str = '1792x1024'


class Style:
    """
    The style of the generated image. Must be one of vivid or natural.
     - Vivid causes the model to lean towards generating hyper-real and dramatic images.
     - Natural causes the model to produce more natural, less hyper-real looking images.
    """
    natural: str = "natural"
    vivid: str = "vivid"


class Quality:
    """
    The quality of the image that will be generated.
     - ‘hd’ creates images with finer details and greater consistency across the image.
    """
    standard: str = "standard"
    hd: str = "hd"

async def _save_images(attachments: list[Attachment]):
    # Create DIAL bucket client
    async with DialBucketClient(API_KEY, DIAL_URL) as client:
        # Create output directory
        output_dir = Path("generated_images")
        output_dir.mkdir(exist_ok=True)

        # Download and save each image
        for attachment in attachments:
            if attachment.url:
                # Download image
                image_content = await client.get_file(attachment.url)

                # Create filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                extension = "png" if attachment.type == "image/png" else "jpg"
                filename = f"generated_{timestamp}.{extension}"
                filepath = output_dir / filename

                # Save image locally
                with open(filepath, "wb") as f:
                    f.write(image_content)

                print(f"✅ Image saved: {filepath}")


def start() -> None:
    # Test with DALL-E 3
    print("=== Generating image with DALL-E 3 ===\n")
    client = DialModelClient(DIAL_CHAT_COMPLETIONS_ENDPOINT, "dall-e-3", API_KEY)

    # Create message with text prompt
    message = Message(
        role=Role.USER,
        content="Sunny day on Bali"
    )

    # Configure image generation with custom_fields
    custom_fields = {
        "size": Size.square,
        "quality": Quality.hd,
        "style": Style.vivid
    }

    # Generate image
    response = client.get_completion([message], custom_fields=custom_fields)

    # Extract attachments and save images
    if response.custom_content and response.custom_content.attachments:
        print("\nSaving generated images...")
        asyncio.run(_save_images(response.custom_content.attachments))
    else:
        print("No images generated")

    # Test with Google image generation model
    print("\n=== Generating image with Google (imagegeneration@005) ===\n")
    google_client = DialModelClient(DIAL_CHAT_COMPLETIONS_ENDPOINT, "imagegeneration@005", API_KEY)

    message2 = Message(
        role=Role.USER,
        content="Sunny day on Bali"
    )

    # Configure with different settings
    custom_fields2 = {
        "size": Size.width_rectangle,
        "style": Style.natural
    }

    response2 = google_client.get_completion([message2], custom_fields=custom_fields2)

    if response2.custom_content and response2.custom_content.attachments:
        print("\nSaving generated images...")
        asyncio.run(_save_images(response2.custom_content.attachments))
    else:
        print("No images generated")


start()
