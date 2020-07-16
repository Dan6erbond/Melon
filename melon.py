
import configparser
import re
import traceback
from datetime import datetime

import discord
from discord.ext import commands

from const import MAINTAINER, VERSION
from database.database import session
from database.models import Category, Guild
from sqlalchemy.sql.expression import true


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
            traceback.print_tb(error.__traceback__)

    @property
    def embed(self):
        embed = discord.Embed(
            colour=discord.Colour(0).from_rgb(255, 85, 85)
        )
        embed.set_footer(text=f"Melon v{VERSION} by {MAINTAINER}", icon_url=self.user.avatar_url)
        embed.timestamp = datetime.utcnow()

        return embed

    def get_guild(self, guild_id: int) -> Guild:
        guild = session.query(Guild).filter(Guild.guild_id == guild_id).first()

        if not guild:
            categories = session.query(Category).filter(Category.default == true()).all()
            guild = Guild(guild_id=guild_id, categories=categories)
            session.add(guild)
            session.commit()

        return guild

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


extensions = ["cogs.util_cog", "cogs.poll_cog", "cogs.user_cog",
              "cogs.reaction_role_cog", "cogs.melon_cog", "cogs.melon_categories_cog"]

if __name__ == "__main__":
    bot = Melon()

    config = configparser.ConfigParser()
    config.read("discord.ini")

    for extension in extensions:
        bot.load_extension(extension)
        print(f"{extension} loaded.")

    bot.run(config["MELON"]["token"])
