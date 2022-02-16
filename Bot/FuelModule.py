import math
import regex

from datetime import timedelta
import interactions

class FuelModule():
    
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
    
    def __init__(self, bot):
        self.client = bot
        self._avatar_url = 'https://cdn.discordapp.com/avatars'
        

    ##################
    # Fuel stuff
    #################
    
    def error_embed(self, title, reason):
        
        eb = interactions.Embed(title=title, description=reason, color=0xff0000)
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

        eb = interactions.Embed(
            title='Fuel Calculation',
            color=0x0099ff,
            fields=[
                interactions.EmbedField(name='Racetime', value=raceTime, inline=True),
                interactions.EmbedField(name='Laptime', value=lapTime, inline=True),
                interactions.EmbedField(name='Fuel per Lap', value=f'{data.fuelUsage:.2f}', inline=True),
                interactions.EmbedField(name='Racelaps', value=f'{data.raceLaps}', inline=True),
                interactions.EmbedField(name='Fuel per Minute (est.)', value="%.2f" % data.fpm, inline=True),
                interactions.EmbedField(name='Minimum Fuel Required', value=f'{math.ceil(data.fuel)} l', inline=False),
                interactions.EmbedField(name=f'Safe Fuel (+{data.reserveLaps} laps / +{int(reserveRatio)}%)', value=f'{math.ceil(data.saveFuel)} l', inline=True)
            ],
            footer=interactions.EmbedFooter(
                text=f'Calculation requested by {ctx.author.nick or ctx.author.user.username}',
                icon_url=f'{self._avatar_url}/{ctx.author.user.id}/{ctx.author.avatar}.png'
            )
        )

        return eb
    
    
    async def handle_fuel_calculation(self, ctx, length: str, raceLaps: int, laptime: str, fuel_usage: float, reserve_laps: int):
        
        try:
            reserve_laps = int(reserve_laps)
        except ValueError:
            await ctx.send(embeds=self.error_embed('Invalid Parameter', 'The `reserve_laps` must be an integer (e.g. `3`)'))
            return
            
        try:
            fuel_usage = float(fuel_usage)
        except ValueError:
            await ctx.send(embeds=self.error_embed('Invalid Parameter', 'The `fuel_usage` must be a decimal number (e.g. `3.1`)'))
            return

        lapTime = self.parseLapTime(laptime)
        if lapTime <= timedelta(minutes=0):
            await ctx.send(embeds=self.error_embed('Invalid Parameter', 'The `laptime` must be greater than 0. Check for the correct format of `mm:ss.fff`'))
            return
        
        if length:
            raceTime = self.parseRaceLen(length)
            if raceTime <= timedelta(minutes=0):
                await ctx.send(embeds=self.error_embed('Invalid Parameter', 'The `raceTime` must be greater than 0. Check for the correct format of `hh:mm`'))
                return
            raceLaps = math.ceil(raceTime/lapTime)
        else:
            try:
                raceLaps = int(raceLaps)
            except ValueError:
                await ctx.send(embeds=self.error_embed('Invalid Parameter', 'The `race_laps` must be an integer (e.g. `3`)'))
                return
            if raceLaps <= 0:
                await ctx.send(embeds=self.error_embed('Invalid Parameter', 'The `race_laps`-count must be greater than 0'))
                return
            raceTime = timedelta(seconds=raceLaps*lapTime.total_seconds())


        if reserve_laps < 0:
            await ctx.send(embeds=self.error_embed('Invalid Parameter', 'The `reserve_laps` must be greater or equals to 0'))
            return

        
        lapData = FuelModule.LapData(raceTime=raceTime, raceLaps=raceLaps, lapTime=lapTime, fuelUsage=float(fuel_usage), reserveLaps=reserve_laps)

        self.setFuelUsage(lapData)
        eb = self.getFuelEmbed(ctx, lapData)

        await ctx.send(embeds=eb)
