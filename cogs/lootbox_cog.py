import nextcord as discord
from nextcord.ext import commands
import json
import random

class LootboxCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    def load_lootboxes(self):
        with open('lootboxes.json', 'r') as f:
            return json.load(f)

    @commands.command()
    async def open_lootbox(self, ctx, lootbox_type: str):
        """Allows a user to open a specific type of lootbox."""
        
        profile_cog = self.client.get_cog("ProfileCog")
        lootboxes = self.load_lootboxes()
        
        if lootbox_type not in lootboxes:
            await ctx.send(f"There's no lootbox named {lootbox_type}.")
            return

        if not profile_cog.has_item(ctx.author.id, lootbox_type):
            await ctx.send(f"You don't have a {lootbox_type}.")
            return

        lootbox = lootboxes[lootbox_type]
        rewards = lootbox["rewards"]

        # Giving out the tokens
        tokens = random.randint(rewards["tokens"]["min"], rewards["tokens"]["max"])
        profile_cog.update_profile(ctx.author.id, tokens=tokens)

        # Determining which item is won, if any
        won_item = None
        random_val = random.random()
        for item in rewards["items"]:
            if random_val <= item["probability"]:
                won_item = item["name"]
                break
            random_val -= item["probability"]
        
        if won_item:
            profile_cog.add_item_to_inventory(ctx.author.id, won_item)
            await ctx.send(f"You opened a {lootbox_type} and received {tokens} tokens and a {won_item}!")
        else:
            await ctx.send(f"You opened a {lootbox_type} and received {tokens} tokens!")

        # Removing the used lootbox
        profile_cog.remove_item_from_inventory(ctx.author.id, lootbox_type)

    @commands.command()
    async def lootbox_info(self, ctx, lootbox_type: str):
        """Displays information about a specific type of lootbox."""
        
        lootboxes = self.load_lootboxes()
        
        if lootbox_type not in lootboxes:
            await ctx.send(f"There's no lootbox named {lootbox_type}.")
            return

        lootbox = lootboxes[lootbox_type]
        embed = discord.Embed(title=lootbox_type, description=lootbox["description"], color=0x00ff00)
        
        token_range = f"{lootbox['rewards']['tokens']['min']} to {lootbox['rewards']['tokens']['max']}"
        embed.add_field(name="Tokens", value=token_range, inline=False)
        
        for item in lootbox["rewards"]["items"]:
            embed.add_field(name=item["name"], value=f"Probability: {item['probability']*100:.2f}%", inline=False)
        
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(LootboxCog(client))
