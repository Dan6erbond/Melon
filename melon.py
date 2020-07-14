
import configparser
import re
import traceback
from datetime import datetime

import discord
from discord.ext import commands

from const import VERSION


class Melon(commands.Bot):
    def __init__(self, **options):
        super().__init__(
            "!",
            description="Dan6erbond's take on Discord utility bots with Melons.",
            **options)

    async def on_ready(self):
        print(f'{self.user.name} is running.')

    async def send_error(self, message: str):
        await self.get_channel(556732041752739840).send(message)

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, discord.ext.commands.errors.CommandNotFound):
            pass
        else:
            await ctx.message.channel.send(error)
            print(traceback.format_exc())

    @property
    def embed(self):
        embed = discord.Embed(
            colour=discord.Colour(0).from_rgb(255, 85, 85)
        )
        embed.set_footer(text=f"Melon v{VERSION}", icon_url=self.user.avatar_url)
        embed.timestamp = datetime.utcnow()

        return embed

    async def get_message(self, id: int, channel: discord.ChannelType = None):
        try:
            message = await channel.fetch_message(id)
            return message
        except BaseException:
            for channel in channel.guild.channels:
                try:
                    message = await channel.fetch_message(id)
                    return message
                except BaseException:
                    continue
            for guild in self.guilds:
                for channel in guild.channels:
                    try:
                        message = await channel.fetch_message(id)
                        return message
                    except BaseException:
                        continue
        return None


extensions = ["cogs.util_cog", "cogs.poll_cog"]

if __name__ == "__main__":
    bot = Melon()

    config = configparser.ConfigParser()
    config.read("discord.ini")

    for extension in extensions:
        bot.load_extension(extension)
        print(f"{extension} loaded.")

    bot.run(config["MELON"]["token"])
