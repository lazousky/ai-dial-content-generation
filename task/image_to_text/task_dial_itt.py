import asyncio
from io import BytesIO
from pathlib import Path

from task._models.custom_content import Attachment, CustomContent
from task._utils.constants import API_KEY, DIAL_URL, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role


async def _put_image() -> Attachment:
    file_name = 'dialx-banner.png'
    image_path = Path(__file__).parent.parent.parent / file_name
    mime_type_png = 'image/png'

    async with DialBucketClient(API_KEY, DIAL_URL) as client:
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()

        content = BytesIO(image_bytes)
        response = await client.put_file(file_name, mime_type_png, content)

        # Extract URL from response
        file_url = response.get("url")

        return Attachment(title=file_name, url=file_url, type=mime_type_png)


def start() -> None:
    # Create DialModelClient with GPT-4o model
    client = DialModelClient(DIAL_CHAT_COMPLETIONS_ENDPOINT, "gpt-4o", API_KEY)

    # Upload image to DIAL bucket
    attachment = asyncio.run(_put_image())
    print(f"Attachment uploaded: {attachment}\n")

    # Create message with attachment
    message = Message(
        role=Role.USER,
        content="What do you see on this picture?",
        custom_content=CustomContent(attachments=[attachment])
    )

    print("=== Analyzing image via DIAL bucket attachment ===")
    response = client.get_completion([message])
    print(f"Response: {response.content}")


start()
