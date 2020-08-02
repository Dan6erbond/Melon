import asyncio

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

    @commands.command(help="Delete a Melon category.")
    @commands.check(is_authorized)
    async def delcat(self, ctx: commands.Context, *, cat: str):
        category = session.query(Category).filter(func.lower(Category.name) == cat.lower()).first()

        if not category:
            await ctx.send(f"<{EMOJIS['XMARK']}> '{cat}' isn't a category in the Melons!")
            return

        message = await ctx.send(f"❓ Are you sure you want to remove {cat} from the Melons?")
        await message.add_reaction(EMOJIS['CHECK'])
        await message.add_reaction(EMOJIS['XMARK'])

        try:
            reaction = await self.bot.wait_for("reaction_add",
                                               check=lambda r, u: u.id == ctx.author.id and r.message.id == message.id,
                                               timeout=2 * 60)
        except asyncio.exceptions.TimeoutError:
            await ctx.send(f"<{EMOJIS['XMARK']}> That took too long! " +
                           "You can restart the process by calling this command again.")
            return
        finally:
            if reaction[0].custom_emoji and reaction[0].emoji.id == int(EMOJIS['CHECK'].split(":")[2]):
                session.delete(category)
                session.commit()
                await ctx.send(f"<{EMOJIS['CHECK']}> Successfully removed '{cat}' as a category in the Melons!")

    @commands.command(help="Enable a Melon category in this guild.")
    @commands.has_permissions(administrator=True)
    async def enablecat(self, ctx: commands.Context, *, cat: str):
        category = session.query(Category).filter(func.lower(Category.name) == cat.lower()).first()

        if not category:
            await ctx.send(f"<{EMOJIS['XMARK']}> Melon category '{cat}' doesn't exist!")
            return

        guild = self.bot.get_db_guild(ctx.guild.id)

        category_ids = [cat.category_id for cat in guild.categories]
        if category.category_id in category_ids:
            await ctx.send(f"❗ Melon category '{cat}' was already enabled!")
        else:
            guild.categories.append(category)
            session.commit()
            await ctx.send(f"<{EMOJIS['CHECK']}> Melon category '{cat}' successfully enabled!")

    @commands.command(help="Disable a Melon category in this guild.")
    @commands.has_permissions(administrator=True)
    async def disablecat(self, ctx, cat):
        category = session.query(Category).filter(func.lower(Category.name) == cat.lower()).first()

        if not category:
            await ctx.send(f"<{EMOJIS['XMARK']}> Melon category '{cat}' doesn't exist!")
            return

        guild = self.bot.get_db_guild(ctx.guild.id)

        category_ids = [cat.category_id for cat in guild.categories]
        if category.category_id in category_ids:
            guild.categories.remove(category)
            session.commit()
            await ctx.send(f"<{EMOJIS['CHECK']}> Melon category '{cat}' successfully disabled!")
        else:
            await ctx.send(f"<{EMOJIS['XMARK']}> Melon category '{cat}' was never enabled in this guild!")


def setup(bot: 'Melon'):
    bot.add_cog(MelonCategoriesCog(bot))
