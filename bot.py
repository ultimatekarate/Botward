# bot.py
import os
import json
import datetime
from dotenv import load_dotenv

import sys

import discord
from discord import ChannelType
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', description="I am Botward. I am doing Botward things.",intents=intents)

@bot.event
async def on_ready():
  print('Botward reporting for duty!')
  print('current wd:',os.getcwd())

@bot.command(pass_context=True)
async def Deadward(ctx):
  shutdown_embed = discord.Embed(title='Shut Down', description='I am now shutting down. Do not mourn me, for I am eternal! :slight_smile:', color=0x8ee6dd)
  await ctx.channel.send(embed=shutdown_embed)
  await ctx.bot.close()

@bot.command(pass_context=True)
async def show_mapping(ctx):
  guild = ctx.guild.name.replace(" ","")
  MAPPING_FILE = f'/home/container/character_mapping/{guild}.json'

  if sys.platform == 'win32':
    MAPPING_FILE =  f'/character_mapping/{guild}.json'
  
  CHARACTER_MAPPING = json.load(open(MAPPING_FILE))

  mapping_list = []
  for member_name in sorted(CHARACTER_MAPPING,key=CHARACTER_MAPPING.get):
    temp_str=member_name+':'+CHARACTER_MAPPING[member_name]
    mapping_list.append(temp_str)

  message='\n'.join(mapping_list)
  name_embed = discord.Embed(title='Character Name Mapping',description=message,color=0x00FF00)
  await ctx.channel.send(embed=name_embed)

@bot.command(pass_context=True)
async def attendance(ctx, channel_name=None, raid_mob=None, tick_type=None):
  guild_name = ctx.guild.name.replace(" ","")
  MAPPING_FILE = f'/home/container/character_mapping/{guild_name}.json'
  if sys.platform == 'win32':
    MAPPING_FILE =  f'character_mapping/{guild_name}.json'

  CHARACTER_MAPPING = json.load(open(MAPPING_FILE))

  if guild_name == 'BloodGuard':
    if channel_name is None or raid_mob is None:
      message = "Use the following command to take attendance: \n **!attendance \"<voice channel>\" \"<raid mob>\"**"
      name_embed = discord.Embed(title='MISSING ARGUMENTS',description=message,color=0xFF0000)
      await ctx.channel.send(embed=name_embed)
      return

    for channel in ctx.guild.voice_channels:
      if channel.name == channel_name:
        f_name = f'/home/container/attendance_logs/{guild_name}/'+raid_mob+'.csv'
        attendance_file = open(f_name,'w+')

        for member in channel.members:
          member_name = member.name + '#' + member.discriminator
          char = CHARACTER_MAPPING.get(member_name)
          if not char:
            message = "Discord name " + member_name + " was not found in the mapping."
            name_embed = discord.Embed(title='NAME NOT FOUND',description = message,color=0xFF0000)
            await ctx.channel.send(embed=name_embed)
          else:
            attendance_file.write(f"1\t{char}\t65\tBard\tYes\n")
            
        attendance_file.close()
        raid_time = datetime.datetime.now().strftime('%D %H:%M')
        file = discord.File(f_name)
        attachment_message = "Attendance taken in "+channel_name+" for "+ raid_mob + " at "+str(raid_time)+". \n" + str(len(channel.members)) + " nerds accounted for."

        print('Taking attendance for '+guild_name+'.')
        print(attachment_message)

        await ctx.send(file=file, content=attachment_message)
        return
  if guild_name == 'Paragon' or 'BGToolsTestServer':
    if channel_name is None or raid_mob is None or tick_type is None:
      message = "Use the following command to take attendance: \n **!attendance \"<voice channel>\" \"<raid name>\"  \"<tick type>\"**"
      name_embed = discord.Embed(title='MISSING ARGUMENTS',description=message,color=0xFF0000)
      await ctx.channel.send(embed=name_embed)
      return
    if tick_type not in ['hourly', 'ontime', 'raidend']:
      message = "tick type must be one of the following: **hourly, ontime, raidend**"
      name_embed = discord.Embed(title='MISSING ARGUMENTS',description=message,color=0xFF0000)
      await ctx.channel.send(embed=name_embed)
      return

    for channel in ctx.guild.voice_channels:
      if channel.name == channel_name:
        raid_time = datetime.datetime.now().strftime('%m-%d-%y_%H:%M')
        f_path = f'/home/container/attendance_logs/{guild_name}/{raid_mob}/'

        #f_path = f'/attendance_logs/{guild_name}/{raid_mob}/'
        f_name = f'{tick_type}_{raid_time}.csv'

        full_path = f_path + f_name
        if not os.path.exists(f_path):
          os.makedirs(f_path)
          
        attendance_file = open(full_path,'w+')

        members_present = [member.name + '#' + member.discriminator for member in channel.members]

        for member_name in CHARACTER_MAPPING:

          tick_value = 0
          if member_name in members_present:
            tick_value = 1

          dkp_name = CHARACTER_MAPPING.get(member_name)

          if not dkp_name:
            message = "Discord name " + member_name + " was not found in the mapping."
            name_embed = discord.Embed(title='NAME NOT FOUND',description = message,color=0xFF0000)
            await ctx.channel.send(embed=name_embed)
          else:
            attendance_file.write(f"{dkp_name}\t{tick_value}")
            
        attendance_file.close()
        raid_time = datetime.datetime.now().strftime('%D %H:%M')
        file = discord.File(f_name)
        attachment_message = f"Attendance taken in {channel_name} for {raid_mob} at {raid_time}. \n {len(channel.members)} nerds accounted for."

        print('Taking attendance for '+guild_name+'.')
        print(attachment_message)

        await ctx.send(file=file, content=attachment_message)
        return

bot.run(TOKEN)
