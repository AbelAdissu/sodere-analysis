# telegram_scraper.py
from telethon import TelegramClient
import config
import os
import json

# Create a client instance using the user's phone number
client = TelegramClient('user_session', config.api_id, config.api_hash)

# Ensure the directory for saving images exists
if not os.path.exists('movie_posters'):
    os.makedirs('movie_posters')

def extract_data(message_text):
    data = {}
    lines = message_text.split('\n')
    
    for line in lines:
        if "ᴛɪᴛᴛʟᴇ" in line:
            data['title'] = line.split(":")[1].strip()
        elif "ʀᴀᴛɪɴɢ" in line:
            data['rating'] = line.split(":")[1].strip()
        elif "ɢᴇɴʀᴇ" in line:
            data['genre'] = line.split(":")[1].strip()
        elif "ʀᴇʟᴇᴀsᴇ" in line:
            data['release'] = line.split(":")[1].strip()
        elif "ᴅᴜʀᴀᴛɪᴏɴ" in line:
            data['duration'] = line.split(":")[1].strip()
        elif "sʜᴏʀᴛ" in line:
            data['description'] = line.split(":")[1].strip()
        elif "ʟᴀɴɢᴜᴀɢᴇ" in line:
            data['language'] = line.split(":")[1].strip()
    
    return data

async def find_target_channel(client):
    message_id = 2190
    channel = 'Films_433'
    
    message = await client.get_messages(channel, ids=message_id)
    if message:
        print(f"Message content: {message.message}")
        # Extract URLs from message entities
        urls = [entity.url for entity in message.entities if hasattr(entity, 'url')]
        print(f"Extracted URLs: {urls}")
        # Manually return the relevant URL for Romance Movies (second URL in this case)
        if urls:
            return urls[1]  # Assume the second URL corresponds to "Romance Movies"
    return None

async def scrape_target_channel(client, target_channel_link):
    movies_data = []

    async for message in client.iter_messages(target_channel_link, limit=None):
        movie = {}
        if message.photo:
            # Check if the message contains relevant movie information
            if message.message and all(keyword in message.message for keyword in ["ᴛɪᴛᴛʟᴇ", "ʀᴀᴛɪɴɢ", "ɢᴇɴʀᴇ", "ʀᴇʟᴇᴀsᴇ", "ᴅᴜʀᴀᴛɪᴏɴ", "sʜᴏʀᴛ", "ʟᴀɴɢᴜᴀɢᴇ"]):
                # Download the photo
                photo_path = await message.download_media(file='movie_posters/')
                movie['cover'] = photo_path

                # Extract text information
                movie.update(extract_data(message.message))

                if movie:
                    movies_data.append(movie)

    # Save the scraped data to a JSON file
    with open('movies_data.json', 'w', encoding='utf-8') as f:
        json.dump(movies_data, f, ensure_ascii=False, indent=4)

async def main():
    # Connect to the client
    await client.start(config.phone_number)

    # Find the target channel link
    target_channel_link = await find_target_channel(client)
    if target_channel_link:
        print(f'Found target channel link: {target_channel_link}')
        # Scrape the target channel
        await scrape_target_channel(client, target_channel_link)
    else:
        print('Target channel link not found.')

# Start the client and run the event loop
with client:
    client.loop.run_until_complete(main())
