import asyncio
from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Tuple

import discord
from discord.ext import commands
from sqlalchemy import func
from sqlalchemy.sql.expression import and_, or_, true

import helpers.fuzzle as fuzzle
from const import AUTHORIZED_USERS, EMOJIS
from database.database import session
from database.models import Category, Guild, Melon, Tag

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

    def get_guild(self, guild_id: int) -> Guild:
        guild = session.query(Guild).filter(Guild.guild_id == guild_id).first()

        if not guild:
            categories = session.query(Category).filter(Category.default == true()).all()
            guild = Guild(guild_id=guild_id, categories=categories)
            session.add(guild)
            session.commit()

        return guild

    def order_melons(self, melons: List[Melon]) -> Tuple[List[Melon], List[Melon], List[Melon]]:
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
    async def rawmelon(self, ctx: commands.Context, *, key):
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
    async def meloncat(self, ctx: commands.Context, *, cat):
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
    async def meloncats(self, ctx: commands.Context):
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

    async def ask_prompt(self, ctx: commands.Context, prompt: str, timeout: int = 2 * 60):
        await ctx.send(prompt)
        try:
            message = await self.bot.wait_for("message",
                                              check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                                              timeout=timeout)
        except asyncio.exceptions.TimeoutError:
            await ctx.send(f"<{EMOJIS['XMARK']}> That took too long! " +
                           "You can restart the process by calling this command again.")
            return

        return message.content

    @commands.command(help="Add a Melon to a given category.")
    async def addmelon(self, ctx: commands.Context, *, arg: str = ""):
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        if arg and ctx.author.id in AUTHORIZED_USERS:
            category = session.query(Category).filter(func.lower(Category.name) == arg.lower()).first()
            if not category:
                msg = await ctx.send(f"<{EMOJIS['XMARK']}> Category '{arg}' doesn't exist! Would you like to create it?")
                await msg.add_reaction(f"<{EMOJIS['CHECK']}>")
                await msg.add_reaction(f"<{EMOJIS['XMARK']}>")

                try:
                    reaction = await bot.wait_for("reaction_add", check=check, timeout=2 * 60)
                    if reaction[0].custom_emoji and reaction[0].emoji.id == int(EMOJIS['CHECK'].split(":")[2]):
                        category = Category(name=arg)
                        session.add(category)
                        await ctx.send(f"<{EMOJIS['CHECK']}> Category '{arg}' successfully created!")
                except asyncio.exceptions.TimeoutError:
                    await ctx.send(f"<{EMOJIS['XMARK']}> That took too long! " +
                                   "You can restart the process by calling this command again.")
                    return

            key = await self.ask_prompt(ctx, "❓ What should the key of the Melon be?")
            if not key:
                return
            else:
                key = key.lower()

            melon = session.query(Melon).filter(
                and_(func.lower(Melon.key) == key,
                     Melon.category_id == category.category_id)).first()
            if melon:
                await ctx.send(f"❗ A Melon with that key already exists in {arg}! " +
                               "You can edit it with `!editmelon`.")
                return

            await ctx.send(f"❓ What should the value of {key} be?")
            message = await self.bot.wait_for("message", check=check)

            melon = Melon(key=key,
                          category=category,
                          value=message.content,
                          created_by=ctx.author.id)
            session.add(melon)
            session.commit()

            await ctx.send(f"<{EMOJIS['CHECK']}> Successfully added Melon '{key}' to the global Melons!")
        else:
            guild = self.get_guild(ctx.guild.id)

            if not guild.melon_role:
                await ctx.send(f"<{EMOJIS['XMARK']}> Custom Melons for this guild haven't been enabled!")
                return

            roles = [role.id for role in ctx.author.roles]
            if guild.melon_role not in roles:
                await ctx.send(f"<{EMOJIS['XMARK']}> You aren't authorized to create Melons in this guild!")
                return

            if not arg:
                key = await self.ask_prompt(ctx, "❓ What should the key of the Melon be?")
                if not key:
                    return
                else:
                    key = key.lower()
            else:
                key = arg.lower()

            melon = session.query(Melon).filter(
                and_(func.lower(Melon.key) == key,
                     Melon.guild_id == guild.guild_id)).first()
            if melon:
                await ctx.send(f"❗ A Melon with that key already exists in this guild! " +
                               "You can edit it with `!editmelon`.")
                return

            await ctx.send(f"❓ What should the value of {key} be?")
            message = await self.bot.wait_for("message", check=check)

            melon = Melon(key=key,
                          guild=guild,
                          value=message.content,
                          created_by=ctx.author.id)
            session.add(melon)
            session.commit()

            await ctx.send(f"<{EMOJIS['CHECK']}> Successfully added Melon '{key}' to the guild Melons!")

    @commands.command(help="Add tags to a Melon.")
    async def addtags(self, ctx: commands.Context, *, key: str = ""):
        if not key:
            key = await self.ask_prompt(ctx, "❓ What is the key used for the Melon?")
            if not key:
                return
            else:
                key = key.lower()

        guild = self.get_guild(ctx.guild.id)

        if ctx.author.id in AUTHORIZED_USERS:
            melon = session.query(Melon).filter(func.lower(Melon.key) == key).first()
        else:
            melon = session.query(Melon).filter(
                and_(func.lower(Melon.key) == key,
                     Melon.guild_id == guild.guild_id)).first()

        if not melon:
            await ctx.send(f"<{EMOJIS['XMARK']}> Melon '{key}' doesn't exist!")

        tags = await self.ask_prompt(ctx, f"❓ Which tags should be added to the Melon '{key}'?")
        if not tags:
            return
        tags = tags.split(" ")
        for t in tags:
            tag = session.query(Tag).filter(func.lower(Tag.value) == t.lower()).first()
            if not tag:
                tag = Tag(value=t)
                session.add(tag)
            elif tag in melon.tags:
                continue
            melon.tags.append(tag)
        session.commit()
        await ctx.send(f"<{EMOJIS['CHECK']}> Successfully added tags `{', '.join(tags)}` to Melon '{melon.key}'!")


def setup(bot: 'Melon'):
    bot.add_cog(MelonCog(bot))
