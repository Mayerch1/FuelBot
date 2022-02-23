import os
import discord
import logging
import traceback
import sys

from pathlib import Path


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
    
    if isinstance(error, discord.NotFound):
        log.warning('interaction timed out (not found)')
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


def main():
    for filename in os.listdir(Path(__file__).parent / 'cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')

    bot.run(token)


if __name__ == '__main__':
    main()