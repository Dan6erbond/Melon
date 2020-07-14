import asyncio
import os
import random
import re
from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from PIL import Image

import helpers.rgb as rgb
from const import EMOJIS, VERSION

if TYPE_CHECKING:
    from melon import Melon


class UtilCog(commands.Cog):
    def __init__(self, bot: 'Melon'):
        self.bot = bot

    @commands.command(help="Get the prominent colors in an image.", aliases=["colour"])
    async def color(self, ctx: commands.Context, amt: int = 4, tolerance: int = 9):
        amt = min(amt, 20)

        attachment = None
        try:
            attachment = ctx.message.attachments[0]
            height = attachment.height
            width = attachment.width
        except BaseException:
            async for msg in ctx.channel.history(limit=20):
                try:
                    attachment = msg.attachments[0]
                    height = attachment.height
                    width = attachment.width
                    break
                except Exception as e:
                    continue

        if attachment is None:
            return

        path = os.path.join(os.getcwd(), "public", "attachments", f"{ctx.message.id}.png")
        await attachment.save(path)

        image = Image.open(path)
        rgbs = rgb.get_colors(image, amt, tolerance)

        new_path = os.path.join(os.getcwd(), "public", "results", f"{ctx.message.id}_grid.png")

        grid = rgb.to_grid(rgbs, 125)
        res = grid.save(new_path)

        await ctx.send("", file=discord.File(new_path))

    @commands.command(help="Get a random option from a selection (Use '-' to indicate a range between numbers and spaces to separate options).")
    async def rand(self, ctx: commands.Context, *, options: str = ""):
        opts = list()
        if options != "":
            if "-" in options:
                try:
                    int1 = int(options.split("-")[0].strip())
                    int2 = int(options.split("-")[1].strip())
                    opts = list(range(int1, int2 + 1))
                except Exception as e:
                    self.bot.send_error(e)
            if len(opts) == 0:
                opts = options.split(" ")
        else:
            opts = ["HEADS", "TAILS"]

        option = opts[random.randint(0, len(opts) - 1)]

        msg = await ctx.send("⏱ 3")
        await asyncio.sleep(1)
        await msg.edit(content="⏱ 2")
        await asyncio.sleep(1)
        await msg.edit(content="⏱ 1")
        await asyncio.sleep(1)
        await msg.edit(content="{}!".format(option))

    @commands.command(help="Get the last message sent to this channel, or one with a given ID in this channel, in it's raw form.")
    async def rawmsg(self, ctx: commands.Context, id: int = 0, channel: str = ""):
        if not id:
            async for msg in ctx.channel.history(limit=2):
                message = msg
        else:
            channel = re.search(r"(\d{18})", channel)
            channel = bot.get_channel(int(channel.group(1))) if channel else ctx.channel
            message = await self.bot.get_message(id, channel)

        if not message:
            await ctx.send(f"<{EMOJIS['XMARK']}> Couldn't find the message!")
            return

        if not message.channel.permissions_for(message.channel.guild.get_member(ctx.author.id)).read_messages:
            return

        await ctx.send("```\n{}\n```".format(message.content.replace("```", r"\`\`\`")))

    @commands.command(help="Quote a message and displays the reactions in a minified version if there are any.")
    async def quote(self, ctx: commands.Context, id: int = 0, channel: str = ""):
        if not id:
            async for msg in ctx.channel.history(limit=2):
                message = msg
        else:
            channel = re.search(r"(\d{18})", channel)
            channel = bot.get_channel(int(channel.group(1))) if channel else ctx.channel
            message = await self.bot.get_message(id, channel)

        if not message:
            await ctx.send(f"<{EMOJIS['XMARK']}> Couldn't find the message!")
            return

        if not message.channel.permissions_for(message.channel.guild.get_member(ctx.author.id)).read_messages:
            return

        embed = self.bot.get_embed()
        embed.color = discord.Colour(0).from_rgb(0, 0, 0)
        embed.timestamp = message.created_at
        embed.title = f"Message by {message.author}"
        embed.url = message.jump_url
        embed.description = message.content

        reacts = list()
        for reaction in message.reactions:
            s = reaction.emoji if isinstance(reaction.emoji, str) else f"<:{reaction.emoji.name}:{reaction.emoji.id}>"
            reacts.append(f"{s} {reaction.count}")

        if reacts:
            reacts = ", ".join(reacts)
            embed.add_field(name="Reactions", value=reacts, inline=False)

        await ctx.send(embed=embed)


def setup(bot: 'Melon'):
    bot.add_cog(UtilCog(bot))
