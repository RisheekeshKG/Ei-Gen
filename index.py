import discord
import os
from dotenv import load_dotenv
import logging
from discord.ext import commands
import requests  # Import the requests library

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

cmd_pre = "!"
bot = commands.Bot(command_prefix=cmd_pre, intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()  # Sync the commands with the Discord API
    print(f'We have logged in as {bot.user}')
    print(f'Commands: {bot.tree}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content == cmd_pre + "hello":
        await message.channel.send('Hello!')
    await bot.process_commands(message)  # Ensure commands are processed

@bot.command()
async def embed(ctx):
    embed = discord.Embed(
        title="Sample Embed",
        url="https://realdrewdata.medium.com/",
        description="This is an embed that will show how to build an embed and the different components",
        color=0xFFFFFF  # White color
    )
    await ctx.send(embed=embed)

@bot.tree.command(name="name", description="description")
async def slash_command(interaction: discord.Interaction):    
    await interaction.response.send_message("command")

# Image generation command
@bot.command()
async def generate_image(ctx, *, text: str):
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

        response = requests.post(api_url, headers=headers, json=data)
        if response.status_code == 200:
            image_url = response.json().get('generated_image')  # Assuming the API returns a URL to the generated image
            if image_url:
                await ctx.send(image_url)
            else:
                await ctx.send('Failed to retrieve the image URL from the API response.')
        else:
            await ctx.send(f'Failed to generate the image. API returned status code: {response.status_code}')
    except Exception as e:
        await ctx.send(f'An error occurred: {e}')

# Amazon data search command
@bot.command()
async def search_amazon(ctx, *, query: str):
    try:
        api_url = f'https://real-time-amazon-data.p.rapidapi.com/search?query={query}&page=1&country=US&sort_by=RELEVANCE&product_condition=ALL'
        headers = {
            'x-rapidapi-host': 'real-time-amazon-data.p.rapidapi.com',
            'x-rapidapi-key': os.getenv('AMAZON_KEY')  # Ensure your RapidAPI key is stored in the environment variable
        }

        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            products = data.get('data', {}).get('products', [])
            if products:
                results = '\n'.join([
                    f"Name: {product.get('product_title', 'N/A')}\nPrice: {product.get('product_price', 'N/A')}\nURL: {product.get('product_url', 'N/A')}"
                    for product in products[:5]  # Display the top 5 results
                ])
                await ctx.send(f"**Search Results:**\n{results}")
            else:
                await ctx.send('No products found for your query.')
        else:
            await ctx.send(f'Failed to fetch data. API returned status code: {response.status_code}')
    except Exception as e:
        await ctx.send(f'An error occurred: {e}')

bot.run(os.getenv("DISCORD_TOKEN"), log_handler=handler)
