import base64
from pathlib import Path

from task._utils.constants import API_KEY, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.model_client import DialModelClient
from task._models.role import Role
from task.image_to_text.openai.message import ContentedMessage, TxtContent, ImgContent, ImgUrl


def start() -> None:
    project_root = Path(__file__).parent.parent.parent.parent
    image_path = project_root / "dialx-banner.png"

    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    # Create DialModelClient with GPT-4o model
    client = DialModelClient(DIAL_CHAT_COMPLETIONS_ENDPOINT, "gpt-4o", API_KEY)

    # Analyze with base64 encoded image
    base64_data_url = f"data:image/png;base64,{base64_image}"
    image_content = ImgContent(image_url=ImgUrl(url=base64_data_url))
    text_content = TxtContent(text="What do you see on this picture?")

    message = ContentedMessage(
        role=Role.USER,
        content=[text_content, image_content]
    )

    print("=== Analyzing with base64 encoded image ===")
    response = client.get_completion([message])
    print(f"Response: {response.content}\n")

    # Analyze with URL image
    url_image_content = ImgContent(image_url=ImgUrl(url="https://a-z-animals.com/media/2019/11/Elephant-male-1024x535.jpg"))
    message_url = ContentedMessage(
        role=Role.USER,
        content=[TxtContent(text="What do you see on this picture?"), url_image_content]
    )

    print("=== Analyzing with URL image ===")
    response_url = client.get_completion([message_url])
    print(f"Response: {response_url.content}")


start()