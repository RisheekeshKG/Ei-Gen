import discord
import os
from dotenv import load_dotenv
import logging
from discord.ext import commands
import requests  # Import the requests library


load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

cmd_pre = "!"
bot = commands.Bot(command_prefix=cmd_pre, intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()  # Sync the commands with the Discord API
    print(f'We have logged in as {bot.user}')
    print(f'Commands: {bot.tree}')

async def on_message(message):
    if message.author == bot.user:
        return
    if message.content == cmd_pre + "hello":
        await message.reply("Hello !",mention_author = True)
    await bot.process_commands(message)  # Ensure commands are processed

async def on_member_join(member):
        guild = member.guild
        if guild.system_channel is not None:
            to_send = f'Welcome {member.mention} to {guild.name}!'
            await guild.system_channel.send(to_send)


@bot.command()
async def invite(ctx):
    embed = discord.Embed(
        title="Invite Ei-Gen To Your Server",
        url="https://discord.com/oauth2/authorize?client_id=1264103775103225886&scope=bot+applications.commands&permissions=8",
        description="Ei-Gen might require admin permission initially but in future it may or may not require the permission, Please Reconsider your decision as E-Gen Bot is still in its development stage. ",
        color=0xFFFFFF  # White color
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/1266015865262833684/1266018747722891317/Screenshot_from_2024-07-25_18-16-33.png?ex=66acd9d6&is=66ab8856&hm=0ffbdb6c5e886b260044d8f57bcc1a5c348bf3ff29f06df57df319c29cc059b1&")
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
