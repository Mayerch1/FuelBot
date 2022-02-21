import os
import requests
import json
import logging

import discord
from discord.ext import tasks

log = logging.getLogger('FuelBot')

class BotListService:
    def __init__(self, name, api_base, api_path, server_cnt_name=None, shard_cnt_name=None, shard_id_name=None):
        self.name = name
        self.api_base = api_base
        self.api_path = api_path
        
        self.server_cnt_name = server_cnt_name
        self.shard_cnt_name = shard_cnt_name
        self.shard_id_name = shard_id_name

        self.token = None


ServerList = [
    BotListService(
        name='TopGG',
        api_base='https://top.gg/api',
        api_path='/bots/{:s}/stats',
        server_cnt_name='server_count',
        shard_cnt_name='shard_count',
        shard_id_name='shard_id'
    ),
    BotListService(
        name='BotsGG',
        api_base='https://discord.bots.gg/api/v1',
        api_path='/bots/{:s}/stats',
        server_cnt_name='guildCount',
        shard_cnt_name='shardCount',
        shard_id_name='shardId'
    ),
    BotListService(
        name='DBL',
        api_base='https://discordbotlist.com/api/v1',
        api_path='/bots/{:s}/stats',
        server_cnt_name='guilds',
        shard_id_name='shard_id'
    ),
    BotListService(
        name='Discords',
        api_base='https://discords.com/bots/api',
        api_path='/bot/{:s}',
        server_cnt_name='server_count'
    ),
    BotListService(
        name='Disforge',
        api_base='https://disforge.com/api',
        api_path='/botstats/{:s}',
        server_cnt_name='servers'
    ),
    BotListService(
        name='DLSpace',
        api_base='https://api.discordlist.space/v2',
        api_path='/bots/{:s}',
        server_cnt_name='serverCount'
    ),
]


class ServerCountPost(discord.Cog):

    def __init__(self, client):
        self.client: discord.AutoShardedBot = client
        self.serverList = ServerList
        self.user_agent = "fuelBot (https://github.com/Mayerch1/FuelBot)"

        # init all server objects
        for sList in self.serverList:
            if os.path.exists(f'tokens/{sList.name}.txt'):
                sList.token = open(f'tokens/{sList.name}.txt', 'r').readline()[:-1]
                
                if sList.token:
                    log.debug(f'starting {sList.name} job')
                else:
                    log.warning(f'found {sList.name} config, but token is empty')
            else:
                log.debug(f'ignoring {sList.name}, no Token')

        self.post_loop.start()



    def cog_unload(self):
        self.post_loop.cancel()



    async def post_count(self, service: BotListService, payload):
        """post the payload to the given service
           token MUST be set in service

        Args:
            service (BotListService): [description]
            payload ([type]): [description]
        """

        url = service.api_base + service.api_path.format(str(self.client.user.id))
        
        headers = {
            'User-Agent'   : self.user_agent,
            'Content-Type' : 'application/json',
            'Authorization': service.token
        }

        payload = json.dumps(payload)

        r = requests.post(url, data=payload, headers=headers, timeout=5)

        if r.status_code >= 300:
            log.info(f'{service.name} Server Count Post failed with {r.status_code}')



    async def update_stats(self):
        """This function runs every 30 minutes to automatically update your server count."""

        server_count = len(self.client.guilds)

        for sList in self.serverList:
            
            if not sList.token:
                continue
            
            cnt_name = sList.server_cnt_name
            shard_name = sList.shard_cnt_name
            id_name = sList.shard_id_name

            payload = {
                f'{cnt_name}': server_count
            }

            if self.client.shard_count and shard_name:
                payload[shard_name] = self.client.shard_count
            if self.client.shard_id and id_name:
                payload[id_name] = self.client.shard_id

            await self.post_count(sList, payload=payload)



    @tasks.loop(minutes=30)
    async def post_loop(self):
        await self.update_stats()
  

    @post_loop.before_loop
    async def start_loop(self):
        await self.client.wait_until_ready()




def setup(client):
    client.add_cog(ServerCountPost(client))