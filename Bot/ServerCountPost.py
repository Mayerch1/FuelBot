import os
import asyncio
import requests
import json

import interactions
from datetime import datetime, timedelta

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
        api_path='/bots/{:d}/stats',
        server_cnt_name='server_count',
        shard_cnt_name='shard_count',
        shard_id_name='shard_id'
    ),
    BotListService(
        name='BotsGG',
        api_base='https://discord.bots.gg/api/v1',
        api_path='/bots/{:d}/stats',
        server_cnt_name='guildCount',
        shard_cnt_name='shardCount',
        shard_id_name='shardId'
    ),
    BotListService(
        name='DBL',
        api_base='https://discordbotlist.com/api/v1',
        api_path='/bots/{:d}/stats',
        server_cnt_name='guilds',
        shard_id_name='shard_id'
    ),
    BotListService(
        name='Discords',
        api_base='https://discords.com/bots/api',
        api_path='/bot/{:d}',
        server_cnt_name='server_count'
    ),
    BotListService(
        name='Disforge',
        api_base='https://disforge.com/api',
        api_path='/botstats/{:d}',
        server_cnt_name='servers'
    ),
    BotListService(
        name='DLSpace',
        api_base='https://api.discordlist.space/v2',
        api_path='/bots/{:d}',
        server_cnt_name='serverCount'
    ),
]


class ServerCountPost():

    def __init__(self, client):
        self.client: interactions.Client = client
        self.serverList = ServerList
        self.user_agent = "fuelBot (https://github.com/Mayerch1/FuelBot)"

        # init all server objects
        for sList in self.serverList:
            if os.path.exists(f'tokens/{sList.name}.txt'):
                sList.token = open(f'tokens/{sList.name}.txt', 'r').readline()[:-1]
                
                if sList.token:
                    print(f'starting {sList.name} job')
                else:
                    print(f'WARN: found {sList.name} config, but token is empty')
            else:
                print(f'ignoring {sList.name}, no Token')



    async def post_count(self, service: BotListService, payload):
        """post the payload to the given service
           token MUST be set in service

        Args:
            service (BotListService): [description]
            payload ([type]): [description]
        """

        url = service.api_base + service.api_path.format(self.client.me.id)
        
        headers = {
            'User-Agent'   : self.user_agent,
            'Content-Type' : 'application/json',
            'Authorization': service.token
        }

        payload = json.dumps(payload)

        r = requests.post(url, data=payload, headers=headers)

        if r.status_code >= 300:
            print(f'{service.name} Server Count Post failed with {r.status_code}')



    async def update_stats(self):
        """This function runs every 30 minutes to automatically update your server count."""

        guilds = await self.client._http.get_self_guilds()
        server_count = len(guilds)
        #Analytics.guild_cnt(server_count)

        for sList in self.serverList:
            
            if not sList.token:
                continue
            
            cnt_name = sList.server_cnt_name
            shard_name = sList.shard_cnt_name
            id_name = sList.shard_id_name

            payload = {
                f'{cnt_name}': server_count
            }
            # if self.client.shard_count and shard_name:
            #     payload[shard_name] = self.client.shard_count
            # if self.client.shard_id and id_name:
            #     payload[id_name] = self.client.shard_id

            await self.post_count(sList, payload=payload)



    async def loop(self):
        loop_interval = timedelta(hours=1)
        loop_start = None
        while 1:
            loop_start = datetime.utcnow()

            try:
                await self.update_stats()
            except Exception as e:
                print('aborted post due to exception')
                print(e)

            loop_end = datetime.utcnow()
            wait_time = loop_interval - (loop_end-loop_start)
            wait_time_s = max(wait_time.total_seconds(), 0)

            print(f'post sleeping for {wait_time_s}s')
            await asyncio.sleep(wait_time_s)
  

    def start_loop(self):

        async_loop = asyncio.get_event_loop()
        asyncio.ensure_future(self.loop(), loop=async_loop)
        print('started ServerCountPost loop')
