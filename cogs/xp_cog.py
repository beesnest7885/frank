from nextcord.ext import commands

class XPCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channels_for_xp = [1006296186828902421, 1094393858047099001]  # Replace these with the IDs of channels you want
        self.xp_per_message = 1  # The amount of XP you want to give for each message

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from bots
        if message.author.bot:
            return

        # Check if the message is in one of the designated channels
        if message.channel.id in self.channels_for_xp:
            self.add_xp(message.author.id, self.xp_per_message)

    def add_xp(self, user_id: int, amount: int):
        """Add XP to a user."""
        profile_cog = self.bot.get_cog('ProfileCog')
        if profile_cog:
            profile_cog.add_xp(user_id, amount)

    def update_rank(self, user_id: int):
        """Update the rank of a user based on their XP."""
        profile_cog = self.bot.get_cog('ProfileCog')
        if profile_cog:
            profile_cog.update_rank(user_id)

def setup(client):
    client.add_cog(XPCog(client))
