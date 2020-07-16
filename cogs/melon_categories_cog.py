import discord
from discord.ext import commands
from sqlalchemy import func

from const import EMOJIS
from database.database import session
from database.models import Category
from helpers import is_authorized


class MelonCategoriesCog(commands.Cog):
    def __init__(self, bot: 'Melon'):
        self.bot = bot

    @commands.command(help="Add a Melon category.")
    @commands.check(is_authorized)
    async def addcat(self, ctx: commands.Context, *, cat: str):
        category = session.query(Category).filter(func.lower(Category.name) == cat.lower()).first()

        if category:
            await ctx.send(f"<{EMOJIS['XMARK']}> '{cat}' is already a category in the Melons!")
        else:
            category = Category(name=cat)
            session.add(category)
            session.commit()
            await ctx.send(f"<{EMOJIS['CHECK']}> Successfully added '{cat}' as a category in the Melons!")


def setup(bot: 'Melon'):
    bot.add_cog(MelonCategoriesCog(bot))
