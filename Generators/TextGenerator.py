import os
from discord.ext import commands
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import asyncio

load_dotenv()


api_key = os.getenv("GOOGLE_API_KEY")


llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    api_key=api_key,
    temperature=0.4,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

@commands.command(name="ask")
async def get_ai_response(ctx, *, user_message: str):
    message = await ctx.send("🔄 Generating Response, please wait...")
  
    messages = [
        (
            "system",
            "You are a helpful assistant  integrated as a Discord bot namely Eigen who is developed by Risheekesh. Help the user according to their needs and use Markdown language , Respond in 4 lines",
        ),
        ("human", user_message),
    ]
    try:
        # Run synchronous function in thread pool
        ai_msg = await asyncio.to_thread(llm.invoke, messages)

        if ai_msg.content:
            await message.edit(content=ai_msg.content)
        else:
            await message.edit(content="Failed to generate a response.")
    except Exception as e:
        await message.edit(content=f"An error occurred: {e}")





