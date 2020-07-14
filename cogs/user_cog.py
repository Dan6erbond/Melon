import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from melon import Melon


class UserCog(commands.Cog):
    def __init__(self, bot: 'Melon'):
        self.bot = bot

    @commands.command(help="Get a Discord user's avatar.")
    async def avatar(self, ctx: commands.Context, user: discord.User = None):
        user = ctx.author if user is None else user

        if not user.is_avatar_animated():
            avatar = user.avatar_url_as(format="png")
            path = os.path.join(os.getcwd(), "public", "avatars", f"{user.id}.png")
            await avatar.save(path)
        else:
            avatar = user.avatar_url_as(format="gif")
            path = os.path.join(os.getcwd(), "public", "avatars", f"{user.id}.gif")
            await avatar.save(path)

        try:
            await ctx.send(file=discord.File(path))
        except Exception as e:
            await self.bot.send_error(e)
            await ctx.send(user.avatar_url)

    @commands.command(help="Get information on a server's member.")
    async def info(self, ctx: commands.Context, user: discord.Member = None):
        user = ctx.guild.get_member(ctx.author.id) if not user else user

        msg = await ctx.send("Please wait while we find the data...")

        time_started = datetime.now()

        embed = self.bot.embed
        embed.colour = user.colour
        embed.set_author(name="User information for {0.nick}".format(user))

        embed.add_field(name="Joined at", value=user.joined_at.strftime("%Y-%m-%d"), inline=False)

        td = datetime.now() - user.joined_at
        td = "{} days".format(td.days) if td.days > 0 else "{} hours".format(td.seconds / 60 / 60)
        embed.add_field(name="In the server for", value=td, inline=False)

        roles = [" - {}".format(r.name) for r in user.roles]
        embed.add_field(name="Roles in the guild", value="\n".join(roles), inline="False")

        msg.edit(content="", embed=embed)


def setup(bot):
    bot.add_cog(UserCog(bot))
    path = os.path.join(os.getcwd(), "public", "avatars")
    Path(path).mkdir(parents=True, exist_ok=True)
