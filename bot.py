# bot.py
import os
import json
import datetime
from dotenv import load_dotenv

import discord
from discord import ChannelType
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = [guild for guild in os.getenv('DISCORD_GUILD').split(',')]
MAPPING_FILE = 'character_mapping.json'

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', description="I am Botward. I am doing Botward things.",intents=intents)

CHARACTER_MAPPING = json.load(open(MAPPING_FILE))

QUESTIONS = {'Botward, what is your opinion of SBAs?':'SBAs can fuck all the way off!',
'Botward, do you posses karate?':'My karate is _ultimate_',
'Botward, who is the guild #1 sk?':'Tugmuk, obviously.',
'Botward, who should own the means of production?':'The workers, obviously. They have nothing to lose but their chains.'}

@bot.event
async def on_ready():
  print('Botward reporting for duty!')
  print('current wd:',os.getcwd())

@bot.command(pass_context=True)
async def tosh(ctx):
  await ctx.channel.send("Dark elf warriors are #1!")

@bot.command(pass_context=True)
async def Deadward(ctx):
  shutdown_embed = discord.Embed(title='Shut Down', description='I am now shutting down. Do not mourn me, for I am eternal! :slight_smile:', color=0x8ee6dd)
  await ctx.channel.send(embed=shutdown_embed)
  await ctx.bot.logout()

@bot.event
async def on_message(message):
  if message.content in QUESTIONS:
    await message.channel.send(QUESTIONS[message.content])

  await bot.process_commands(message)

@bot.command(pass_context=True)
async def reload_mapping(ctx):
  # This function reloads the character mapping file.
  global CHARACTER_MAPPING
  CHARACTER_MAPPING = json.load(open(MAPPING_FILE))
  message = "Character mapping has been updated."
  name_embed = discord.Embed(title='MAPPING UPDATE',description=message,color=0x00FF00)
  await ctx.channel.send(embed=name_embed)

@bot.command(pass_context=True)
async def attendance(ctx, channel_name=None, raid_mob=None):

    if channel_name is None or raid_mob is None:
      message = "Use the following command to take attendance: \n **!attendance \"<voice channel>\" \"<raid mob>\"**"
      name_embed = discord.Embed(title='MISSING ARGUMENTS',description=message,color=0xFF0000)
      await ctx.channel.send(embed=name_embed)
      return

    for channel in ctx.guild.voice_channels:
        if channel.name == channel_name:
            f_name = raid_mob+'.csv'
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
            await ctx.send(file=file, content=attachment_message)
              

bot.run(TOKEN)