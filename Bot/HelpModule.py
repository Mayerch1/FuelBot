import asyncio

import discord
from discord.ext import commands, tasks
from discord_slash import cog_ext, SlashContext, ComponentContext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils import manage_components
from discord_slash.model import SlashCommandOptionType, ButtonStyle

FEEDBACK_CHANNEL = 890973072662884383
FEEDBACK_MENTION = 872107119988588566

class HelpModule(commands.Cog):
                
    def __init__(self, client):
        self.client = client
    
    # =====================
    # helper methods
    # =====================
    
    async def send_feedback(self, ctx):
        """give the user the option to send some quick
        feedback to the devs
        """

        dm = await ctx.author.create_dm()

        try:
            dm_test = await dm.send('*Direct Feedback*')
            channel = dm
        except discord.errors.Forbidden:
            dm_test = None
            channel = ctx.channel


        def msg_check(msg):
            return msg.author.id == ctx.author.id and msg.channel.id == channel.id

        q = await channel.send('If you want to send some feedback, '\
                        'just type a short sentence into the chat.\n'\
                        'Your feedback will be used to improve the bot')

        try:
            feedback = await self.client.wait_for('message', check=msg_check, timeout=5*60)
        except asyncio.exceptions.TimeoutError:
            # abort the deletion
            await q.delete()
            await dm_test.edit(content='*Feedback Timeout*: You didn\'t enter your feedback fast enough.\nRe-invoke the command if you want to try again.') if dm_test else None
            return


        feedback_ch = self.client.get_channel(FEEDBACK_CHANNEL)

        if feedback_ch:
            feedback_str = f'<@&{FEEDBACK_MENTION}> New Feedback:\n'
            feedback_str += f'Author: {ctx.author.mention} ({ctx.author.name})\n\n'

            content = feedback.clean_content.replace('\n', '\n> ') # make sure multiline doesn't break quote style
            feedback_str += f'> {content}\n'
            await feedback_ch.send(feedback_str)
            await channel.send('Thanks for giving feedback to improve the bot')
        else:
            await channel.send('There was an issue when saving your feedback.\n'\
                            'Please report this bug on the *support server* or on *GitHub*')


    async def send_help_page(self, ctx, page):
        
        page_list = ['overview', 'parameters']
        
        if page not in page_list:
            print('ERROR: unknown help page')
            await ctx.send(f'Error, unknown help page `{page}`')
            return
        
        def get_overview_eb():
            embed = discord.Embed(title='FuelBot Help', description='Calculate your race fuel usage')

            embed.add_field(name='/help', value='show this message', inline=False)
            embed.add_field(name='/fuel time', value='use this for time limited races', inline=False)
            embed.add_field(name='/fuel laps', value='use this for lap limited races', inline=False)

            embed.add_field(name='\u200b', 
                            inline=False,
                            value='If you like this bot, you can leave a vote at [top.gg](https://top.gg/bot/890731736252686337).\n'\
                                'If you find a bug contact us on [Github](https://github.com/Mayerch1/FuelBot) or join the support server.')
            return embed


        def get_parameters_eb():

            eb = discord.Embed(title='FuelBot Parameter Help', description='\u200b')
            
            eb.add_field(name='length', value='length of race, format is `hh:mm` or `mm` (only for `/fuel time`)', inline=False)
            eb.add_field(name='laps', value='total laps of the race (only for `/fuel laps`)', inline=False)
            eb.add_field(name='\u200b', value='\u200b', inline=False)
            eb.add_field(name='laptime', value='expected laptime, format is `mm:ss.fff`, `mm:ss` or `ss.ff`', inline=False)
            eb.add_field(name='fuel_usage', value='average fuel consumption per lap, unit is liter/lap', inline=False)
            eb.add_field(name='reserve_laps', value='reserve laps planned for `Safe Fuel` recommendation', inline=False)

            eb.set_footer(text='If you find a bug or want to give feedback, join the support server.')

            return eb

  
    
        def get_help_components(current_page='overview'):
            
            buttons = [
                manage_components.create_button(
                    style=ButtonStyle.URL,
                    label='Invite Me',
                    url='https://discord.com/api/oauth2/authorize?client_id=890731736252686337&permissions=0&scope=bot%20applications.commands'
                ),
                manage_components.create_button(
                    style=ButtonStyle.URL,
                    label='Support Server',
                    url='https://discord.gg/Xpyb9DX3D6'
                ),
                manage_components.create_button(
                    style=ButtonStyle.gray,
                    label='Direct Feedback',
                    custom_id='help_direct_feedback'
                )
            ]
            row_1 = manage_components.create_actionrow(*buttons)
            
            
            options = [
                manage_components.create_select_option(
                    label='Overview Page',
                    description='List all available commands',
                    value='overview',
                    emoji='🌐',
                    default=(current_page=='overview')
                ),
                manage_components.create_select_option(
                    label='Parameters Page',
                    description='Explain the different command parameters',
                    value='parameters',
                    emoji='✏️',
                    default=(current_page=='parameters')
                ),
            ]
            help_selection = (
                manage_components.create_select(
                    custom_id='help_navigation',
                    placeholder='Please select a category',
                    min_values=1,
                    max_values=1,
                    options=options
                )
            )
            row_2 = manage_components.create_actionrow(help_selection)
            return [row_1, row_2]


        if page == 'overview':
            eb = get_overview_eb()
            comps = get_help_components(page)
        elif page == 'parameters':
            eb = get_parameters_eb()
            comps = get_help_components(page)

        
        if isinstance(ctx, ComponentContext):
            await ctx.edit_origin(embed=eb, components=comps)
        else:
            # this is a reaction to a command
            # permissions to respond are guaranteed
            # however, components might fail with an exception
            msg = await ctx.send(embed=eb, components=comps)

    # =====================
    # events functions
    # =====================
    
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('HelpModule loaded')
        
        
    @commands.Cog.listener()
    async def on_component(self, ctx: ComponentContext):

        if ctx.custom_id == 'help_direct_feedback':
            await ctx.defer(edit_origin=True)
            await self.send_feedback(ctx)
        
        elif ctx.custom_id == 'help_navigation':
            sel_id = ctx.selected_options[0]
            await self.send_help_page(ctx, sel_id)
        
        
        
    # =====================
    # commands functions
    # =====================
    
    @cog_ext.cog_slash(name='help', description='Show the help page for this bot',
                    options=[
                        create_option(
                            name='page',
                            description='choose the subpage to display',
                            required=False,
                            option_type=SlashCommandOptionType.STRING,
                            choices=[
                                create_choice(
                                    name='overview',
                                    value='overview'
                                ),
                                create_choice(
                                    name='parameters',
                                    value='parameters'
                                )
                            ]
                        )
                    ])
    async def get_help(self, ctx, page='overview'):
        await self.send_help_page(ctx, page)


def setup(client):
    client.add_cog(HelpModule(client))