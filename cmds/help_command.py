from discord.ext import commands


class HelpCommand(commands.HelpCommand):

    def __init__(self, **options):
        super().__init__(**options)

    async def send_bot_help(self, mapping):
        print("Bot help:", mapping)
        return await super().send_bot_help(mapping)

    async def send_cog_help(self, cog):
        print("Cog help:", cog)
        return await super().send_cog_help(cog)

    async def send_group_help(self, group):
        print("Group help:", group)
        return await super().send_group_help(group)

    async def send_command_help(self, command):
        print("Command help:", command)
        return await super().send_command_help(command)

    async def command_not_found(self, string):
        print("Command not found:", string)
        return await super().command_not_found(string)

    async def subcommand_not_found(self, command, string):
        print("Subcommand not found:", command, string)
        return await super().subcommand_not_found(command, string)

    async def on_help_command_error(self, ctx, error):
        print("Help command error:", ctx, error)
        return await super().on_help_command_error(ctx, error)

    async def send_error_message(self, error):
        print("Error message:", error)
        return await super().send_error_message(error)
