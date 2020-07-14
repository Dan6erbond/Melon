import re
from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from sqlalchemy.sql.expression import and_, true

from const import EMOJIS
from database.database import session
from database.models import Channel, ChannelEmoji

if TYPE_CHECKING:
    from melon import Melon


class PollCog(commands.Cog):
    def __init__(self, bot: 'Melon'):
        self.bot = bot

    async def handle_poll(self, message: discord.Message):
        if message.author.bot:
            return

        emotes = re.findall(r"<\w+:\d+>", message.content)
        emotes.extend(re.findall(r"\d\\u20e3", message.content.lower()))

        for c in message.content:
            unicode = c.encode("unicode-escape").decode('utf-8')
            if unicode.lower().startswith("\\u"):
                emotes.append(c)

        for i in range(len(emotes)):
            for n in "0123456789":
                unicode = emotes[i].lower().encode("unicode-escape").decode('utf-8')
                if unicode.startswith(n) and "\\u20e3" in unicode:
                    emotes[i] = "{}\N{combining enclosing keycap}".format(n)

        count = 0
        for e in emotes:
            try:
                await message.add_reaction(e)
                count += 1
            except Exception as _e:
                print(e, _e)

        if count == 0:
            channel = session.query(Channel).filter(Channel.channel_id == message.channel.id).first()
            if channel:
                found = False
                for emoji in channel.emojis:
                    if emoji.default_emoji:
                        await message.add_reaction(emoji.emoji)
                if not found:
                    await message.add_reaction("👍")
                    await message.add_reaction("👎")

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
        try:
            msg = await self.bot.get_channel(int(payload.data["channel_id"])).fetch_message(payload.message_id)
        except Exception as e:
            await self.bot.send_error(e)
            return

        if msg:
            channel = session.query(Channel).filter(Channel.channel_id == msg.channel.id).first()
            if channel and channel.poll_channel:
                await self.handle_poll(msg)

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author.bot:
            return

        channel = session.query(Channel).filter(Channel.channel_id == msg.channel.id).first()

        if channel and channel.poll_channel:
            for emoji in channel.emojis:
                if not emoji.default_emoji:
                    await msg.add_reaction(emoji.emoji)
            await self.handle_poll(msg)

        await bot.process_commands(msg)

    @commands.command(help="Add a default emoji that is added to poll channels")
    @commands.has_permissions(manage_channels=True)
    async def adddefault(self, ctx: commands.Context, emoji: str):
        try:
            await ctx.message.add_reaction(emoji)
        except BaseException:
            await ctx.send(f"<{EMOJIS['XMARK']}> Uh-oh, looks like that emoji doesn't work!")
            return

        channel = session.query(Channel).filter(Channel.channel_id == ctx.channel.id).first()

        if not channel or not channel.poll_channel:
            msg = f"<{EMOJIS['XMARK']}> This channel isn't setup as a poll channel! Please use `!togglepoll` to enable the feature!"
            await ctx.send(msg)
            return

        channel_emoji = ChannelEmoji(channel_id=channel.channel_id, emoji=emoji, default_emoji=True)
        session.add(channel_emoji)
        session.commit()

        await ctx.send(f"<{EMOJIS['CHECK']}> Added {emoji} to the list of default emojis for this poll channel!", delete_after=3)
        await ctx.message.delete()

    @commands.command(help="Add a default emoji that is added to poll channels")
    @commands.has_permissions(manage_channels=True)
    async def remdefault(self, ctx: commands.Context, emoji: str):
        try:
            await ctx.message.add_reaction(emoji)
        except BaseException:
            await ctx.send(f"<{EMOJIS['XMARK']}> Uh-oh, looks like that emoji doesn't work!")
            return

        channel = session.query(Channel).filter(Channel.channel_id == ctx.channel.id).first()

        if not channel or not channel.poll_channel:
            msg = f"<{EMOJIS['XMARK']}> This channel isn't setup as a poll channel! Please use `!togglepoll` to enable the feature!"
            await ctx.send(msg)
            return

        channel_emoji = session.query(ChannelEmoji).filter(
            and_(
                ChannelEmoji.channel_id == ctx.channel.id,
                ChannelEmoji.emoji == emoji)).first()

        if channel_emoji:
            channel_emoji.delete()
            session.commit()
            await ctx.send(f"<{EMOJIS['CHECK']}> Removed {emoji} from the list of default emojis for this poll channel!", delete_after=3)
            await ctx.message.delete()
        else:
            await ctx.send(f"<{EMOJIS['XMARK']}> {emoji} isn't a default poll emoji in this channel!")

    @commands.command(help="Add an emomji to the database which the bot will add to all messages sent to this channel.",
                      aliases=["addmoji", "admoji"])
    @commands.has_permissions(manage_channels=True)
    async def addemoji(self, ctx: commands.Context, emoji: str):
        try:
            await ctx.message.add_reaction(emoji)
        except BaseException:
            await ctx.send(f"<{EMOJIS['XMARK']}> Uh-oh, looks like that emoji doesn't work!")
            return

        channel = session.query(Channel).filter(Channel.channel_id == ctx.channel.id).first()

        if not channel or not channel.poll_channel:
            msg = f"<{EMOJIS['XMARK']}> This channel isn't setup as a poll channel! Please use `!togglepoll` to enable the feature!"
            await ctx.send(msg)
            return

        channel_emoji = session.query(ChannelEmoji).filter(
            and_(
                ChannelEmoji.channel_id == ctx.channel.id,
                ChannelEmoji.emoji == emoji)).first()

        if not channel_emoji:
            channel_emoji = ChannelEmoji(channel_id=ctx.channel.id, emoji=emoji)
            session.add(channel_emoji)
            session.commit()
            await ctx.send(f"<{EMOJIS['CHECK']}> Successfully added {emoji} to the list of emojis to add in this channel!", delete_after=3)

            async for msg in ctx.history(limit=None):
                await msg.add_reaction(emoji)
        else:
            await ctx.send(f"<{EMOJIS['XMARK']}> That emoji is already set for this channel!")

    @commands.command(help="Remove an emoji from the list of emojis that are added to this channel's messages.",
                      aliases=["removeemoji", "rememoji"])
    @commands.has_permissions(manage_channels=True)
    async def remoji(self, ctx: commands.Context, emoji: str):
        member = ctx.guild.get_member(bot.user.id)
        try:
            await ctx.message.remove_reaction(emoji, member)
        except BaseException:
            await ctx.send(f"<{EMOJIS['XMARK']}> Uh-oh, looks like that emoji doesn't work!")
            return

        channel_emoji = session.query(ChannelEmoji).filter(
            and_(
                ChannelEmoji.channel_id == ctx.channel.id,
                ChannelEmoji.emoji == emoji)).first()

        if channel_emoji:
            channel_emoji.delete()
            session.commit()
            await ctx.send(f"<{EMOJIS['CHECK']}> Successfully removed {emoji} from the list of emojis to add in this channel!", delete_after=3)
        else:
            await ctx.send(f"<{EMOJIS['XMARK']}> Couldn't find {emoji} in the list of emojis to add in this channel!")

        async for msg in ctx.history(limit=None):
            await msg.remove_reaction(emoji, member)

    @commands.command(help="Set a channel as a poll channel telling Melon to scan messages for emojis and add them as reactions to make it easier for users to vote!")
    @commands.has_permissions(manage_channels=True)
    async def togglepoll(self, ctx: commands.Context):
        channel = session.query(Channel).filter(Channel.channel_id == ctx.channel.id).first()

        if not channel:
            channel = Channel(channel_id=ctx.channel.id, poll_channel=True)
            session.add(channel)
        else:
            channel.poll_channel = not channel.poll_channel

        session.commit()

        if channel.poll_channel:
            await ctx.send(f"<{EMOJIS['CHECK']}> Successfully registered channel as a poll channel!", delete_after=3)
        else:
            await ctx.send(f"<{EMOJIS['CHECK']}> Successfully removed polling feature from this channel!", delete_after=3)
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(PollCog(bot))
