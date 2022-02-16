import asyncio
import interactions

FEEDBACK_CHANNEL = 890973072662884383
FEEDBACK_MENTION = 872107119988588566

class HelpModule():

    tos_notice = open('legal/tos.md').read()
    privacy_notice = open('legal/privacy.md').read()
                
    def __init__(self, client):
        self.client: interactions.Client = client
    
    # =====================
    # helper methods
    # =====================

    async def help_send_tos(self, ctx):
        await ctx.send(HelpModule.tos_notice, ephemeral=True)
            

    async def help_send_privacy(self, ctx):
        await ctx.send(HelpModule.privacy_notice, ephemeral=True)


    
    async def send_feedback(self, ctx):
        """give the user the option to send some quick
        feedback to the devs
        """

        modal = interactions.Modal(
            title='Direct Feedback',
            custom_id='modal_direct_feedback',
            components=[
                interactions.TextInput(
                    style=interactions.TextStyleType.PARAGRAPH,
                    label='Please enter your feedback for this bot',
                    custom_id='txt_lap_time',
                    max_length=1500
                )
            ]
        )
        await ctx.popup(modal)


    async def process_feedback(self, ctx, feedback: str):
        def _error_components():
            buttons = [
                interactions.Button(
                    style=interactions.ButtonStyle.LINK,
                    label='Support Server',
                    url='https://discord.gg/Xpyb9DX3D6'
                ),
                interactions.Button(
                    style=interactions.ButtonStyle.LINK,
                    label='Github Issue',
                    url='https://github.com/Mayerch1/FuelBot/issues'
                )
            ]
            return interactions.ActionRow(components=buttons)


        try:
            ch = await self.client._http.get_channel(channel_id=FEEDBACK_CHANNEL)
        except ValueError:
            await ctx.send('There was an issue when saving your feedback.\n'\
                        'Please report this bug on the *support server* or on *GitHub*', components=_error_components(), ephemeral=True)
            return

        ch = interactions.Channel(**ch)

        feedback_str = f'<@&{FEEDBACK_MENTION}> New Feedback:\n'
        feedback_str += f'Author: {ctx.author.mention} ({ctx.author.user.username})\n\n'

        content = feedback.replace('\n', '\n> ') # make sure multiline doesn't break quote style
        feedback_str += f'> {content}\n'

        await self.client._http.send_message(
            channel_id=ch.id,
            content=feedback_str
        )
        await ctx.send('Thanks for giving feedback to improve the bot', ephemeral=True)



    async def send_help_page(self, ctx, page):
        
        page_list = ['overview', 'parameters']
        
        if page not in page_list:
            print('ERROR: unknown help page')
            await ctx.send(f'Error, unknown help page `{page}`')
            return
        
        def get_overview_eb():
            embed = interactions.Embed(
                title='FuelBot Help', 
                description='Calculate your race fuel usage',
                fields=[
                    interactions.EmbedField(name='/help', value='show this message', inline=False),
                    interactions.EmbedField(name='/fuel time', value='use this for time limited races', inline=False),
                    interactions.EmbedField(name='/fuel laps', value='use this for lap limited races', inline=False),
                    interactions.EmbedField(name='\u200b', 
                            inline=False,
                            value='If you like this bot, you can leave a vote at [top.gg](https://top.gg/bot/890731736252686337).\n'\
                                'If you find a bug contact us on [Github](https://github.com/Mayerch1/FuelBot) or join the support server.'),
                ])
            return embed


        def get_parameters_eb():
            eb = interactions.Embed(
                title='FuelBot Parameter Help', 
                description='\u200b',
                fields=[
                    interactions.EmbedField(name='length', value='length of race, format is `hh:mm` or `mm` (only for `/fuel time`)', inline=False),
                    interactions.EmbedField(name='laps', value='total laps of the race (only for `/fuel laps`)', inline=False),
                    interactions.EmbedField(name='\u200b', value='\u200b', inline=False),
                    interactions.EmbedField(name='laptime', value='expected laptime, format is `mm:ss.fff`, `mm:ss` or `ss.ff`', inline=False),
                    interactions.EmbedField(name='fuel_usage', value='average fuel consumption per lap, unit is liter/lap', inline=False),
                    interactions.EmbedField(name='reserve_laps', value='reserve laps planned for `Safe Fuel` recommendation', inline=False),
                ],
                footer=interactions.EmbedFooter(text='If you find a bug or want to give feedback, join the support server.')
            )
            return eb

  
    
        def get_help_components(current_page='overview'):
            buttons = [
                interactions.Button(
                    style=interactions.ButtonStyle.LINK,
                    label='Invite Me',
                    url='https://discord.com/api/oauth2/authorize?client_id=890731736252686337&permissions=0&scope=bot%20applications.commands'
                ),
                interactions.Button(
                    style=interactions.ButtonStyle.LINK,
                    label='Support Server',
                    url='https://discord.gg/Xpyb9DX3D6'
                ),
                interactions.Button(
                    style=interactions.ButtonStyle.SECONDARY,
                    label='Direct Feedback',
                    custom_id='help_direct_feedback'
                )
            ]
            row_1 = interactions.ActionRow(components=buttons)

            buttons = [
                interactions.Button(
                    style=interactions.ButtonStyle.SECONDARY,
                    label='ToS',
                    custom_id='help_tos'
                ),
                interactions.Button(
                    style=interactions.ButtonStyle.SECONDARY,
                    label='Privacy',
                    custom_id='help_privacy'
                )
            ]
            row_2 = interactions.ActionRow(components=buttons)
            

            options = [
                interactions.SelectOption(
                    label='Overview Page',
                    description='List all available commands',
                    value='overview',
                    #emoji=interactions.Emoji(name=':globe_with_meridians:'),
                    default=(current_page=='overview')
                ),
                interactions.SelectOption(
                    label='Parameters Page',
                    description='Explain the different command parameters',
                    value='parameters',
                    #emoji=interactions.Emoji(name=':pencil2:'),
                    default=(current_page=='parameters')
                ),
            ]
            help_selection = interactions.SelectMenu(
                    custom_id='help_navigation',
                    options=options,
                    placeholder='Please select a category',
                    min_values=1,
                    max_values=1,
            )

            row_3 = interactions.ActionRow(components=[help_selection])
            return [row_1, row_2, row_3]


        if page == 'overview':
            eb = get_overview_eb()
            comps = get_help_components(page)
        elif page == 'parameters':
            eb = get_parameters_eb()
            comps = get_help_components(page)

        
        if isinstance(ctx, interactions.ComponentContext):
            await ctx.edit(embeds=eb, components=comps)
        else:
            # this is a reaction to a command
            # permissions to respond are guaranteed
            # however, components might fail with an exception
            msg = await ctx.send(embeds=eb, components=comps)


    # =====================
    # events functions
    # =====================
        
        
        
    # =====================
    # commands functions
    # =====================
