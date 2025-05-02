import discord
from discord.ext import commands
from nltk.sentiment import SentimentIntensityAnalyzer
import io
import matplotlib.pyplot as plt
import asyncio
import random

class SentimentModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sia = SentimentIntensityAnalyzer()
        self.blacklist = {'idiot', 'dogwater', 'stupid'}
        self.warnings = {}
        self.flagged_messages = []

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or not message.guild:
            return

        content = message.content.lower()
        sentiment = self.sia.polarity_scores(content)
        is_blacklisted = any(bad_word in content for bad_word in self.blacklist)
        is_negative = sentiment['compound'] < -0.5

        if is_blacklisted or is_negative:
            self.flagged_messages.append((message.author, message.content, is_blacklisted, is_negative))
            await message.delete()
            await message.channel.send(f"⚠️ Message from {message.author.name} deleted for violating community guidelines.")
            await self.handle_warning(message, severe=is_negative)

        if len(self.flagged_messages) > 30:
            self.flagged_messages.pop(0)

    async def handle_warning(self, message, severe=False):
        user = message.author
        guild = message.guild
        mute_role = discord.utils.get(guild.roles, name="Timeout")
        mod_roles = [role for role in guild.roles if role.name.lower() == "moderator"]
        mod = random.choice(mod_roles) if mod_roles else None

        if user in self.warnings:
            self.warnings[user] += 1
            if self.warnings[user] >= 5:
                if mute_role:
                    await user.add_roles(mute_role)
                    await message.channel.send(f"{mod.mention if mod else ''} {user.name} has been muted temporarily for repeated offenses.")
                    await asyncio.sleep(30)
                    await user.remove_roles(mute_role)
                del self.warnings[user]
            else:
                remaining = 5 - self.warnings[user]
                await message.channel.send(f"⚠️ {user.mention}, you have {remaining} warning{'s' if remaining > 1 else ''} remaining.")
        else:
            self.warnings[user] = 1
            await message.channel.send(f"⚠️ {user.mention}, this is your first warning. You have 4 warnings remaining.")

    @commands.command(name="emotions")
    async def emotions(self, ctx):
        negative, blacklist_hits, clean = 0, 0, 0
        flagged = []

        # Analyze deleted messages
        for author, content, is_blacklist, is_negative in self.flagged_messages:
            if is_blacklist:
                blacklist_hits += 1
                flagged.append(f"🚫 Blacklist | {author.name}: {content}")
            elif is_negative:
                negative += 1
                flagged.append(f"😠 Negative | {author.name}: {content}")
            else:
                clean += 1

        # Analyze recent visible messages
        try:
            async for msg in ctx.channel.history(limit=30):
                if msg.author.bot:
                    continue
                content = msg.content.lower()
                is_blacklist = any(word in content for word in self.blacklist)
                sentiment = self.sia.polarity_scores(content)
                is_negative = sentiment['compound'] < -0.5

                if is_blacklist:
                    blacklist_hits += 1
                    flagged.append(f"🚫 Blacklist | {msg.author.name}: {msg.content}")
                elif is_negative:
                    negative += 1
                    flagged.append(f"😠 Negative | {msg.author.name}: {msg.content}")
                else:
                    clean += 1
        except Exception as e:
            await ctx.send(f"An error occurred while processing messages: {e}")
            return

        # Plotting
        labels = ['Negative', 'Blacklist', 'Clean']
        values = [negative, blacklist_hits, clean]
        fig, ax = plt.subplots()
        ax.bar(labels, values, color=['orange', 'red', 'green'])
        ax.set_ylabel('Number of Messages')
        ax.set_title('Chat Emotion Summary (Recent Messages)')
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        file = discord.File(buf, filename="chat_emotion.png")
        embed = discord.Embed(
            title="🔍 Chat Emotion Analysis",
            description="Flagged messages:\n" + "\n".join(flagged[:5]) if flagged else "✅ All messages are clean.",
            color=0xFF0000 if flagged else 0x00FF00
        )
        embed.set_image(url="attachment://chat_emotion.png")
        await ctx.send(embed=embed, file=file)

async def setup(bot):
    await bot.add_cog(SentimentModeration(bot))
