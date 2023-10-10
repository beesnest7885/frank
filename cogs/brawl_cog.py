import nextcord
from nextcord.ext import commands
import asyncio
import random

class BrawlCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    

    @commands.command(name='brawl')
    async def brawl(self, ctx):
        players = []

        

        # Inform players about the brawl and how to join
        embed = nextcord.Embed(title="Brawl!", description="A brawl is starting! React with 💪 to join within the next 20 seconds!", color=0xFF4500)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('💪')

        await asyncio.sleep(20)
        msg = await ctx.channel.fetch_message(msg.id)

        for reaction in msg.reactions:
            if reaction.emoji == '💪':
                async for user in reaction.users():
                    if user != self.bot.user:
                        players.append(user)

        if len(players) < 2:
            embed = nextcord.Embed(title="Brawl Result", description="Not enough players joined the brawl!", color=0xFF4500)
            await ctx.send(embed=embed)
            return

        # ... (your previous code)

        winner = random.choice(players)
        players.remove(winner)
        loser = random.choice(players)

        profile_cog = self.bot.get_cog('ProfileCog')
        winner_bonus = loser_bonus = 0

        # Check if winner has charm and apply bonus if they do
        if profile_cog and profile_cog.check_charm(winner.id):
            winner_bonus = 50
        
        # Check if loser has charm and apply bonus if they do
        if profile_cog and profile_cog.check_charm(loser.id):
            loser_bonus = 50

        # Set both players' health to 100 + any bonuses from charms
        winner_health = 100 + winner_bonus
        loser_health = 100 + loser_bonus

        xp_cog = self.bot.get_cog('XPCog')

        # ... (rest of your code)

        while winner_health > 0 and loser_health > 0:
            winner_damage = random.randint(5, 20)
            loser_damage = random.randint(5, 20)

            loser_health -= winner_damage
            winner_health -= loser_damage

            # Award XP to surviving participants
            if xp_cog:
                if winner_health > 0:
                    xp_cog.add_xp(winner.id, 3)  # Winner gets 3 XP for surviving the round
                if loser_health > 0:
                    xp_cog.add_xp(loser.id, 1)  # Loser gets 1 XP for surviving the round


            # Brawl update after each attack
            attack_descriptions = [
                f"{winner.display_name} delivers a crushing blow to {loser.display_name}, dealing {winner_damage} damage!",
                f"{loser.display_name} retaliates fiercely, inflicting {loser_damage} damage on {winner.display_name}!"
            ]
            embed = nextcord.Embed(title="Brawl Update", description="\n".join(attack_descriptions), color=0xFFFF00)
            await ctx.send(embed=embed)
            await asyncio.sleep(2)  # Short delay between updates for better pacing

        if winner_health <= 0:
            winner, loser = loser, winner

        if profile_cog:
            profile_cog.update_profile(winner.id, category='fights', action='win')
            profile_cog.update_profile(loser.id, category='fights', action='lose')


        # Award the winner additional XP for winning the brawl
        if xp_cog:
            xp_cog.add_xp(winner.id, 50)  # Winner gets an additional 50 XP for winning the brawl

        embed = nextcord.Embed(title="Brawl Result", description=f"{winner.mention} wins the brawl against {loser.mention}!", color=0x00FF00)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(BrawlCog(client))