from loguru import logger
from openai import OpenAI


def generate_image(word):
    client = OpenAI()
    response = client.images.generate(
        model="dall-e-2",
        prompt=word,
        size="1024x1024",
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url
    return image_url
