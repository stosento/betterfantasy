import httpx
from utils.logger import setup_logging

logger = setup_logging()

async def send_message_to_webhook(webhook_url, message):
    async with httpx.AsyncClient() as client:
        payload = {
            "content": message
        }
        response = await client.post(webhook_url, json=payload)
        if response.status_code == 204:
            logger.info("Message sent to webhook successfully")
        else:
            logger.error(f"Failed to send message to webhook. Status code - {response.status_code}")