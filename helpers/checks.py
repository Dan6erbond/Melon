import discord
from discord.ext import commands

from const import AUTHORIZED_USERS


def is_pinned(m: discord.Message):
    return not m.pinned


def is_authorized(ctx: commands.Context):
    return ctx.author.id in AUTHORIZED_USERS
