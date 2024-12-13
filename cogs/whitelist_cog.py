import json
import nextcord
from nextcord.ext import commands
import csv
import os
import asyncio

class WalletWhitelistCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wallet_file = "tipwallets.json"
        self.role_id = None  # Role ID to be assigned
        self.admin_channel_id = None  # Admin channel ID to send the CSV file

    def save_wallet_data(self, user_id, user_name, wallet_address):
        if os.path.exists(self.wallet_file):
            with open(self.wallet_file, "r") as f:
                wallet_data = json.load(f)
        else:
            wallet_data = {}

        wallet_data[user_id] = {"user_name": user_name, "wallet_address": wallet_address}

        with open(self.wallet_file, "w") as f:
            json.dump(wallet_data, f, indent=4)

    @commands.command(name="setrole")
    @commands.has_permissions(administrator=True)
    async def set_role(self, ctx, role: nextcord.Role):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You do not have permission to use this command.")
            return

        self.role_id = role.id
        await ctx.send(f"Role {role.name} has been set for whitelisted users.")

    @commands.command(name="setadminchannel")
    @commands.has_permissions(administrator=True)
    async def set_admin_channel(self, ctx, channel: nextcord.TextChannel):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You do not have permission to use this command.")
            return

        self.admin_channel_id = channel.id
        await ctx.send(f"Admin channel {channel.name} has been set.")

    @commands.command(name="exportwallets")
    @commands.has_permissions(administrator=True)
    async def export_wallets(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You do not have permission to use this command.")
            return

        try:
            with open(self.wallet_file, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            await ctx.send("No wallet addresses found.")
            return

        csv_file = "wallet_addresses.csv"
        with open(csv_file, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Wallet Address"])
            for info in data.values():
                writer.writerow([info["wallet_address"]])

        if self.admin_channel_id:
            admin_channel = self.bot.get_channel(self.admin_channel_id)
            if admin_channel:
                await admin_channel.send(files=[nextcord.File(csv_file), nextcord.File(self.wallet_file)])
                await ctx.send("Wallet addresses have been exported and sent to the admin channel.")
            else:
                await ctx.send("Admin channel not found.")
        else:
            await ctx.send("Admin channel not set.")

        os.remove(csv_file)

    @commands.command(name="whitelist")
    async def whitelist(self, ctx, wallet_address: str):
        user_id = str(ctx.author.id)
        user_name = ctx.author.name

        self.save_wallet_data(user_id, user_name, wallet_address)

        if self.role_id:
            role = ctx.guild.get_role(self.role_id)
            if role:
                await ctx.author.add_roles(role)
                await ctx.send(f"Thanks, your wallet address has been recorded. You've been given the {role.name} role.")
            else:
                await ctx.send("Role not found. Please have an admin set the role again.")
        else:
            await ctx.send("Thanks, your wallet address has been recorded, but no role is set for assignment.")

        # Send a public viewable wink emoji
        await ctx.send("😉")

        # Delete the user's message
        await ctx.message.delete()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if self.bot.user.mentioned_in(message) and "a tip" in message.content.lower():
            prompt_message = await message.channel.send("Please provide your wallet address to whitelist.")
            
            def check(m):
                return m.author == message.author and m.channel == message.channel

            try:
                response = await self.bot.wait_for('message', check=check, timeout=60.0)
                await self.whitelist(await self.bot.get_context(response), response.content)
                try:
                    await response.delete()  # Delete the user's response
                    await prompt_message.delete()  # Delete the prompt message
                except nextcord.errors.NotFound:
                    pass  # Message was already deleted
            except asyncio.TimeoutError:
                await message.channel.send("You took too long to respond. Please try again.")
                await prompt_message.delete()  # Delete the prompt message if timeout occurs

def setup(bot):
    bot.add_cog(WalletWhitelistCog(bot))
