import os
import requests
import discord
from discord.ext import commands

# Command to generate an image based on text
@commands.command(name="generate")
async def generate_image(ctx, *, text: str):
    loading_message = await ctx.send("🔄 Generating your image, please wait...")  # Send a loading message

    try:
        api_url = 'https://chatgpt-42.p.rapidapi.com/texttoimage'
        headers = {
            'Content-Type': 'application/json',
            'x-rapidapi-host': 'chatgpt-42.p.rapidapi.com',
            'x-rapidapi-key': os.getenv('IMAGE_KEY')  # Ensure your RapidAPI key is stored in the environment variable
        }
        data = {
            "text": text,
            "width": 512,
            "height": 512
        }

        # Make the request to the image generation API
        response = requests.post(api_url, headers=headers, json=data)
        
        if response.status_code == 200:
            image_url = response.json().get('generated_image')  # Assuming the API returns a URL to the generated image
            if image_url:
                await loading_message.edit(content="Here is your generated image:")
                await ctx.send(image_url)
            else:
                await loading_message.edit(content="Failed to retrieve the image URL from the API response.")
        else:
            await loading_message.edit(content=f"Failed to generate the image. API returned status code: {response.status_code}")
    except Exception as e:
        await loading_message.edit(content=f"An error occurred: {e}")
