# bot.py
import os
import json
import datetime
import pandas as pd
import random

from dotenv import load_dotenv

import sys

import discord
from discord import ChannelType
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', description="I am Botward. I am doing Botward things.",intents=intents)


# custom decorators
def is_paragon():
  def predicate(ctx):
    return ctx.guild == 'Paragon'
  return commands.check(predicate)

def can_take_attendance():
  def predicate(ctx):
    author_roles = [x.name.replace(" ","").lower() for x in ctx.author.roles]
    attendance_roles = ['raidlead', 'seniorofficer', 'botwardtester', 'officer', 'guildleader']

    return not set(author_roles).isdisjoint(attendance_roles)
  return commands.check(predicate)

def can_do_botward_stuff():
  def predicate(ctx):
    author_roles = [x.name.replace(" ","").lower() for x in ctx.author.roles]
    botward_roles = ['raidlead', 'botwardtester']

    return not set(author_roles).isdisjoint(botward_roles)
  return commands.check(predicate)

def turn_off():
  def predicate(ctx):
    return False
  return commands.check(predicate)

# Actual bot functions
@bot.event
async def on_ready():
  print('Botward reporting for duty!')
  print('current wd:',os.getcwd())

@bot.command(pass_context=True)
@can_do_botward_stuff()
async def Deadward(ctx):
  shutdown_embed = discord.Embed(title='Shut Down', description='I am now shutting down. Do not mourn me, for I am eternal! :slight_smile:', color=0x8ee6dd)
  await ctx.channel.send(embed=shutdown_embed)
  await ctx.bot.close()

@bot.command(pass_context=True)
@can_take_attendance()
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
@can_take_attendance()
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
            attendance_file.write(f"{dkp_name},{tick_value}\n")
            
        attendance_file.close()
        raid_time = datetime.datetime.now().strftime('%D %H:%M')
        file = discord.File(full_path)
        attachment_message = f"Attendance taken in {channel_name} for {tick_type} at {raid_time}. \n {len(channel.members)} nerds accounted for."

        print('Taking attendance for '+guild_name+'.')
        print(attachment_message)

        await ctx.send(file=file, content=attachment_message)
        return

@bot.command(pass_context = True)
@can_do_botward_stuff()
async def listroles(ctx):
  roles = [x.name for x in ctx.author.roles]
  await ctx.channel.send(content=roles)

@bot.command(pass_context=True)
@turn_off()
async def make_mappingfile(ctx):
  member_dict = {}

  for member in ctx.guild.members:
    member_name = member.name + '#' + member.discriminator
    member_nick = member.nick

    if member_nick is None:
      member_nick = member.name
    roles = [x.name.lower().replace(" ","") for x in member.roles]
    paragon_roles = ['officer','member','newmember','botwardtester']

    if not set(roles).isdisjoint(paragon_roles):
      member_dict[member_name] = member_nick

  print(member_dict)
  sorted_dict = dict(sorted(member_dict.items(),key = lambda item:item[1]))
  guild_name = ctx.guild.name.replace(" ","")
  with open(f"/home/container/character_mapping/{guild_name}.json","w+") as mapfile:
    json.dump(sorted_dict, mapfile)

  return

@bot.command(pass_context=True)
@is_paragon()
async def gnometoss(ctx,reason='because they deserve it.'):
  target = random.choice(ctx.server.members).mention
  tstring = f'{ctx.author.nick} tosses a gnome at {target} because {reason}!'
  await ctx.channel.send(content=tstring)

@bot.command(pass_context=True)
@is_paragon()
async def totaldkp(ctx,raid_name=None):
  guild_name = ctx.guild.name.replace(" ","")
  raid_path = f'/home/container/attendance_logs/{guild_name}/{raid_name}/'
  if guild_name == 'Paragon' or 'BGToolsTestServer':
    if raid_name is None:
      message = "Use the following command to take aggregate attendance: \n **!totaldkp \"<raid name>\"**"
      name_embed = discord.Embed(title='MISSING ARGUMENTS',description=message,color=0xFF0000)
      await ctx.channel.send(embed=name_embed)

    if os.path.exists(raid_path):
      # Find all files
      log_files = os.listdir(raid_path)

      ontime  = [x for x in log_files if x.startswith('ontime')]
      hourly  = [x for x in log_files if x.startswith('hourly')]
      raidend = [x for x in log_files if x.startswith('raidend')]

      for x in ontime:
        ontime_df = pd.read_csv(raid_path+x,header=None)

      ontime_df.columns = ['discord_name', 'ontime']
      hourly_dkp_ticks = [list(pd.read_csv(raid_path+x,header=None)[1]) for x in hourly]
      total_hourly_dkp = [sum(x) for x in zip(*hourly_dkp_ticks)]
      ontime_df['hourly'] = total_hourly_dkp

      for x in raidend:
        raidend_df = pd.read_csv(raid_path+x,header=None)

      ontime_df['raidend'] = raidend_df[1]

      ontime_df.to_csv(raid_path+'aggregate.csv',header=None,index=None,mode='w+')
      file = discord.File(raid_path+'aggregate.csv')
      attachment_message = f"Finalizing dkp for {raid_name}. Good work."

      print('Computing total dkp earned '+guild_name+'.')

      await ctx.send(file=file, content=attachment_message)

    else:
      message = f"{raid_name} is not a valid raid."
      name_embed = discord.Embed(title='Raid does not exist!',description=message,color=0xFF0000)
      await ctx.channel.send(embed=name_embed)

  else:
    message = "This function can only be used by members of Paragon."
    name_embed = discord.Embed(title='HOW DARE YOU?!',description = message,color=0xFF0000)
    await ctx.channel.send(embed=name_embed)

bot.run(TOKEN)
