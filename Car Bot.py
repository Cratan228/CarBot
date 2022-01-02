import discord
from discord import Member
from discord import Reaction
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow, create_button
from discord_slash.utils.manage_commands import create_choice, create_option
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import wait_for_component
from discord_slash import cog_ext, SlashContext
from discord_slash.context import ComponentContext
from discord_slash.http import CustomRoute
from discord.ext import commands
import os
from discord.ext.commands import has_permissions, MissingPermissions
from datetime import datetime

import subprocess
import sys

try:
    from pretty_help import DefaultMenu, PrettyHelp
    from prettytable import PrettyTable
except:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'discord-pretty-help'])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'prettytable'])
    from pretty_help import DefaultMenu, PrettyHelp

from discord_slash import SlashCommand

bot = commands.Bot(command_prefix='#', intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)
path = os.path.dirname(os.path.realpath(__file__)) + "/"

nav = DefaultMenu("⬅️", "➡️", "❌")
bot.help_command = PrettyHelp(
    DefaultMenu=nav,
    index_title="Categories",
    active_time=60,
    no_category="Help",
    timestamp=datetime.utcnow()
)

owner = 417939383698718720


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Car-hunt!"))
    print("Bot is online!")


@bot.command(hidden=True)
async def unload(ctx, extension):
    if ctx.message.author.id == owner:
        bot.unload_extension(f"Cogs.{extension}")
        await ctx.send(f"Unloaded {extension} 🔓")
    else:
        await ctx.send("**__Error:__** You are not entitled to use this command!")


@bot.command(hidden=True)
async def load(ctx, extension):
    if ctx.message.author.id == owner:
        bot.load_extension(f"Cogs.{extension}")
        await ctx.send(f"Loaded {extension} 🔒")
    else:
        await ctx.send("**__Error:__** You are not entitled to use this command!")


@bot.command(hidden=True)
async def reload(ctx, extension):
    if ctx.message.author.id == owner:
        bot.unload_extension(f"Cogs.{extension}")
        bot.load_extension(f"Cogs.{extension}")
        await ctx.send(f"Reloaded {extension} 🔃")
    else:
        await ctx.send("**__Error:__** You are not entitled to use this command!")


for filename in os.listdir(f"{path}Cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"Cogs.{filename[:-3]}")

bot.run("ODQyMjk4NDA2NDk5OTA5NjQz.YJzRhQ.LOHLy0UPXjbOuYcO9GhcOwmT2E4")
