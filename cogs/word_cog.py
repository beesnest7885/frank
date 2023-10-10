import nextcord as discord
from nextcord.ext import commands, tasks
import random

class WordCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.post_word_channel_id = None  # ID of the channel to post the challenge
        self.current_word = None  # Current challenge word
        self.hobo_words = ["word1", "word2", "word3", "..."]  # Fill with your hobo words
        self.word_task.start()  # Start the task when the cog is loaded

    def cog_unload(self):
        self.word_task.cancel()  # Stop the task when the cog is unloaded

    @tasks.loop(hours=5)
    async def word_task(self):
        if self.post_word_channel_id:
            channel = self.client.get_channel(self.post_word_channel_id)
            if channel:
                self.current_word = random.choice(self.hobo_words)
                embed = discord.Embed(title="Word Challenge", description="First one to reply with one of the hobo words wins!")
                await channel.send(embed=embed)

    @word_task.before_loop
    async def before_word_task(self):
        await self.client.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == self.post_word_channel_id and message.content == self.current_word:
            profile_cog = self.client.get_cog("ProfileCog")
            if profile_cog:
                profile_cog.add_rewards_to_user(message.author.id, xp=50, tokens=50, lootbox=1)
                await message.channel.send(f"Congratulations {message.author.mention}! You've won the challenge!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_word_channel(self, ctx, channel: discord.TextChannel):
        self.post_word_channel_id = channel.id
        await ctx.send(f"Word challenge channel set to {channel.mention}")

def setup(client):
    client.add_cog(WordCog(client))
