from discord.ext import commands


class Setup(commands.Cog):
    def __init__(self, bot):
        self.name = "Setup"
        self.bot = bot
        print("loaded extension: ", self.name)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f"Welcome {member.mention}.")

    @commands.command(aliases=["Hi"])
    async def hello(self, ctx):
        await ctx.send(f"Hello {ctx.author.display_name}.")


async def setup(bot):
    await bot.add_cog(Setup(bot))
