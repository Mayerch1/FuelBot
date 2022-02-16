import os
import interactions

import FuelModule
import HelpModule
import ServerCountPost


token = os.getenv('BOT_TOKEN')
intents = interactions.Intents.GUILDS

bot = interactions.Client(token=token, intents=intents)
fm = FuelModule.FuelModule(bot)
help = HelpModule.HelpModule(bot)
serverCount = ServerCountPost.ServerCountPost(bot)




###########
# Eevents 
###########
@bot.component("help_direct_feedback")
async def help_direct_feedback(ctx):
    await help.send_feedback(ctx)


@bot.component("help_navigation")
async def help_change_page(ctx, page):
    await help.send_help_page(ctx, page[0])


@bot.component('help_tos')
async def help_send_tos(ctx):
    await help.help_send_tos(ctx)


@bot.component('help_privacy')
async def help_send_privacy(ctx):
    await help.help_send_privacy(ctx)

############
# Modals
############

@bot.modal("modal_direct_feedback")
async def mod_direct_feedback(ctx, feedback: str):
    await help.process_feedback(ctx, feedback)


@bot.modal("fuel_length_form")
async def modal_response(ctx, race_len, lap_time, fuel_usage, reserve_laps):
    reserve_laps = reserve_laps or '3'
    await fm.handle_fuel_calculation(ctx, race_len, None, lap_time, fuel_usage, reserve_laps)

@bot.modal("fuel_laps_form")
async def modal_response(ctx, race_laps, lap_time, fuel_usage, reserve_laps='3'):
    reserve_laps = reserve_laps or '3'
    await fm.handle_fuel_calculation(ctx, None, race_laps, lap_time, fuel_usage, reserve_laps)

#############
# Commands
############


@bot.command(
    name='help',
    description='Show the help page for this bot',
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name='page',
            description='select a page',
            required=False,
            choices=[
                interactions.Choice(
                    name='overview',
                    value='overview'
                ),
                interactions.Choice(
                    name='parameters',
                    value='parameters'
                )
            ]
        )
    ]
)
async def help_cmd(ctx, page:str='overview'):
    await help.send_help_page(ctx, page)


@bot.command(
    name='fuel',
    description='Calculate fuel usage for a race',
    options=[
        interactions.Option(
            name='time',
            description='Calculate based on max session time',
            type=interactions.OptionType.SUB_COMMAND
        ),
        interactions.Option(
            name='laps',
            description='Calculate based on max laps',
            type=interactions.OptionType.SUB_COMMAND
        )
    ]
)
async def fuel_time(ctx: interactions.CommandContext, sub_command: str):

    if sub_command == 'time':
        mod_id = 'fuel_length_form'
        duration = interactions.TextInput(
            style=interactions.TextStyleType.SHORT,
            label='Race Length (hh:mm or minutes)',
            custom_id='txt_race_time',
            min_length=1,
            max_length=10
        )
    else:
        mod_id = 'fuel_laps_form'
        duration = interactions.TextInput(
            style=interactions.TextStyleType.SHORT,
            label='Race Laps',
            custom_id='txt_race_laps',
            min_length=1,
            max_length=10
        )

    modal = interactions.Modal(
        title='Fuel Calculations',
        custom_id=mod_id,
        components=[
            duration,
            interactions.TextInput(
                style=interactions.TextStyleType.SHORT,
                label='Laptime (m:ss.ff or seconds)',
                custom_id='txt_lap_time',
                min_length=1,
                max_length=10
            ),
            interactions.TextInput(
                style=interactions.TextStyleType.SHORT,
                label='Fuel Usage (ltrs/lap)',
                custom_id='txt_fuel_usage',
                min_length=1,
                max_length=10
            ),
            interactions.TextInput(
                style=interactions.TextStyleType.SHORT,
                label='Reserve Laps for safe (optional)',
                custom_id='txt_reserve_laps',
                required=False,
                placeholder='3',
                min_length=1,
                max_length=5
            )
        ]
    )
    await ctx.popup(modal)



@bot.event
async def on_ready():
    # debug log
    print('Interaction as')
    print(bot.me.name)
    print(bot.me.id)
    print('-----------')

    serverCount.start_loop()


def main():
    bot.start()


if __name__ == '__main__':
    main()