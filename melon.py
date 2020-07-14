
import configparser
import re
import traceback
from datetime import datetime

import discord
from discord.ext import commands


class Melon(commands.Bot):
    def __init__(self, **options):
        super().__init__(
            "!",
            description="Dan6erbond's take on Discord utility bots with Melons.",
            **options)

    async def on_ready(self):
        print(f'{self.user.name} is running.')

    async def send_error(self, message: str):
        await self.get_channel(556732041752739840).send(message)

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, discord.ext.commands.errors.CommandNotFound):
            pass
        else:
            await ctx.message.channel.send(error)
            print(traceback.format_exc())

    async def handle_poll(self, message: discord.Message):
        if message.author.bot:
            return

        emotes = re.findall(r"<:\w+:\d+>", message.content)
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
            with open("configs/channels.json", encoding="utf8") as f:
                channels = json.loads(f.read())
                for channel in channels:
                    if channel["id"] == message.channel.id:
                        if "defaultemojis" in channel and len(channel["defaultemojis"]) > 0:
                            for e in channel["defaultemojis"]:
                                await message.add_reaction(e)
                        else:
                            await message.add_reaction("👍")
                            await message.add_reaction("👎")
                        break

    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
        try:
            msg = await bot.get_channel(int(payload.data["channel_id"])).fetch_message(payload.message_id)
        except Exception as e:
            await self.send_error(e)

        if msg:
            with open("configs/channels.json", encoding="utf8") as f:
                channels = json.loads(f.read())

                for channel in channels:
                    if channel["id"] == msg.channel.id:
                        if "poll" in channel and channel["poll"]:
                            await handle_poll(msg)
                        break


extensions = ["cogs.util_cog"]

if __name__ == "__main__":
    bot = Melon()

    config = configparser.ConfigParser()
    config.read("discord.ini")

    for extension in extensions:
        bot.load_extension(extension)
        print(f"{extension} loaded.")

    bot.run(config["MELON"]["token"])
