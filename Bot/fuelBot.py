import os
import discord
from discord.ext import commands
from discord_slash import SlashContext, SlashCommand
from discord_slash.context import MenuContext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.model import SlashCommandOptionType, ContextMenuType


token = os.getenv('BOT_TOKEN')

intents = discord.Intents.none()
intents.guilds = True
intents.guild_messages = True

client = commands.Bot(command_prefix='/', intents=intents, description='Calculate race fuel usage', help_command=None)
slash = SlashCommand(client, sync_commands=True)



@client.event
async def on_slash_command_error(ctx, error):

    if isinstance(error, discord.ext.commands.errors.MissingPermissions):
        await ctx.send('You do not have permission to execute this command')
    elif isinstance(error, discord.ext.commands.errors.NoPrivateMessage):
        await ctx.send('This command is only to be used on servers')
    else:
        print(error)
        raise error


@slash.slash(name='help', description='show a help message')
async def get_help(ctx):

    embed = discord.Embed(title='FuelBot Help', description='Calculate your race fuel usage')

    embed.add_field(name='/help', value='show this message', inline=False)
    embed.add_field(name='/fuel time', value='use this for time limited races', inline=False)
    embed.add_field(name='/fuel laps', value='use this for lap limited races', inline=False)

    embed.add_field(name='\u200b', value='If you like this bot, you can leave a vote at [top.gg](https://top.gg/bot/734829435844558999)', inline=False)

    # direct slash response is guaranteed to have permissions
    await ctx.send(embed=embed)


@client.event
async def on_ready():
    # debug log
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('-----------')
    await client.change_presence(activity=discord.Game(name='/fuel'))




def main():
    client.load_extension(f'FuelModule')
    client.load_extension(f'ServerCountPost')
    client.run(token)


if __name__ == '__main__':
    main()