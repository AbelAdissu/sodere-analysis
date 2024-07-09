# telegram_scraper.py
from telethon import TelegramClient
import config
import os

# Create a client instance using the user's phone number
client = TelegramClient('user_session', config.api_id, config.api_hash)

async def main():
    # Connect to the client
    await client.start(config.phone_number)
    
    # Ensure the directory for saving images exists
    if not os.path.exists('images'):
        os.makedirs('images')

    # Fetch messages from the specific channel
    async for message in client.iter_messages('Soderefilmss', limit=None):
        if message.photo:
            # Download the photo
            await message.download_media(file='images/')

# Start the client and run the event loop
with client:
    client.loop.run_until_complete(main())
