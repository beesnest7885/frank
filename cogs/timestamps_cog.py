import nextcord
from nextcord.ext import commands
from datetime import datetime, timezone
import pytz
import humanize

# Mapping of common timezone abbreviations to their full names
TIMEZONE_ABBREVIATIONS = {
    "CST": "America/Chicago",  # Central Standard Time (North America)
    "EST": "America/New_York",  # Eastern Standard Time (North America)
    "PST": "America/Los_Angeles",  # Pacific Standard Time (North America)
    "MST": "America/Denver",  # Mountain Standard Time (North America)
    "UTC": "UTC",  # Coordinated Universal Time
    "GMT": "Europe/London",  # Greenwich Mean Time
    "CET": "Europe/Paris",  # Central European Time
    "EET": "Europe/Athens",  # Eastern European Time
    "IST": "Asia/Kolkata",  # India Standard Time
    "CST-CHINA": "Asia/Shanghai",  # China Standard Time
    "JST": "Asia/Tokyo",  # Japan Standard Time
    "AEST": "Australia/Sydney",  # Australian Eastern Standard Time
    # Add more abbreviations as needed
}

class TimestampsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="when")
    async def convert_to_local_time(self, ctx, *, time_input: str):
        """
        Converts a given time in a specified timezone to the user's local time.
        Usage:
        - .when HH:MM TZ (e.g., 10:45 CST or 14:30 UTC)
        """
        try:
            # Split input into time and timezone
            time_part, tz_part = time_input.rsplit(" ", 1)

            # Parse the input time
            input_time = datetime.strptime(time_part, "%H:%M")

            # Convert the timezone abbreviation to full name if necessary
            tz_name = TIMEZONE_ABBREVIATIONS.get(tz_part.upper(), tz_part.upper())

            # Convert to the given timezone
            tz = pytz.timezone(tz_name)
            time_with_tz = tz.localize(input_time)

            # Assume the user's local timezone (e.g., "Europe/London")
            # Modify this default or implement a method for users to set their timezone
            user_timezone = pytz.timezone("Europe/London")  # Replace with user's actual timezone if available

            # Convert to the user's local timezone
            local_time = time_with_tz.astimezone(user_timezone)

            # Calculate the time difference between the two timezones
            time_difference = local_time.utcoffset() - time_with_tz.utcoffset()
            hours, remainder = divmod(time_difference.total_seconds(), 3600)
            minutes = remainder // 60
            time_difference_str = f"{int(hours)} hours and {int(minutes)} minutes"

            # Send the result
            await ctx.send(f"Provided time: {time_with_tz.strftime('%H:%M')}\n"
                           f"Local time: {local_time.strftime('%H:%M')}\n"
                           f"Time difference: {time_difference_str}")

        except (ValueError, pytz.UnknownTimeZoneError) as e:
            await ctx.send(f"Error: {str(e)}. Please use the format HH:MM TZ (e.g., 10:45 CST or 14:30 UTC).")

    @commands.command(name="time")
    async def convert_to_timestamp(self, ctx, *, time_input: str):
        """
        Converts a given date, time, or both into a universal timestamp.
        Usage:
        - .time YYYY-MM-DD (date only)
        - .time HH:MM:SS (time only)
        - .time YYYY-MM-DD HH:MM:SS (both)
        """
        try:
            now = datetime.now(tz=timezone.utc)

            if "-" in time_input and ":" in time_input:
                # Full date and time
                provided_time = datetime.strptime(time_input, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            elif "-" in time_input:
                # Date only, assume midnight
                provided_time = datetime.strptime(time_input, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            elif ":" in time_input:
                # Time only, use today's date
                provided_time = datetime.combine(
                    now.date(),
                    datetime.strptime(time_input, "%H:%M:%S").time()
                ).replace(tzinfo=timezone.utc)
            else:
                raise ValueError("Invalid format")

            # Convert to UNIX timestamp
            unix_timestamp = int(provided_time.timestamp())

            # Generate Discord timestamps
            discord_timestamps = {
                "Default": f"<t:{unix_timestamp}>",
                "Relative": f"<t:{unix_timestamp}:R>",
                "Short Date/Time": f"<t:{unix_timestamp}:f>",
                "Long Date/Time": f"<t:{unix_timestamp}:F>",
                "Default + Relative": f"<t:{unix_timestamp}> (<t:{unix_timestamp}:R>)",
            }

            # Send the result
            await ctx.send(f"Here are the Discord timestamps you can use:\n"
                           f"Default (absolute): `{discord_timestamps['Default']}`\n"
                           f"Relative (from now): `{discord_timestamps['Relative']}`\n"
                           f"Short Date/Time: `{discord_timestamps['Short Date/Time']}`\n"
                           f"Long Date/Time: `{discord_timestamps['Long Date/Time']}`\n"
                           f"Default + Relative: `{discord_timestamps['Default + Relative']}`")

        except ValueError as e:
            await ctx.send(f"Error: {str(e)}. Please use one of the following formats:\n"
                           "- YYYY-MM-DD (date only)\n"
                           "- HH:MM:SS (time only)\n"
                           "- YYYY-MM-DD HH:MM:SS (both)")

def setup(bot):
    bot.add_cog(TimestampsCog(bot))
