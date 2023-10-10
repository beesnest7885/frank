import nextcord as discord
from nextcord.ext.commands import Cog, command
from nextcord.ext import commands
import json

class ShopCog(Cog):
    def __init__(self, client):
        self.client = client

        # Load the shop items from shop.json
        with open('shop.json', 'r') as f:
            self.shop_items = json.load(f)

    @command()
    async def shop(self, ctx):
        """Displays available items in the shop."""
        embed = discord.Embed(title="Shop", description="Available items for purchase:")
        for item, details in self.shop_items.items():
            embed.add_field(name=item, value=f"Cost: {details['price']} tokens, Quantity: {details['quantity']}", inline=False)
        await ctx.send(embed=embed)

    @command()
    async def buy(self, ctx, item: str):
        """Allows a user to buy an item from the shop."""
        
        profile_cog = self.client.get_cog('ProfileCog')
        user_data = profile_cog.get_user_data(ctx.author.id)

        if item in self.shop_items and self.shop_items[item]['quantity'] > 0:
            if user_data['tokens'] >= self.shop_items[item]['price']:
                self.shop_items[item]['quantity'] -= 1
                profile_cog.update_profile(ctx.author.id, tokens=-self.shop_items[item]['price'], item=item)
                if item == 'lucky_charm':  # If the item is a charm
                    profile_cog.add_charm_uses(ctx.author.id, 3)  # Add 3 uses to the charm when bought
                # Update shop.json with the new quantity
                with open('shop.json', 'w') as f:
                    json.dump(self.shop_items, f)
                await ctx.send(f"You bought a {item}!")
            else:
                await ctx.send(f"You don't have enough tokens to buy a {item}.")
        else:
            await ctx.send(f"{item} is not available in the shop.")

    @command()
    async def sell(self, ctx, item: str):
        """Allows a user to sell an item back to the shop."""
        profile_cog = self.client.get_cog('ProfileCog')

        if profile_cog.has_item(ctx.author.id, item):
            profile_cog.remove_item_from_inventory(ctx.author.id, item, int(self.shop_items[item]['price'] * 0.5))

            # Increase the quantity in the shop stock when sold back
            self.shop_items[item]['quantity'] += 1

            # Save the updated shop.json
            with open('shop.json', 'w') as f:
                json.dump(self.shop_items, f)

            await ctx.send(f"You sold your {item} for {self.shop_items[item]['price'] * 0.5} tokens.")
        else:
            await ctx.send(f"You don't have a {item} to sell.")


    @buy.error
    async def buy_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(f"Error: {error.original}")

def setup(client):
    client.add_cog(ShopCog(client))
