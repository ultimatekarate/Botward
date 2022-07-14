# bot.py
import os
import json
import datetime

import discord
from discord import ChannelType
from discord.ext import commands

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
MAPPING_FILE = os.getenv('CHARACTER_MAPPING')

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', description="I am Botward. I am doing Botward things.",intents=intents)

CHARACTER_MAPPING = json.load(open(MAPPING_FILE))

@bot.event
async def on_ready():
  print('Botward reporting for duty!')
  print(os.getcwd())

@bot.command(pass_context=True)
async def Deadward(ctx):
  shutdown_embed = discord.Embed(title='Shut Down', description='I am now shutting down. Do not mourn me, for I am eternal! :slight_smile:', color=0x8ee6dd)
  await ctx.channel.send(embed=shutdown_embed)

@bot.command(pass_context=True)
async def a(ctx, channel_name='raid-chat', filename=None):
    for channel in ctx.guild.voice_channels:
        if channel.name == channel_name:
            message = 'Members in '+channel_name
            await ctx.send(message)

            if filename is None:
              f_name = 'raid-attendance'
            else:
              f_name = filename
            
            attendance_file = open(f_name+'.csv','w+')

            for member in channel.members:
              member_name = member.name + '#' + member.discriminator
              char = CHARACTER_MAPPING.get(member_name)
              if not char:
                message = "Discord name " + member_name + " was not found in the mapping."
                name_embed = discord.Embed(title='NAME NOT FOUND',description =message,color=0xFF0000)
                await ctx.channel.send(embed=name_embed)
              else:
                attendance_file.write(f"1\t{char}\t65\tBard\tYes\n")
            attendance_file.close()

            file = discord.File(f_name+'.csv')
            await ctx.send(file=file, content="Message to be sent")
              

bot.run(TOKEN)
