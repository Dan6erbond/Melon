import asyncio
from datetime import datetime
from typing import TYPE_CHECKING, Dict, List

import discord
from discord.ext import commands
from sqlalchemy import func
from sqlalchemy.sql.expression import and_, or_, true

import helpers.fuzzle as fuzzle
from const import EMOJIS
from database.database import session
from database.models import Category, Guild, Melon

if TYPE_CHECKING:
    from melon import Melon


class MelonCog(commands.Cog):
    def __init__(self, bot: 'Melon'):
        self.bot = bot

    def get_melon_string(self, ctx: commands.Context, search: str, melon: Dict):
        value = melon["value"].format(ctx, search)

        add = None
        if melon["creator"] and melon["created"]:
            creator = self.bot.get_user(melon["creator"])
            date = melon["created"].strftime("%d.%m.%Y")
            add = f"Created by {creator} on {date}."
        elif melon["creator"]:
            creator = self.bot.get_user(melon["creator"])
            add = f"Created by {creator}."
        elif melon["created"]:
            date = melon["created"].strftime("%d.%m.%Y")
            add = f"Created on {date}."

        if add:
            value += f"\n\n*[{add}]*"

        return value

    def get_guild(self, guild_id: int):
        guild = session.query(Guild).filter(Guild.guild_id == guild_id).first()

        if not guild:
            categories = session.query(Category).filter(Category.default == true()).all()
            guild = Guild(guild_id=guild_id, categories=categories)
            session.add(guild)
            session.commit()

        return guild

    def order_melons(self, melons: List[Melon]):
        melons = sorted(melons, key=lambda m: m.key)
        melons = sorted(melons, key=lambda m: m.uses)

        popular = [melon.key for melon in melons[:7]]
        new = [melon.key for melon in melons[7:] if melon.uses == 0]
        others = [melon.key for melon in melons[7:] if melon.uses > 0]

        return popular, new, others

    @commands.command(help="Search through a wide array of Melons with keywords and get the information you need!")
    async def melon(self, ctx: commands.Context, *, search=""):
        guild = self.get_guild(ctx.guild.id)
        melons = session.query(Melon).filter(or_(Melon.guild_id == guild.guild_id,
                                                 Melon.category_id.in_(c.category_id for c in guild.categories))).all()

        if len(melons) == 0:
            await ctx.send("Your guild has no enabled Melon categories. Please contact an admin to enable them.")
            return

        if search == "":
            popular, new, others = self.order_melons(melons)

            await ctx.send("You can search for a Melon by typing `!melon [search]`." +
                           "There are many available Melons.\n\n" +
                           f"**Popular Melons: **{', '.join(popular)}\n" +
                           f"**New Melons: **{', '.join(new)}\n" +
                           f"**Other Melons: **{', '.join(others)}")
            return

        results = fuzzle.find([melon.to_dict() for melon in melons], search, return_all=True)

        if not results:
            await ctx.send(f"We couldn't find any Melons or Tags with the search '{search}'.")
        elif len(results) == 1 and results[0]["match"]:
            melon = session.query(Melon).filter(Melon.melon_id == results[0]["id"]).first()
            melon.uses += 1
            session.commit()
            await ctx.send(self.get_melon_string(ctx, search, results[0]))
        else:
            max_results = min(3, len(results))
            emojis = ["1\N{combining enclosing keycap}",
                      "2\N{combining enclosing keycap}",
                      "3\N{combining enclosing keycap}",
                      "4\N{combining enclosing keycap}",
                      "5\N{combining enclosing keycap}"][:3]
            similar = [f"{emojis[i]} {results[i]['key']}" for i in range(max_results)]
            keys = set()

            if results[0]["match"]:
                result = results[0]
                key = result["key"]

                similar = [f"{emojis[i]} {results[i]['key']}" for i in range(1, max_results)]
                similar = f"\n\n**Not what you were looking for? Try** {', '.join(similar)}**.**" if similar else ""

                melon = session.query(Melon).filter(Melon.melon_id == result["id"]).first()
                melon.uses += 1
                session.commit()

                keys.add(key)
                content = f"**__{key}__**\n\n{self.get_melon_string(ctx, search, result)}{similar}"
                msg = await ctx.send(content)
            else:
                similar = '\n'.join(similar)
                content = f"We couldn't find any results. Maybe you meant?\n\n{similar}\n\n*Powered by Fuzzle™.*"
                msg = await ctx.send(content)

            for e in emojis:
                await msg.add_reaction(e)

            seconds = 0
            while seconds < 120:
                try:
                    time_started = datetime.now()

                    def check(r, u):
                        return u.id == ctx.author.id and r.message.id == msg.id and r.emoji in emojis

                    reaction = await self.bot.wait_for("reaction_add", check=check, timeout=120 - seconds)

                    j = emojis.index(reaction[0].emoji)
                    result = results[j]
                    key = result["key"]

                    similar = [f"{emojis[i]} {results[i]['key']}" for i in range(max_results) if i != j]
                    similar = f"\n\n**Not what you were looking for? Try** {', '.join(similar)}**.**" if similar else ""

                    if key not in keys:
                        melon = session.query(Melon).filter(Melon.melon_id == result["id"]).first()
                        melon.uses += 1
                        session.commit()
                        keys.add(key)

                    content = f"**__{key}__**\n\n{self.get_melon_string(ctx, search, result)}{similar}"
                    await msg.edit(content=content)
                except asyncio.exceptions.TimeoutError:
                    pass
                except Exception as e:
                    await self.bot.send_error(e)
                finally:
                    seconds += (datetime.now() - time_started).seconds

    @commands.command(help="Get the RAW markdown version of a Melon.")
    async def rawmelon(self, ctx, *, key):
        guild = self.get_guild(ctx.guild.id)

        melon = session.query(Melon).filter(
            and_(func.lower(Melon.key) == key.lower(),
                 or_(Melon.guild_id == guild.guild_id,
                     Melon.category_id.in_(c.category_id for c in guild.categories)))).first()

        if melon:
            value = melon.value.replace("```", r"\`\`\`")
            await ctx.send(f"```\n{value}\n```")
        else:
            await ctx.send("❗ No Melon or Tag found under that name!")

    @commands.command(help="Display all the available Melons from a category.")
    async def meloncat(self, ctx, *, cat):
        category = session.query(Category).join(Guild, Category.guilds).filter(
            and_(Guild.guild_id == ctx.guild.id,
                 func.lower(Category.name) == cat.lower())).first()

        if category:
            popular, new, others = self.order_melons(category.melons)

            await ctx.send(f"Here are the available Melons in '{cat}'. " +
                           "You can search for a Melon by typing `!melon [seach]`.\n\n" +
                           f"**Popular Melons: **{', '.join(popular)}\n" +
                           f"**New Melons: **{', '.join(new)}\n" +
                           f"**Other Melons: **{', '.join(others)}")
        else:
            await ctx.send(f"<{EMOJIS['XMARK']}> This Melon category isn't available or has been disabled in this guild.")

    @commands.command(help="Display the enabled/disabled categories for this guild.")
    async def meloncats(self, ctx):
        guild = self.get_guild(ctx.guild.id)
        enabled = [category.name for category in guild.categories]

        disabled_categories = session.query(Category).filter(
            ~Category.guilds.any(Guild.guild_id == ctx.guild.id)).all()
        disabled = [category.name for category in disabled_categories]

        await ctx.send(
            "These are the enabled/disabled Melon categories for this guild. " +
            "A server admin can enable a Melon category by typing `!enablecat [cat]`.\n\n" +
            f"**Enabled categories: **{', '.join(enabled)}\n" +
            f"**Disabled cateogires: **{', '.join(disabled)}")


def setup(bot: 'Melon'):
    bot.add_cog(MelonCog(bot))
