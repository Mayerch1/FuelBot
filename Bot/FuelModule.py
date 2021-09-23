import math
import regex

from datetime import timedelta

import discord
from discord.ext import commands, tasks

from discord_slash import cog_ext, SlashContext, ComponentContext
from discord_slash.context import MenuContext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils import manage_components
from discord_slash.model import SlashCommandOptionType, ButtonStyle, ContextMenuType


class FuelModule(commands.Cog):
    
    ##################
    # Types
    #################
    
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
    
    ##################
    # Cog setup
    #################
    
    def __init__(self, client):
        self.client = client
        
    @commands.Cog.listener()
    async def on_ready(self):
        print('FuelModule loaded')
    
    ##################
    # Fuel stuff
    #################
    
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
    
    
    def setFuelUsage(self, data: LapData):
    
        data.fpm = data.fuelUsage / data.lapTime.total_seconds() * 60
        
        data.fuel = data.raceLaps * data.fuelUsage
        data.saveFuel = data.fuel + (data.reserveLaps + data.fuelUsage)


    def getFuelEmbed(self, ctx, data: LapData):
        
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

        eb = discord.Embed(title='Fuel Calculation')
        eb.color=0x0099ff
        
        eb.add_field(name='Racetime', value=raceTime, inline=True)
        eb.add_field(name='Laptime', value=lapTime, inline=True)
        eb.add_field(name='Fuel per Lap', value=data.fuelUsage, inline=True)
        eb.add_field(name='Racelaps', value=data.raceLaps, inline=True)
        eb.add_field(name='Fuel per Minute (est.)', value="%.2f" % data.fpm, inline=True)
        eb.add_field(name='Minimum Fuel Required', value=f'{math.ceil(data.fuel)} l', inline=False)
        eb.add_field(name=f'Safe Fuel (+{data.reserveLaps} laps / +{int(reserveRatio)}%)', value=f'{math.ceil(data.saveFuel)} l', inline=True)
        

        eb.set_author(name=ctx.me.display_name, icon_url=ctx.me.avatar_url or ctx.me.default_avatar_url)
        eb.set_footer(text=f'Calculation requested by {ctx.author.display_name}', icon_url=ctx.author.avatar_url or ctx.author.default_avatar_url)
        return eb
    
    @cog_ext.cog_subcommand(base='fuel', name='time', description='Calculate fuel for time limited races',
                            options=[
                                create_option(
                                    name='length',
                                    description='hh:mm or minutes',
                                    required=True,
                                    option_type=SlashCommandOptionType.STRING
                                ),
                                create_option(
                                    name='laptime',
                                    description='m:ss.ff or total seconds',
                                    required=True,
                                    option_type=SlashCommandOptionType.STRING
                                ),
                                create_option(
                                    name='fuel_usage',
                                    description='in liters/lap',
                                    required=True,
                                    option_type=SlashCommandOptionType.FLOAT
                                ),
                                create_option(
                                    name='reserve_laps',
                                    description='specify how many reserve is planned for the safe recommendation',
                                    required=False,
                                    option_type=SlashCommandOptionType.INTEGER
                                )
                            ])
    async def fuel_time(self, ctx, length, laptime, fuel_usage, reserve_laps=3):

        raceTime = self.parseRaceLen(length)
        lapTime = self.parseLapTime(laptime)
        
        raceLaps = math.ceil(raceTime/lapTime)

        lapData = FuelModule.LapData(raceTime=raceTime, raceLaps=raceLaps, lapTime=lapTime, fuelUsage=float(fuel_usage), reserveLaps=reserve_laps)

        self.setFuelUsage(lapData)
        eb = self.getFuelEmbed(ctx, lapData)

        await ctx.send(embed=eb)
    
    @cog_ext.cog_subcommand(base='fuel', name='laps', description='Calculate fuel for time limited races',
                            options=[
                                create_option(
                                    name='laps',
                                    description='number of laps',
                                    required=True,
                                    option_type=SlashCommandOptionType.INTEGER
                                ),
                                create_option(
                                    name='laptime',
                                    description='m:ss.ff or total seconds',
                                    required=True,
                                    option_type=SlashCommandOptionType.STRING
                                ),
                                create_option(
                                    name='fuel_usage',
                                    description='in liters/lap',
                                    required=True,
                                    option_type=SlashCommandOptionType.FLOAT
                                ),
                                create_option(
                                    name='reserve_laps',
                                    description='specify how many reserve is planned for the safe recommendation',
                                    required=False,
                                    option_type=SlashCommandOptionType.INTEGER
                                )
                            ])
    async def fuel_laps(self, ctx, laps, laptime, fuel_usage, reserve_laps=3):
        
        lapTime = self.parseLapTime(laptime)
        raceTime = timedelta(seconds=laps*lapTime.total_seconds())

        lapData = FuelModule.LapData(raceTime=raceTime, raceLaps=laps, lapTime=lapTime, fuelUsage=float(fuel_usage), reserveLaps=reserve_laps)
        
        self.setFuelUsage(lapData)
        eb = self.getFuelEmbed(ctx, lapData)
        
        await ctx.send(embed=eb)
    
def setup(client):
    client.add_cog(FuelModule(client))