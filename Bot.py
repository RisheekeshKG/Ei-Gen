import discord
import os
from dotenv import load_dotenv
import logging
from discord.ext import commands
from Games.Rock_Paper_Scissors import rps
from Generators.ImageGenerator import generate_image
from Generators.TextGenerator import get_ai_response

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

cmd_pre = "!"
bot = commands.Bot(command_prefix=cmd_pre, intents=intents)


bot.add_command(rps)
bot.add_command(generate_image)
bot.add_command(get_ai_response)

@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=f"Ei-Gen, type {cmd_pre}help"))
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content == cmd_pre + "hello":
        await message.reply("Hello !", mention_author=True)
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    embed = discord.Embed(
        title="Welcome to Ei-Gen Development Server",
        description="✨ Feel free to use the Ei-Gen bot and support us with your valuable feedback! \n 💬 Don't forget to follow the rules and policies when using the bot. ✅🚀",
        color=0xFFFFFF
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/1266015865262833684/1266018747722891317/Screenshot_from_2024-07-25_18-16-33.png")
    await member.send(embed=embed)
    role = discord.utils.get(member.guild.roles, name='Visitor')
    await member.add_roles(role)

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(
        title=f"Server Information - {guild.name}",
        color=0xFFFFFF
    )
    embed.add_field(name="ID", value=guild.id, inline=True)
    embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="Created At", value=guild.created_at.strftime("%d %b %Y %H:%M"), inline=True)
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    embed.add_field(name="Text Channels", value=len(guild.text_channels), inline=True)
    embed.add_field(name="Voice Channels", value=len(guild.voice_channels), inline=True)
    embed.set_thumbnail(url=guild.icon.url)
    await ctx.send(embed=embed)

@bot.command()
async def invite(ctx):
    embed = discord.Embed(
        title="Invite Ei-Gen To Your Server",
        url="https://discord.com/oauth2/authorize?client_id=1264103775103225886&scope=bot+applications.commands&permissions=8",
        description="Ei-Gen might require admin permission initially but in the future may or may not require the permission. Please reconsider your decision as the Ei-Gen Bot is still in development.",
        color=0xFFFFFF
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/1266015865262833684/1266018747722891317/Screenshot_from_2024-07-25_18-16-33.png")
    await ctx.send(embed=embed)

@bot.tree.command(name="status", description="This command verifies the status of bot")
async def status(interaction: discord.Interaction):
    await interaction.response.send_message(f"Bot is Online, Ping : {round(bot.latency*1000)} ms")

@bot.tree.command(name="about", description="This command shows the details of bot")
async def about(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Ei-Gen Bot",
        description="This bot is made by ___hyphen___ and void.jsx. It is still in Development. Only a few commands are available at the moment. Type !help for help.",
        color=0xFFFFFF
    )
    await interaction.response.send_message(embed=embed)



bot.run(os.getenv("DISCORD_TOKEN"), log_handler=handler)
