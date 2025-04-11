# config.py
import discord
from discord.ext import commands

MASTER_IDS = [1152338010248069163]
SECURE_CHANNEL = 1226790349968769045
LOGGING_CHANNEL_ID = 1226790367232266261  # Replace with your channel ID
CYBER_COLOR = 0xFF00FF
SAFE_COMMANDS = ["neural_scan", "system_diagnostic", "data_backup"]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)