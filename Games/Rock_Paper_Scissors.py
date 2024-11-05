import random
import discord
from discord.ext import commands

rps_choices = ['rock', 'paper', 'scissors']

# Command for the RPS game
@commands.command(name='rps')
async def rps(ctx, user_choice: str):
    user_choice = user_choice.lower()

    if user_choice not in rps_choices:
        await ctx.send(f"Invalid choice! Please choose from 'rock', 'paper', or 'scissors'.")
        return

    bot_choice = random.choice(rps_choices)
    result, color = determine_winner(user_choice, bot_choice)

    embed = discord.Embed(
        title="Rock Paper Scissors Game",
        description=f"{ctx.author.mention} \n\n**{result}** \n\n ``Your Choice`` : {user_choice} \n ``Bot's Choice`` : {bot_choice}",
        color=color
    )
    await ctx.send(embed=embed)

# Helper function to determine the winner
def determine_winner(user_choice, bot_choice):
    if user_choice == bot_choice:
        return "It's a tie!", 0xFFFFFF
    elif (user_choice == 'rock' and bot_choice == 'scissors') or \
         (user_choice == 'paper' and bot_choice == 'rock') or \
         (user_choice == 'scissors' and bot_choice == 'paper'):
        return "You win!", 0x2ecc71
    else:
        return "Bot wins!", 0xe74c3c
