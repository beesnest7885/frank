import nextcord
from nextcord.ext import commands
import asyncio
import random

class RaceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='race')
    async def race(self, ctx):
        hobo_names = ["Boxcar Benny", "Tumbleweed Tina", "Switchyard Sam", "Junkyard Jill", "Railroader Randy", "Hobo Harry", "Rucksack Rosie", "Nomad Nancy", "Freight-train Fred", "Drifter Dave"
        ]
        bad_events = ["Caught by the trainyard security", "Tripped over loose rail ties", "Lost your map and took a wrong turn", "Backpack strap broke, spilling essentials", "Hitchhiked on a train going the wrong direction", "Caught in a makeshift trap set by rivals", "Bitten by a stray dog guarding a shortcut", "Caught a 'bad ticket' (caught a disease)", "Ran afoul of a hostile vagrant", "Sleeping bag taken by gang members"
        ]
        good_events = ["Found a stash of food and water", "Caught a fast train going in the right direction", "Received useful gear from a sympathetic rail worker", "Discovered a shortcut through an abandoned tunnel", "Met a friendly stray dog that helped guide the way", "Found a hidden cache of first-aid supplies", "Stumbled upon an old, working bicycle", "Encountered a kind stranger who gave accurate directions", "Found a functioning GPS device among discarded items", "Got a tip about a police checkpoint and successfully avoided it"
        ]
        neutral_events = ["Cross paths with a group of graffiti artists", "Witness a beautiful sunset over a derelict factory", "Encounter a disused train car covered in murals","Find an old harmonica next to the tracks", "Stumble upon a makeshift shrine or memorial", "Run into a fellow hobo who shares a story but no useful information", "Discover an old, rusted-out locomotive off to the side of the tracks", "Hear the distant sound of a live band playing in a nearby town", "Find a pile of discarded books and magazines", "Come across a campfire site that has already been extinguished"]
        padding_texts = ["Race Update: A lucky competitor catches a fast-moving freight train, surging ahead of the pack!", "Race Update: A run-in with trainyard security sets one racer back, as guard dogs nearly catch them.", "Race Update: A hidden tunnel offers an unexpected shortcut, allowing one racer to make up for lost time.", "Race Update: A fortunate find of food and water supplies helps one participant press on.", "Race Update: Quick thinking saves a competitor from capture, as they dodge into a drainage pipe.", "Race Update: Mechanical trouble slows down one racer as a makeshift cart loses a wheel.", "Race Update: A stray dog joins one competitor, helping navigate a complicated rail junction.", "Race Update: A risky detour through an industrial zone pays off, as one racer evades security.", "Race Update: A clever trap set by rivals temporarily slows down a leading competitor.", "Race Update: The discovery of an old bicycle allows one participant to pedal into a strong position."
        ]

        embed = nextcord.Embed(title="Hobo Race!", description="A new race is starting! React with 🏃‍♂️ to join within the next 20 seconds!", color=0x00ff00)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('🏃‍♂️')

        await asyncio.sleep(20)
        msg = await ctx.channel.fetch_message(msg.id)

        players = []
        for reaction in msg.reactions:
            if reaction.emoji == '🏃‍♂️':
                async for user in reaction.users():
                    if user != self.bot.user:
                        players.append({"user": user, "name": random.choice(hobo_names)})

        if len(players) <= 1:
            await ctx.send("Sorry, not enough players to start the race!")
            return

        participants_list = "\n".join([f"{player['user'].mention} as {player['name']}" for player in players])
        embed = nextcord.Embed(title="Hobos joining the race", description=participants_list, color=0xffa500)
        await ctx.send(embed=embed)

        positions = {player['user'].id: 0 for player in players}

        while len(players) > 1:  # Game loop
            events_for_round = []
            for player in players[:]:
                event_chance = random.randint(1, 14)
                user_id = player['user'].id

                if event_chance <= 2:  # Bad event
                    bad_event = random.choice(bad_events)
                    events_for_round.append(f"{player['name']} ({player['user'].mention}): {bad_event}")
                    players.remove(player)
                elif 2 < event_chance <= 4:  # Good event
                    good_event = random.choice(good_events)
                    events_for_round.append(f"{player['name']}: {good_event}")
                    positions[user_id] += 1
                else:  # Neutral event
                    neutral_event = random.choice(neutral_events)
                    events_for_round.append(f"{player['name']}: {neutral_event}")

            embed_title = random.choice(padding_texts)
            embed = nextcord.Embed(title=embed_title, description="\n".join(events_for_round), color=0x87ceeb)
            await ctx.send(embed=embed)
            await asyncio.sleep(5)

        # ... (End of game part)

            # Initialize an empty list to collect achievements
        achievements_awarded = []
        sorted_positions = sorted(positions.items(), key=lambda x: x[1], reverse=True)

        # Get the top players
        top_players = [await ctx.guild.fetch_member(player_id) for player_id, _ in sorted_positions[:3]]

        # Fetch the ProfileCog
        profile_cog = self.bot.get_cog('ProfileCog')

        if top_players:
            winner = top_players[0]
            winner_id = winner.id
            winners = [f"🥇 {top_players[0].mention}"]

            if len(top_players) > 1:
                winners.append(f"🥈 {top_players[1].mention}")
            if len(top_players) > 2:
                winners.append(f"🥉 {top_players[2].mention}")

            if profile_cog:
                # Update the winner's profile
                profile_cog.update_profile(winner_id, "races", "win")

                # Update stats for the losers
                for loser_id, _ in sorted_positions:
                    if loser_id != winner_id:
                        profile_cog.update_profile(loser_id, "races", "lose")

            winner_msg = f"Congratulations {winner.mention}! You are the winner of the Hobo Race!"
            await ctx.send(winner_msg)

            embed_description = f"Congratulations {' '.join(winners)}!"
            embed = nextcord.Embed(title="Top Performers", description=embed_description, color=0xffd700)
            await ctx.send(embed=embed)

        else:
            embed = nextcord.Embed(title="Race Result", description="It seems there were no winners this time!", color=0xff0000)
            await ctx.send(embed=embed)

    @commands.command()
    async def winrace(self, ctx):
        """Command to simulate a race win for testing purposes."""
        profile_cog = self.bot.get_cog('ProfileCog')
        if profile_cog:
            profile_cog.update_profile(ctx.author.id, "races", "win")
            await ctx.send(f"Congratulations {ctx.author.mention}! You simulated a race win!")

def setup(client):
    client.add_cog(RaceCog(client))