from datetime import datetime
from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from sqlalchemy.sql.expression import or_, true

import helpers.fuzzle as fuzzle
from database.database import session
from database.models import Category, Guild, Melon

if TYPE_CHECKING:
    from melon import Melon


class MelonCog(commands.Cog):
    def __init__(self, bot: 'Melon'):
        self.bot = bot

    def get_melon_string(self, ctx, search, melon):
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

    @commands.command()
    async def melon(self, ctx: commands.Context, *, search=""):
        guild = session.query(Guild).filter(Guild.guild_id == ctx.guild.id).first()

        if not guild:
            categories = session.query(Category).filter(Category.default == true()).all()
            guild = Guild(guild_id=ctx.guild.id, categories=categories)
            session.add(guild)
            session.commit()

        melons = session.query(Melon).filter(or_(Melon.guild_id == guild.guild_id,
                                                 Melon.category_id.in_(c.category_id for c in guild.categories))).all()

        if len(melons) == 0:
            await ctx.send("Your guild has no enabled Melon categories. Please contact an admin to enable them.")
            return

        if search == "":
            melons = sorted(melons, key=lambda m: m.key)
            melons = sorted(melons, key=lambda m: m.uses)

            popular = [melon.key for melon in melons[:7]]
            new = [melon.key for melon in melons[7:] if melon.uses == 0]
            others = [melon.key for melon in melons[7:] if melon.uses > 0]

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
                except Exception as e:
                    await self.bot.send_error(e)
                finally:
                    seconds += (datetime.now() - time_started).seconds


def setup(bot: 'Melon'):
    bot.add_cog(MelonCog(bot))
