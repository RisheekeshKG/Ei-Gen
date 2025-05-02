import discord
from discord.ext import commands
from nltk.sentiment import SentimentIntensityAnalyzer
import io
import matplotlib.pyplot as plt

class SentimentModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sia = SentimentIntensityAnalyzer()
        self.blacklist = {}
        self.warnings = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or not message.guild:
            return

        content = message.content.lower()

        # Check if the message contains any bad words
        if any(bad_word in content for bad_word in self.blacklist):
            sentiment = self.sia.polarity_scores(content)
            
            # If the message has negative sentiment or contains a bad word
            if sentiment['compound'] < -0.5:
                await message.delete()
                await message.channel.send(f"⚠️ Message from {message.author.name} deleted due to offensive language.")
                await self.handle_warning(message, is_severe=True)
            else:
                await self.handle_warning(message, is_severe=False)

    async def handle_warning(self, message, is_severe):
        user = message.author
        if is_severe:
            # Severe messages trigger immediate deletion and punishment
            await message.channel.send(f"⚠️ {user.mention}, your message was deleted due to offensive language.")
            if user not in self.warnings:
                self.warnings[user] = 1
            else:
                self.warnings[user] += 1
            if self.warnings[user] >= 3:
                await message.author.add_roles(discord.utils.get(message.guild.roles, name="Muted"))
                await message.channel.send(f"{user.mention} has been muted for repeated offenses.")
        else:
            # Less severe messages just trigger a warning
            if user not in self.warnings:
                self.warnings[user] = 1
                await message.channel.send(f"⚠️ {user.mention}, please refrain from using inappropriate language.")
            else:
                self.warnings[user] += 1

            if self.warnings[user] >= 3:
                await message.author.add_roles(discord.utils.get(message.guild.roles, name="Muted"))
                await message.channel.send(f"{user.mention} has been muted for repeated offenses.")

    @commands.command(name="emotions")
    async def emotions(self, ctx):
        await ctx.defer()

        negative, blacklist_hits, both, clean = 0, 0, 0, 0
        flagged = []

        try:
            async for msg in ctx.channel.history(limit=30):
                if msg.author.bot:
                    continue
                content = msg.content.lower()
                is_blacklist = any(word in content for word in self.blacklist)
                sentiment = self.sia.polarity_scores(content)
                is_negative = sentiment['compound'] < -0.5

                if is_negative and is_blacklist:
                    both += 1
                    flagged.append(f"❌ Both | {msg.author.name}: {msg.content}")
                elif is_negative:
                    negative += 1
                    flagged.append(f"😠 Negative | {msg.author.name}: {msg.content}")
                elif is_blacklist:
                    blacklist_hits += 1
                    flagged.append(f"🚫 Blacklist | {msg.author.name}: {msg.content}")
                else:
                    clean += 1
        except Exception as e:
            await ctx.send(f"An error occurred while processing messages: {e}")
            return

        labels = ['Negative', 'Blacklist', 'Both', 'Clean']
        values = [negative, blacklist_hits, both, clean]
        fig, ax = plt.subplots()
        ax.bar(labels, values, color=['orange', 'red', 'purple', 'green'])
        ax.set_ylabel('Number of Messages')
        ax.set_title('Chat Emotion Summary (Last 30 Messages)')
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
