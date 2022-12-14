"""
    This is the main python class that will run on the server
"""
import asyncio
import logging
import logging.handlers
import os

from typing import List, Optional

# import asyncpg
import discord
from discord.ext import commands
from aiohttp import ClientSession

# from replit import db


class CustomBot(commands.Bot):
    def __init__(
        self,
        *args,
        initial_extensions: List[str],
        # db_pool: asyncpg.Pool,
        # db,
        logger,
        web_client: ClientSession,
        testing_guild_id: Optional[int] = None,
        **kwargs,
    ):
        intents = discord.Intents.default()
        # allow bot to chat in the channel
        intents.members = True
        super().__init__(*args, intents=intents, **kwargs)
        # self.db_pool = db_pool
        # self.db = db
        self.logger = logger
        self.web_client = web_client
        self.testing_guild_id = testing_guild_id
        self.initial_extensions = initial_extensions

    async def setup_hook(self) -> None:

        # here, we are loading extensions prior to sync to ensure we are syncing interactions defined in those extensions.

        for extension in self.initial_extensions:
            await self.load_extension(extension)

        # In overriding setup hook,
        # we can do things that require a bot prior to starting to process events from the websocket.
        # In this case, we are using this to ensure that once we are connected, we sync for the testing guild.
        # You should not do this for every guild or for global sync, those should only be synced when changes happen.
        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)
            # We'll copy in the global commands to test with:
            self.tree.copy_global_to(guild=guild)
            # followed by syncing to the testing guild.
            await self.tree.sync(guild=guild)

    # This would also be a good place to connect to our database and
    # load anything that should be in memory prior to handling events.


async def main():

    # When taking over how the bot process is run, you become responsible for a few additional things.

    # 1. logging

    # for this example, we're going to set up a rotating file logger.
    # for more info on setting up logging,
    # see https://discordpy.readthedocs.io/en/latest/logging.html and https://docs.python.org/3/howto/logging.html

    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        filename="discord.log",
        encoding="utf-8",
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
    )
    dt_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Alternatively, you could use:
    # discord.utils.setup_logging(handler=handler, root=False)

    # One of the reasons to take over more of the process though
    # is to ensure use with other libraries or tools which also require their own cleanup.

    # Here we have a web client and a database pool, both of which do cleanup at exit.
    # We also have our bot, which depends on both of these.
    async with ClientSession() as our_client:
        # 2. We become responsible for starting the bot.

        # exts = ["general", "mod", "dice"]
        exts = ["Setup"]
        async with CustomBot(
            # commands.when_mentioned,
            command_prefix="$",
            # db=db,
            logger=logger,
            web_client=our_client,
            initial_extensions=exts,
        ) as bot:
            await bot.start(os.getenv("TOKEN", ""))


# For most use cases, after defining what needs to run, we can just tell asyncio to run it:
if __name__ == "__main__":
    asyncio.run(main())
