import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from const import EMOJIS

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

        embed = self.bot.embed
        embed.colour = user.colour
        embed.set_author(name="User information for {0.nick}".format(user))

        embed.add_field(name="Joined at", value=user.joined_at.strftime("%Y-%m-%d"), inline=False)

        td = datetime.now() - user.joined_at
        td = "{} days".format(td.days) if td.days > 0 else "{} hours".format(td.seconds / 60 / 60)
        embed.add_field(name="In the server for", value=td, inline=False)

        roles = [" - {}".format(r.name) for r in user.roles]
        embed.add_field(name="Roles in the guild", value="\n".join(roles), inline="False")

        msg = await ctx.send(content=f"Here's the information for {user.mention}:", embed=embed)

        msg1 = await ctx.send("Basic information found, fetch more?")
        await msg1.add_reaction(EMOJIS["CHECK"])

        def check(r, u):
            return u.id == ctx.author.id

        try:
            reaction = await self.bot.wait_for("reaction_add", check=check, timeout=2 * 60)
            if reaction[0].custom_emoji and reaction[0].emoji.id == int(EMOJIS["CHECK"].split(":")[2]):
                await msg1.edit(content="Please wait while I fetch the data...")
                time_started = datetime.now()

                count = 0
                long_count = 0
                char_count = 0
                word_count = 0
                for channel in user.guild.channels:
                    channel_count = 0
                    permissions = channel.permissions_for(user)
                    if not permissions.read_messages:
                        continue
                    if not isinstance(channel, discord.TextChannel):
                        continue
                    async for msg in channel.history(limit=None):
                        if msg.author.id == user.id:
                            count += 1
                            channel_count += 1
                            chars = len(msg.content)
                            char_count += chars
                            word_count += len(msg.content.split(" "))
                            if chars > 5:
                                long_count += 1

                embed.add_field(name="Messages written to the guild", value=str(count), inline=False)
                embed.add_field(name="Messages longer than 5 characters", value=str(long_count), inline=False)
                embed.add_field(name="Characters written", value=str(char_count), inline=False)
                embed.add_field(name="Words written", value=str(word_count), inline=False)

                await msg.edit(content="", embed=embed)
                await msg1.edit(content=f"Data found! Took me {datetime.now() - time_started}.")
        except Exception as e:
            await self.bot.send_error(e)


def setup(bot):
    bot.add_cog(UserCog(bot))
    path = os.path.join(os.getcwd(), "public", "avatars")
    Path(path).mkdir(parents=True, exist_ok=True)
