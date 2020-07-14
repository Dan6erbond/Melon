import os
from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from PIL import Image

import helpers.rgb as rgb

if TYPE_CHECKING:
    from main import Melon


class UtilCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
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


def setup(bot: 'Melon'):
    bot.add_cog(UtilCog(bot))
