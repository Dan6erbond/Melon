import discord
from discord.ext import commands
from sqlalchemy.sql.expression import and_

from const import EMOJIS
from database.database import session
from database.models import ReactionRole


class ReactionRoleCog(commands.Cog):
    def __init__(self, bot: 'Melon'):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == bot.user.id:
            return

        emoji = payload.emoji.name if not payload.emoji.is_custom_emoji(
        ) else f"<:{payload.emoji.name}:{payload.emoji.id}>"

        react_role = session.query(ReactionRole).filter(
            and_(
                ReactionRole.message_id == payload.message_id,
                ReactionRole.emoji == emoji)).first()

        if react_role:
            guild = bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            role = guild.get_role(react_role.role)
            try:
                await member.add_roles(role)
            except Exception as e:
                self.bot.send_error(e)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == bot.user.id:
            return

        emoji = payload.emoji.name if not payload.emoji.is_custom_emoji(
        ) else f"<:{payload.emoji.name}:{payload.emoji.id}>"

        react_role = session.query(ReactionRole).filter(
            and_(
                ReactionRole.message_id == payload.message_id,
                ReactionRole.emoji == emoji)).first()

        if react_role:
            guild = bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            role = guild.get_role(react_role.role)
            try:
                await member.remove_roles(role)
            except Exception as e:
                self.bot.send_error(e)

    @commands.command(help="Adds a reaction-role to a message.")
    @commands.has_permissions(manage_roles=True)
    async def addreactrole(self, ctx: commands.Context, emoji: str, role: discord.Role, msg: int, channel: discord.TextChannel = None):
        channel = ctx.channel if channel is None else channel
        msg = await channel.fetch_message(msg)
        emoji = emoji.replace("<", "").replace(">", "")

        if msg:
            await msg.add_reaction(emoji)

            react_role = session.query(ReactionRole).filter(
                and_(ReactionRole.message_id == msg.id, ReactionRole.emoji == emoji)).first()

            if not react_role:
                react_role = ReactionRole(message_id=msg.id, emoji=emoji)
                session.add(react_role)
                session.commit()

                await ctx.message.delete()
                await ctx.send(f"<{EMOJIS['CHECK']}> Successfully added reaction-role!", delete_after=3)
            else:
                await ctx.send(f"<{EMOJIS['XMARK']}> This emoji is already being used as a reaction-role on this message!", delete_after=3)

    @commands.command(help="Adds a reaction-role to a message.")
    @commands.has_permissions(manage_roles=True)
    async def remreactrole(self, ctx, emoji: str, msg: int, channel: discord.TextChannel = None):
        channel = ctx.channel if channel is None else channel
        msg = await channel.fetch_message(msg)
        emoji = emoji.replace("<", "").replace(">", "")

        if msg:
            try:
                await msg.remove_reaction(emoji, self.bot.user)
            except Exception as e:
                print(e)
                return

            react_role = session.query(ReactionRole).filter(
                and_(ReactionRole.message_id == msg.id, ReactionRole.emoji == emoji)).first()

            if react_role:
                session.delete(react_role)
                session.commit()
                await ctx.send(f"<{EMOJIS['CHECK']}> Successfully removed reaction-role!".format(check), delete_after=3)
            else:
                await ctx.send(f"<{EMOJIS['XMARK']}> Couldn't find reaction-role in the DB!", delete_after=3)


def setup(bot: 'Melon'):
    bot.add_cog(ReactionRoleCog(bot))
