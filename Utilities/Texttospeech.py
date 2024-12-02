from discord.ext import commands
from gtts import gTTS
import discord
import os
import tempfile

@commands.command(name='tos')
async def text_to_speech(ctx, *, text: str):
    try:
       
        safe_author_name = "".join(char for char in ctx.author.name if char.isalnum() or char in "-_")
        temp_dir = tempfile.gettempdir() 
        filename = os.path.join(temp_dir, f"{safe_author_name}_output.mp3")

       
        tts = gTTS(text=text, lang='en')
        tts.save(filename)

        
        await ctx.send(f"Here's your TTS audio, {ctx.author.mention}:", file=discord.File(filename))

        
        os.remove(filename)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")