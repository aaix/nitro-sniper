import discord
import aiohttp
import re
import asyncio
import datetime
with open("TOKEN","r",encoding='utf-8') as f:
    TOKEN = f.read().split("\n")[0]


class Sweeper(discord.Client):
    def __init__(self,loop):
        self.r = re.compile(r"(https:\/\/)?(discord\.com\/gifts\/|discordapp\.com\/gifts\/|discord\.gift\/)([a-zA-Z0-9]{16})")
        self.cs = aiohttp.ClientSession(loop=loop)
        self.cache = set()
        super().__init__(
            loop=loop,
            max_messages=None,
            guild_subscriptions=False,
            fetch_offline_members=False
        )
    print("Active")

    async def on_message(self,message):
        code = self.check(message.content)
        if code:
            async with self.cs.post(
                    f"https://discord.com/api/v7/entitlements/gift-codes/{code}/redeem?",
                    headers={
                        "authorization":TOKEN,
                        "Content-Type":"application/json"
                    },
                    json={
                        "channel_id":message.channel.id,
                        "payment_source_id":None
                    }
            ) as query:

                posttime = datetime.datetime.utcnow() - message.created_at
                r = await self.decode(query)
                if r.get("message"):
                    print(f"{code} - {r['message']} ({r['code']})")
                elif r.get("subscription_plan"):
                    print(f"{code} - {r['subscription_plan']['name']} ({r['gifter_user_id']})")
                else:
                    print(f"{code} HTTP {query.status}")
            print(f"{code} from {message.author} in {message.guild or 'DMS'}\nTook {posttime.total_seconds()*1000}ms\n")

    def check(self,content):
        r = self.r.match(content)
        if r:
            string = r.group().split("/")[-1]
            if string not in self.cache:
                self.cache.add(string)
                return string

    async def decode(self,response):
        try:
            return await response.json()
        except aiohttp.ContentTypeError:
            return {}


loop = asyncio.get_event_loop()
client = Sweeper(loop)
client.run(TOKEN,bot=False)
