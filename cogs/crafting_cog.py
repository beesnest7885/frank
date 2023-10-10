import nextcord as discord
from nextcord.ext import commands
import json

class CraftingCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        with open('crafting.json', 'r') as f:
            self.recipes = json.load(f)

    @commands.command()
    async def craft(self, ctx, item: str):
        """Allows a user to craft an item if they have enough resources."""
        
        profile_cog = self.client.get_cog("ProfileCog")
        user_data = profile_cog.get_user_data(ctx.author.id)

        if not item in self.recipes:
            await ctx.send(f"{item} is not a craftable item.")
            return

        recipe = self.recipes[item]

        for required_item, amount in recipe["cost"].items():
            if required_item == "tokens":
                if user_data["tokens"] < amount:
                    await ctx.send(f"You don't have enough tokens to craft {item}.")
                    return
            else:
                if not profile_cog.has_item(ctx.author.id, required_item, amount):
                    await ctx.send(f"You don't have enough {required_item}(s) to craft {item}.")
                    return

        # Deduct resources and craft the item
        for required_item, amount in recipe["cost"].items():
            if required_item == "tokens":
                profile_cog.update_profile(ctx.author.id, tokens=-amount)
            else:
                profile_cog.remove_item_from_inventory(ctx.author.id, required_item, amount)

        profile_cog.add_item_to_inventory(ctx.author.id, item)

        await ctx.send(f"Successfully crafted {item}!")

    @commands.command()
    async def crafting_recipes(self, ctx):
        """Displays available crafting recipes."""
        
        embed = discord.Embed(title="Crafting Recipes", description="Here are the available crafting recipes:")
        
        for item, recipe in self.recipes.items():
            cost = ', '.join(f"{amount} {required_item}" for required_item, amount in recipe["cost"].items())
            embed.add_field(name=item, value=f"Cost: {cost}\n{recipe['description']}", inline=False)
        
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(CraftingCog(client))
