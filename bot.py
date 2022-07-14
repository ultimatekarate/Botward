# bot.py
import os

import discord
from discord import ChannelType
from discord.ext import commands

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', description="Hey there, I'm Botty (for example)!",intents=intents)

@bot.event
async def on_ready():
  print('Ready!')

@bot.command(pass_context=True)
async def Attendance(ctx, channel_name):
    for channel in ctx.guild.voice_channels:
        if channel.name == channel_name:
            message = 'Members in '+channel_name
            await ctx.send(message)
            for member in channel.members:
                print(member)
                await ctx.send(member)

bot.run(TOKEN)