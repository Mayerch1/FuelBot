import os
import discord
import logging
import traceback
import sys

from pathlib import Path
from discord.ext.help import Help, HelpElement, HelpPage
from discord.ext.servercount import ServerCount

FEEDBACK_CHANNEL = 890973072662884383
FEEDBACK_MENTION = 872107119988588566


logging.basicConfig(level=logging.INFO) # general 3rd party

handler = logging.FileHandler(filename='./logs/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

dc_logger = logging.getLogger('discord')
dc_logger.setLevel(logging.WARNING) # discord lib
log = logging.getLogger('FuelBot')
log.setLevel(logging.DEBUG) # own code

dc_logger.addHandler(handler)
log.addHandler(handler)



token: str = os.getenv('BOT_TOKEN')
intents = discord.Intents.none()
#intents.guilds = True

bot: discord.AutoShardedBot = discord.AutoShardedBot(intents=intents)


# ###########
# Methods
# ###########
async def log_exception(ctx: discord.ApplicationContext, error: Exception):
    if isinstance(error, discord.ApplicationCommandInvokeError) and isinstance(error.original, discord.NotFound):
        log.warning(f'interaction timed out ({error.original.text})')
    else:
        t = (type(error), error, error.__traceback__)
        log.error(''.join(traceback.format_exception(*t)))


# ###########
# Commands
# ###########



# ###########
# Events
# ###########

@bot.event
async def on_ready():
    log.info('Logged in as')
    log.info(bot.user)
    log.info(bot.user.id)
    log.info('----------------')
    config_help()


@bot.event
async def on_shard_connect(shard_id):
    log.debug(f'shard {shard_id} connected')


@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: Exception):
    await log_exception(ctx, error)


@bot.event
async def on_error(event_method, *args, **kwargs):
    exc_info = sys.exc_info()
    log.critical('non-application error occurred', exc_info=exc_info)


# #############
# # Commands
# ############

def set_tokens():
    ServerCount.init(bot, 'fuelBot (https://github.com/Mayerch1/FuelBot)')
    ServerCount.set_token_dir('tokens')


def config_help():

    custom_footer = 'If you like this bot, you can leave a vote at [top.gg](https://top.gg/bot/890731736252686337).\n'\
                                'If you find a bug contact us on [Github](https://github.com/Mayerch1/FuelBot) or join the support server.'

    Help.init_help(bot, auto_detect_commands=True)

    Help.set_default_footer(custom_footer)
    Help.set_feedback(FEEDBACK_CHANNEL, FEEDBACK_MENTION)
    Help.invite_permissions(
        discord.Permissions(attach_files=True)
    )
    Help.support_invite('https://discord.gg/Xpyb9DX3D6')
    Help.set_tos_file('legal/tos.md')
    Help.set_privacy_file('legal/privacy.md')
    Help.set_github_url('https://github.com/Mayerch1/FuelBot')


def main():
    for filename in os.listdir(Path(__file__).parent / 'cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')

    bot.load_extension('discord.ext.help.help')
    bot.load_extension('discord.ext.servercount.servercount')

    set_tokens()
    bot.run(token)


if __name__ == '__main__':
    main()