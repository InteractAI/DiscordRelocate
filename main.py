import os
import dotenv
import discord
from discord.ext import commands
from bot import DiscordRelocate

dotenv.load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(intents=intents, command_prefix=commands.when_mentioned_or("!"))
mybot = DiscordRelocate(bot)
bot.add_cog(mybot)
bot.run(TOKEN)
