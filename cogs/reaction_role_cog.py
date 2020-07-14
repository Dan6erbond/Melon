import discord
from discord.ext import commands
from sqlalchemy.sql.expression import and_

from database.database import session
from database.models import ReactionRole


class ReactionRoleCog(commands.Cog):
    def __init__(self, bot: 'Melon'):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == bot.user.id:
            return

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
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


def setup(bot: 'Melon'):
    bot.add_cog(ReactionRoleCog(bot))
