import math
import regex
import logging

from datetime import timedelta
import discord

log = logging.getLogger('FuelBot')



class LapData:
    def __init__(self, raceTime, raceLaps, lapTime, fuelUsage, reserveLaps):
        self.raceTime = raceTime
        self.raceLaps = raceLaps
        self.lapTime = lapTime
        self.fuelUsage = fuelUsage
        self.reserveLaps = reserveLaps
        
        self.fuel = None
        self.saveFuel = None
        self.fpm = None


class FuelCalculator():

    @staticmethod
    def calculate(raceLaps: int, raceTime: str, lapTime: str, fuel_usage: float, reserve_laps: int) -> LapData:

        data  =LapData(raceTime=raceTime, raceLaps=raceLaps, lapTime=lapTime, fuelUsage=float(fuel_usage), reserveLaps=reserve_laps)
        FuelCalculator._setFuelUsage(data)
        return data


    @staticmethod
    def _setFuelUsage(data: LapData):
        data.fpm = data.fuelUsage / data.lapTime.total_seconds() * 60
        data.fuel = data.raceLaps * data.fuelUsage
        data.saveFuel = data.fuel + (data.reserveLaps + data.fuelUsage)



class FuelModal(discord.ui.Modal):


    ##################
    # Calc Methods
    #################

    def error_embed(self, title, reason):
        eb = discord.Embed(title=title, description=reason, color=0xff0000)
        return eb


    def parseRaceLen(self, length):
        """parse the inputted race duration
           priority for parsing is:
                1. hh:mm
                2. h:mm
                3. [minutes]
                4. return 0 seconds

        Args:
            length (str): length string

        Returns:
            timedelta: race length
        """
        
        timestmap = r'^(\d{1,2}:)?\d{1,2}$'
        re_stamp = regex.compile(timestmap)
        
        re_minutes = regex.compile(r'^\d+$')
        
        delta = timedelta(seconds=0)
        if re_stamp.match(length):
            # match hh:mm aswell  as [minutes]
            split = length.split(':')
            
            if len(split) == 1:
                delta = timedelta(minutes=int(split[0]))
            elif len(split) == 2:
                delta += timedelta(hours=int(split[0]))
                delta += timedelta(minutes=int(split[1]))
        else:
            try:
                mins = int(length)
            except ValueError:
                delta = timedelta(minutes=0)
            else:
                delta += timedelta(minutes=int(length))

        return delta


    def parseLapTime(self, time):
        """parse inputted fuel usage into ms
                1. mm:ss.ffff
                    - mm{0,2}, ss{1,2}, fff{0,3}
                2. [total seconds]
                3. return 0 seconds

        Args:
            time (str): laptime string

        Returns:
            timedelta: laptime
        """
        
        def parse_ms(ms_str):
            ms = 0
            
            if len(ms_str) == 1:
                ms = int(ms_str)*100
            elif len(ms_str) == 2:
                ms = int(ms_str)*10
            elif len(ms_str) == 3:
                ms = int(ms_str)
                
            return ms
        
        timestmap = r'^(\d{1,2}:)?\d{1,2}(.\d{1,3})?$'
        re_stamp = regex.compile(timestmap)
        
        re_seconds = regex.compile(r'^\d+$')
        
        delta = timedelta(seconds=0)
        if re_stamp.match(time):
            # match mm:ss.ffff
            
            if ':' in time and '.' not in time:
                split = time.split(':')
                delta += timedelta(minutes=int(split[0]))
                delta += timedelta(seconds=int(split[1]))
            elif ':' in time and '.' in time:
                split = time.split(':')
                delta += timedelta(minutes=int(split[0]))

                split = split[1].split('.')
                delta += timedelta(seconds=int(split[0]))
                delta += timedelta(microseconds=parse_ms(split[1])*1000)
            elif '.' in time:
                split = time.split('.')
                delta = timedelta(seconds=int(split[0]))
                delta += timedelta(microseconds=parse_ms(split[1])*1000)
            else:
                delta =  timedelta(seconds=int(time))


        return delta


    async def getFuelData(self, interaction: discord.Interaction) -> LapData:
        
        try:
            reserve_laps = int(self.children[3].value)
        except ValueError:
            await interaction.response.send_message(embeds=[self.error_embed('Invalid Parameter', 'The `reserve_laps` must be an integer (e.g. `3`)')])
            return None
            
        try:
            fuel_usage = float(self.children[2].value)
        except ValueError:
            await interaction.response.send_message(embeds=[self.error_embed('Invalid Parameter', 'The `fuel_usage` must be a decimal number (e.g. `3.1`)')])
            return

        lapTime = self.parseLapTime(self.children[1].value)
        if lapTime <= timedelta(minutes=0):
            await interaction.response.send_message(embeds=[self.error_embed('Invalid Parameter', 'The `laptime` must be greater than 0. Check for the correct format of `mm:ss.fff`')])
            return None
        

        if self.children[0].custom_id == 'modal_field_racelen_laps':
            try:
                raceLaps = int(self.children[0].value)
            except ValueError:
                await interaction.response.send_message(embeds=[self.error_embed('Invalid Parameter', 'The `race_laps` must be an integer (e.g. `3`)')])
                return None
            if raceLaps <= 0:
                await interaction.response.send_message(embeds=[self.error_embed('Invalid Parameter', 'The `race_laps`-count must be greater than 0')])
                return None
            raceTime = timedelta(seconds=raceLaps*lapTime.total_seconds())
        else:
            raceTime = self.parseRaceLen(self.children[0].value)
            if raceTime <= timedelta(minutes=0):
                await interaction.response.send_message(embeds=[self.error_embed('Invalid Parameter', 'The `raceTime` must be greater than 0. Check for the correct format of `hh:mm`')])
                return None
            raceLaps = math.ceil(raceTime/lapTime)


        if reserve_laps < 0:
            await interaction.response.send_message(embeds=[self.error_embed('Invalid Parameter', 'The `reserve_laps` must be greater or equals to 0')])
            return None

        data = FuelCalculator.calculate(raceLaps=raceLaps, raceTime=raceTime, lapTime=lapTime, fuel_usage=fuel_usage, reserve_laps=reserve_laps)
        return data



    def getFuelEmbed(self, interaction: discord.Interaction, data: LapData):
        
        def delta_to_raceTime(delta):
            hours, remainder = divmod(delta.total_seconds(), 3600)
            minutes = math.ceil(remainder/60)
            return f'{"%02.0f" % hours}:{"%02.0f" % minutes}'
        
        def delta_to_lapTime(delta):
            
            minutes, remainder = divmod(delta.total_seconds(), 60)
            seconds = int(remainder)
            ms = (remainder-seconds)*1000

            return f'{"%02.f" % minutes}:{"%02.f" % seconds}.{"%01.f" % ms}'
        
        raceTime = delta_to_raceTime(data.raceTime)
        lapTime = delta_to_lapTime(data.lapTime)
        reserveRatio = data.reserveLaps / data.raceLaps*100

        eb = discord.Embed(
            title='Fuel Calculation',
            color=0x0099ff
        )

        eb.add_field(name='Racetime', value=raceTime, inline=True)
        eb.add_field(name='Laptime', value=lapTime, inline=True)
        eb.add_field(name='Fuel per Lap', value=f'{data.fuelUsage:.2f}', inline=True)
        eb.add_field(name='Racelaps', value=f'{data.raceLaps}', inline=True)
        eb.add_field(name='Fuel per Minute (est.)', value="%.2f" % data.fpm, inline=True)
        eb.add_field(name='Minimum Fuel Required', value=f'{math.ceil(data.fuel)} l', inline=False)
        eb.add_field(name=f'Safe Fuel (+{data.reserveLaps} laps / +{int(reserveRatio)}%)', value=f'{math.ceil(data.saveFuel)} l', inline=True)
        
        eb.set_footer(text=f'Calculation requested by {interaction.user.display_name}',
                icon_url=interaction.user.display_avatar.url)

        return eb


    ##################
    # Discord Methods
    #################

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


    def populate(self):
        self.add_item(
            discord.ui.InputText(
                label='Laptime (m:ss.ff or seconds)',
                placeholder='1:56.9'
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="Fuel Usage (ltrs/lap)",
                placeholder='3.2'
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="Reserve Laps (for safe fuel)",
                value="3"
            )
        )


    async def callback(self, interaction: discord.Interaction):
        data = await self.getFuelData(interaction=interaction)

        if data:
            embed = self.getFuelEmbed(interaction, data)
            await interaction.response.send_message(embeds=[embed])



