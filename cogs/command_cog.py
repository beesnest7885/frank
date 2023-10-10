import nextcord
from nextcord.ext import commands
import random

class ComandCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def hello(self, ctx):
        await ctx.send("Hello the names Freight-train Frank im coach round here.Don't let the wrinkles fool you. I may be up there in age, but I promise you, it's not me who'll be gasping for air. The regimen I've laid out is no walk in the park many will fall by the wayside")

    @commands.command()
    async def info(self, ctx):
        embed = nextcord.Embed(title="Hobofc", description="A list of all available commands for the task frank can do for you.", color=0x00ff00)
        embed.add_field(name=".user", value="Shows your scores and inventory.", inline=False)
        embed.add_field(name=".race", value="Start a new hobo race. multiplayer fun. React to the message to join the race.", inline=False)
        embed.add_field(name=".challenge", value="Single player against bots - work in progress", inline=False)
        embed.add_field(name=".fight_leaderboard", value="race leaderboard.", inline=False)
        embed.add_field(name=".token_leaderboard", value="leaderboard of tokens.", inline=False)
        embed.add_field(name=".share", value="send sandwiches to your fellow hungry hobos '.share @user amount to send.'", inline=False)
        embed.add_field(name=".help", value="lists functions available, more coming.", inline=False)
        await ctx.send(embed=embed)

    

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            embed = nextcord.Embed(
                title="Error!",
                description="Unknown command. Use `.help, .info` for a list of commands.",
                color=0xff0000
            )
            await ctx.send(embed=embed)

    @commands.command(name='consume_charm')
    async def consume_charm(self, ctx):
        user_data = self.get_user_data(ctx.author.id)

        if not user_data or 'lucky_charm' not in user_data['inventory']:
            await ctx.send("You don't have any lucky charms in your inventory!")
            return

        user_data['inventory'].remove('lucky_charm')
        user_data['has_active_charm'] = True
        self.save_user_data(user_data)
        await ctx.send(f"{ctx.author.mention} consumed a lucky charm! They will have a bonus in the next event.")


    @commands.command()
    async def share(self, ctx, recipient: nextcord.Member, amount: int):
        """Tip a user some amount of your tokens."""
        giver_id = ctx.author.id  # IDs should be integers, not strings
        recipient_id = recipient.id

        profile_cog = self.client.get_cog('ProfileCog')
        
        if not profile_cog:
            embed = nextcord.Embed(title="Error", description="The profile system seems to be offline right now.", color=0xff0000)
            await ctx.send(embed=embed)
            return

        giver_data = profile_cog.get_user_data(giver_id)
        recipient_data = profile_cog.get_user_data(recipient_id)

        if not giver_data:
            await ctx.send("You don't have a profile set up.")
            return

        if giver_data["tokens"] < amount or amount <= 0:
            embed = nextcord.Embed(title="Insufficient Tokens", description="You don't have enough tokens to tip this amount!", color=0xff0000)
            await ctx.send(embed=embed)
            return

        # Deduct tokens from the giver
        giver_data["tokens"] -= amount

        # If the recipient does not have a profile, create one
        if not recipient_data:
            recipient_data = {
                "races_won": 0,
                "races_lost": 0,
                "challenges_won": 0,
                "challenges_lost": 0,
                "tokens": 0,
                "inventory": []
            }

        recipient_data["tokens"] += amount

        profile_cog.save_user_data(giver_data)
        profile_cog.save_user_data(recipient_data)

        embed = nextcord.Embed(title="Tip Successful", description=f"You've tipped {recipient.mention} {amount} tokens!", color=0x00ff00)
        await ctx.send(embed=embed)
        

    @commands.command()
    async def xp_leaders(self, ctx):
        """Show a leaderboard based on XP."""
        
        profile_cog = self.client.get_cog('ProfileCog')
        
        if not profile_cog:
            embed = nextcord.Embed(title="Error", description="The profile system seems to be offline right now.", color=0xff0000)
            await ctx.send(embed=embed)
            return

        # Fetch top 10 users based on XP. If you have a dedicated method for this in ProfileCog, use that. 
        # Otherwise, use the generic SQL approach (assuming you have a method for raw SQL execution):
        top_users = profile_cog.cursor.execute("SELECT user_id, xp FROM profiles ORDER BY xp DESC LIMIT 10").fetchall()

        embed = nextcord.Embed(title="XP Leaderboard", description="Top users based on XP:")
        for idx, (user_id, xp) in enumerate(top_users, 1):
            user = await self.client.fetch_user(int(user_id))
            embed.add_field(name=f"{idx}. {user.name}", value=f"{xp} XP", inline=False)
        
        await ctx.send(embed=embed)




def setup(client):
    print("Setting up ComandCog")  # For debug purposes
    client.add_cog(ComandCog(client))
