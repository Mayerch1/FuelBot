import asyncio
import logging
import discord

from typing import Union

FEEDBACK_CHANNEL = 890973072662884383
FEEDBACK_MENTION = 872107119988588566

log = logging.getLogger('FuelBot')

class FeedbackModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        # override args
        kwargs['title'] = 'Direct Feedback'

        # pop custom args
        self.callback = kwargs['callback']
        del kwargs['callback']
        
        super().__init__(*args, **kwargs)

        self.add_item(
            discord.ui.InputText(
                label='Please enter your feedback for this bot',
                min_length=3,
                max_length=1500,
                style=discord.InputTextStyle.paragraph
            )
        )

class HelpModule(discord.Cog):

    tos_notice = open('legal/tos.md').read()
    privacy_notice = open('legal/privacy.md').read()
                
    def __init__(self, client):
        self.client: discord.AutoShardedBot = client

    # =====================
    # helper methods
    # =====================

    async def help_send_tos(self, interaction: discord.Interaction):
        await interaction.response.send_message(HelpModule.tos_notice, ephemeral=True)
            
    
    async def help_send_privacy(self, interaction: discord.Interaction):
        await interaction.response.send_message(HelpModule.privacy_notice, ephemeral=True)

    
    async def send_feedback(self, interaction: discord.Interaction):
        """give the user the option to send some quick
        feedback to the devs
        """
        feedback = FeedbackModal(callback=self.process_feedback)
        await interaction.response.send_modal(feedback)


    async def process_feedback(self, interaction: discord.Interaction):
        def _error_components():
            view = discord.ui.View(timeout=None)
            
            buttons = [
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label='Support Server',
                    url='https://discord.gg/Xpyb9DX3D6'
                ),
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label='Github Issue',
                    url='https://github.com/Mayerch1/FuelBot/issues'
                )
            ]
            for b in buttons:
                view.add_item(b)
            return view


        try:
            ch = await self.client.fetch_channel(FEEDBACK_CHANNEL)
        except (discord.errors.Forbidden, discord.errors.NotFound) as ex:
            await interaction.response.send_message(
                'There was an issue while saving your feedback.\n'\
                'Please report this bug on the *support server* or on *GitHub*', 
                view=_error_components(), 
                ephemeral=True
            )
            log.error('failed to fetch feedback channel', exc_info=ex)
            raise ex

        feedback = interaction.data['components'][0]['components'][0]['value']
        feedback_str = f'<@&{FEEDBACK_MENTION}> New Feedback:\n'
        feedback_str += f'Author: {interaction.user.mention} ({interaction.user.name}#{interaction.user.discriminator})\n\n'

        content = feedback.replace('\n', '\n> ') # make sure multiline doesn't break quote style
        feedback_str += f'> {content}\n'

        try:
            await ch.send(feedback_str)
        except discord.errors.Forbidden as ex:
            await interaction.response.send_message(
                'There was an issue while saving your feedback.\n'\
                'Please report this bug on the *support server* or on *GitHub*', 
                view=_error_components(), 
                ephemeral=True
            )
            log.error('failed to send message into feedback channel', exc_info=ex)
            raise ex

        await interaction.response.send_message('Thanks for giving feedback to improve the bot', ephemeral=True)


    async def send_help_page(self, ctx: discord.ApplicationContext, page: str='overview'):

        page_list = ['overview', 'parameters']
        
        if page not in page_list:
            log.error('unknown help page')
            await ctx.send(f'Error, unknown help page `{page}`')
            return
        

        def get_overview_eb():
            embed = discord.Embed(
                title='FuelBot Help', 
                description='Calculate your race fuel usage'
            )

            embed.add_field(name='/help', value='show this message', inline=False)
            embed.add_field(name='/fuel time', value='use this for time limited races', inline=False)
            embed.add_field(name='/fuel laps', value='use this for lap limited races', inline=False)
            embed.add_field(name='\u200b', 
                            inline=False,
                            value='If you like this bot, you can leave a vote at [top.gg](https://top.gg/bot/890731736252686337).\n'\
                                'If you find a bug contact us on [Github](https://github.com/Mayerch1/FuelBot) or join the support server.')
            return embed


        def get_parameters_eb():
            eb = discord.Embed(
                title='FuelBot Parameter Help', 
                description='\u200b'
            )
            eb.add_field(name='length', value='length of race, format is `hh:mm` or `mm` (only for `/fuel time`)', inline=False)
            eb.add_field(name='laps', value='total laps of the race (only for `/fuel laps`)', inline=False)
            eb.add_field(name='\u200b', value='\u200b', inline=False)
            eb.add_field(name='laptime', value='expected laptime, format is `mm:ss.fff`, `mm:ss` or `ss.ff`', inline=False)
            eb.add_field(name='fuel_usage', value='average fuel consumption per lap, unit is liter/lap', inline=False)
            eb.add_field(name='reserve_laps', value='reserve laps planned for `Safe Fuel` recommendation', inline=False)
            eb.set_footer(text='If you find a bug or want to give feedback, join the support server.')
            return eb

    
        def get_help_view(current_page='overview'):

            view = discord.ui.View(timeout=None)
      
            components = [
                # === ROW 0 ===
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label='Invite Me',
                    url='https://discord.com/api/oauth2/authorize?client_id=890731736252686337&permissions=0&scope=bot%20applications.commands',
                    row=0
                ),
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label='Support Server',
                    url='https://discord.gg/Xpyb9DX3D6',
                    row=0
                ),
                discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label='Direct Feedback',
                    custom_id='help_direct_feedback',
                    row=0
                ),

                # === ROW 1 ===
                discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label='ToS',
                    custom_id='help_tos',
                    row=1
                ),
                discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label='Privacy',
                    custom_id='help_privacy',
                    row=1
                )
            ]

            # # === ROW 3 ===
            # options = [
            #     discord.SelectOption(
            #         label='Overview Page',
            #         description='List all available commands',
            #         value='overview',
            #         emoji='🌐', # :globe_with_meridians:
            #         default=(current_page=='overview')
            #     ),
            #     discord.SelectOption(
            #         label='Parameters Page',
            #         description='Explain the different command parameters',
            #         value='parameters',
            #         emoji='✏️', # :pencil2:
            #         default=(current_page=='parameters')
            #     ),
            # ]
            # components.append(discord.ui.Select(
            #         options=options,
            #         placeholder='Please select a category',
            #         min_values=1,
            #         max_values=1,
            #         row=3,
            #         custom_id='help_navigation'
            #     )
            # )
            for c in components:
                view.add_item(c)

            return view


        if page == 'overview':
            eb = get_overview_eb()
            comps = get_help_view(page)
        elif page == 'parameters':
            eb = get_parameters_eb()
            comps = get_help_view(page)


        # this is a reaction to a command
        # permissions to respond are guaranteed
        await ctx.respond(embeds=[eb], view=comps)
        comps.stop() # handle stuff ourselves using raw events instead
        

    # ###########
    # Commands
    # ###########

    @discord.slash_command(name='help', description='Show the help page for this bot')
    async def help(self, 
                    ctx: discord.ApplicationContext,
                    #page: discord.Option(str, "select a page", default='overview', choices=['overview', 'parameters'])
                    ):
        await self.send_help_page(ctx)#, page)


    # =====================
    # events functions
    # =====================

    @discord.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if 'custom_id' not in interaction.data:
            # we only care about buttons/selects here
            return

        custom_id = interaction.data['custom_id']

        if custom_id == 'help_tos':
            await self.help_send_tos(interaction)
        elif custom_id == 'help_privacy':
            await self.help_send_privacy(interaction)
        elif custom_id == 'help_direct_feedback':
            await self.send_feedback(interaction)
        # elif custom_id == 'help_navigation':
        #     page = interaction.data['values'][0] # min select is 1
        #     await self.send_help_page(interaction, page)
        


    @discord.Cog.listener()
    async def on_ready(self):
        log.info('HelpModule loaded')
        

    # =====================
    # commands functions
    # =====================

def setup(client):
    client.add_cog(HelpModule(client))