class FuelTimeModal(FuelModal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.populate()

    def populate(self):
        self.add_item(
            discord.ui.InputText(
                label='Race Length (hh:ss or minutes)',
                placeholder='0:40',
                custom_id='modal_field_racelen_time'
            )
        )
        super().populate()


class FuelLapsModal(FuelModal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.populate()

    def populate(self):
        self.add_item(
            discord.ui.InputText(
                label='Race Laps',
                placeholder='25',
                custom_id='modal_field_racelen_laps'
            )
        )
        super().populate()




class FuelModule(discord.Cog):
    
    ##################
    # Statics
    #################

    fuel_group = discord.SlashCommandGroup('fuel', 'Calculate fuel usage for a race')


    ##################
    # Cog setup
    #################
    
    def __init__(self, client):
        self.client = client
        self._avatar_url = 'https://cdn.discordapp.com/avatars'

    
    # ###########
    # Commands
    # ###########

    @fuel_group.command(name='time', description='Calculate based on max session time')
    async def fuel_time(self, ctx: discord.ApplicationContext):
        modal = FuelTimeModal(title='Fuel Calculation')
        await ctx.interaction.response.send_modal(modal)


    @fuel_group.command(name='laps', description='Calculate based on max laps')
    async def fuel_laps(self, ctx: discord.ApplicationContext):
        modal = FuelLapsModal(title='Fuel Calculation')
        await ctx.interaction.response.send_modal(modal)


    # =====================
    # events functions
    # =====================

    @discord.Cog.listener()
    async def on_ready(self):
        log.info('FuelModule loaded')


# =====================
# commands functions
# =====================

def setup(client):
    client.add_cog(FuelModule(client))
