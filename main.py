# -*- coding: utf-8 -*-
import discord
import subprocess
import asyncio
import os
from discord.ext import commands
from discord import app_commands
from discord.ui import Modal, TextInput
from discord import TextStyle
import token
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the TOKEN from the environment variables
token = os.getenv('TOKEN')

# 🔐 Konfiguration
MASTER_IDS = [1152338010248069163]
SECURE_CHANNEL = 1226790349968769045
CYBER_COLOR = 0xFF00FF
SAFE_COMMANDS = ["neural_scan", "system_diagnostic", "data_backup"]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger("discord").setLevel(logging.WARNING)
logging.getLogger("discord.gateway").setLevel(logging.WARNING)

# Enhance logging to capture all critical events and errors
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Log unhandled exceptions
def log_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # Allow keyboard interrupts to exit the program
        return
    logging.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

# Log bot events
@bot.event
async def on_error(event_method, *args, **kwargs):
    logging.error(f"Error in {event_method}", exc_info=True)

@bot.event
async def on_command_error(ctx, error):
    logging.error(f"Command error: {ctx.command} - {error}", exc_info=True)
    await ctx.send(embed=discord.Embed(
        title="⚠️ Command Error",
        description=f"An error occurred: {error}",
        color=0xFF0000
    ))

# 🔌 Terminal-Executor
class CyberTerminal:
    def __init__(self):
        self.sessions = {}

    async def execute(self, command: str) -> str:
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            return f"$ {command}\n\n{stdout.decode() or stderr.decode()}"[:1900]
        except Exception as e:
            return f"TERMINAL ERROR: {str(e)}"

    async def list_files(self, path: str) -> str:
        try:
            result = subprocess.run(["ls", "-la", path], capture_output=True, text=True, shell=True)
            return result.stdout or result.stderr
        except Exception as e:
            return f"ERROR: {str(e)}"

    async def read_file(self, file_path: str) -> str:
        try:
            with open(file_path, "r") as file:
                return file.read()[:1900]
        except Exception as e:
            return f"ERROR: {str(e)}"

    async def write_file(self, file_path: str, content: str) -> str:
        try:
            with open(file_path, "w") as file:
                file.write(content)
            return "File written successfully."
        except Exception as e:
            return f"ERROR: {str(e)}"

    async def delete_file(self, file_path: str) -> str:
        try:
            os.remove(file_path)
            return "File deleted successfully."
        except Exception as e:
            return f"ERROR: {str(e)}"

terminal = CyberTerminal()

# 🔒 Master-Check
def cyberlock():
    async def predicate(interaction: discord.Interaction):
        if interaction.user.id not in MASTER_IDS:
            embed = discord.Embed(
                title="⛔ NEURAL LOCK ACTIVATED",
                description="```diff\n- ACCESS VIOLATION DETECTED\n```",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True
    return app_commands.check(predicate)

# 🔒 Admin-Check
def adminlock():
    async def predicate(interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="⛔ ADMIN LOCK ACTIVATED",
                description="```diff\n- You need administrator rights to use this command.\n```",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True
    return app_commands.check(predicate)

# 🔐 Biometric Modal
class BioAuthModal(Modal):
    def __init__(self):
        super().__init__(title="Biometric Scan", timeout=120)
        self.neurocode = TextInput(
            label="Enter Neuro-Code",
            style=TextStyle.short,  # Updated to use TextStyle
            placeholder="XXXX-XXXX-XXXX",
            required=True
        )
        self.add_item(self.neurocode)

    async def on_submit(self, interaction: discord.Interaction):
        if self.neurocode.value == "1337-4242-9000":
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="✅ BIOMETRIC VERIFIED",
                    description="Neural signature confirmed",
                    color=CYBER_COLOR
                ),
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="⛔ ACCESS DENIED",
                    description="Invalid neuro-code",
                    color=0xFF0000
                ),
                ephemeral=True
            )

# 🖥️ Slash Command: /cyberterm
@bot.tree.command(name="cyberterm", description="Access the neural terminal")
@app_commands.describe(command="Terminal command to execute")
@cyberlock()
async def cyberterm(interaction: discord.Interaction, command: str):
    if interaction.channel.id != SECURE_CHANNEL:
        return await interaction.response.send_message(
            embed=discord.Embed(
                title="🚫 CHANNEL LOCKED",
                description="Terminal access restricted to secure zones",
                color=0xFF0000
            ),
            ephemeral=True
        )

    modal = BioAuthModal()
    await interaction.response.send_modal(modal)
    await modal.wait()

    if modal.neurocode.value != "1337-4242-9000":
        return

    await interaction.followup.send(
        embed=discord.Embed(
            title="🖥️ TERMINAL SESSION STARTED",
            description="Type your commands below. Send `exit` to close the session.",
            color=CYBER_COLOR
        ),
        ephemeral=True
    )

    def check(msg):
        return msg.author == interaction.user and msg.channel == interaction.channel

    while True:
        try:
            msg = await bot.wait_for("message", check=check, timeout=300)  # 5-minute timeout
            if msg.content.lower() == "exit":
                await msg.channel.send(
                    embed=discord.Embed(
                        title="🖥️ TERMINAL SESSION ENDED",
                        description="Session closed successfully.",
                        color=CYBER_COLOR
                    )
                )
                break

            output = await terminal.execute(msg.content)
            await msg.channel.send(
                embed=discord.Embed(
                    title="🖥️ TERMINAL OUTPUT",
                    description=f"```ansi\n\u001b[2;36m{output}\u001b[0m\n```",
                    color=CYBER_COLOR
                )
            )
        except asyncio.TimeoutError:
            await interaction.channel.send(
                embed=discord.Embed(
                    title="⏳ SESSION TIMEOUT",
                    description="No input received for 5 minutes. Session closed.",
                    color=0xFF0000
                )
            )
            break

# ⚡ /neuroshutdown
@bot.tree.command(name="neuroshutdown", description="Initiate system meltdown")
@cyberlock()
async def shutdown(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚠️ SYSTEM MELTDOWN INITIATED",
        description="```diff\n- Shutting down cyberware\n- Purging memory\n```",
        color=0xFF0000
    )
    await interaction.response.send_message(embed=embed)
    await asyncio.sleep(3)
    await bot.close()

# 🔄 /neurostat
@bot.tree.command(name="neurostat", description="Display system vitals")
@cyberlock()
async def stats(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🧠 NEURAL VITALS",
        description=f"""
        ```yaml
        Latency: {round(bot.latency * 1000)}ms
        Guilds: {len(bot.guilds)}
        Users: {len(bot.users)}
        Sessions: {len(terminal.sessions)}
        ```""",
        color=CYBER_COLOR
    )
    await interaction.response.send_message(embed=embed)

# 📜 /help Command
@bot.tree.command(name="help", description="Show all commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🧾 AVAILABLE COMMANDS",
        description="""
        **/cyberterm** – Secure terminal access  
        **/neuroshutdown** – Shutdown system  
        **/neurostat** – View system info  
        **/help** – Show this help panel  
        **/kick** – Kick a user
        **/ban** – Ban a user
        **/mute** – Mute a user
        **/warn** – Warn a user
        **/addrole** – Add a role to a user
        **/removerole** – Remove a role from a user
        **/clear** – Clear messages in a channel
        **/setup_logging** – Set up a logging channel
        **/data_backup** – Backup system data design 
        """,
        color=CYBER_COLOR
    )
    embed.set_footer(text="Entwickelt von Linaru/2b53")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# 🛠️ Moderation Commands
@bot.tree.command(name="kick", description="Kick a user from the server")
@adminlock()
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.kick(reason=reason)
    await interaction.response.send_message(
        embed=discord.Embed(
            title="✅ User Kicked",
            description=f"{member.mention} was kicked. Reason: {reason}",
            color=CYBER_COLOR
        )
    )

@bot.tree.command(name="ban", description="Ban a user from the server")
@adminlock()
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.ban(reason=reason)
    await interaction.response.send_message(
        embed=discord.Embed(
            title="✅ User Banned",
            description=f"{member.mention} was banned. Reason: {reason}",
            color=CYBER_COLOR
        )
    )

@bot.tree.command(name="mute", description="Mute a user in the server")
@adminlock()
async def mute(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await interaction.guild.create_role(name="Muted")
        for channel in interaction.guild.channels:
            await channel.set_permissions(muted_role, speak=False, send_messages=False)
    await member.add_roles(muted_role, reason=reason)
    await interaction.response.send_message(
        embed=discord.Embed(
            title="✅ User Muted",
            description=f"{member.mention} was muted. Reason: {reason}",
            color=CYBER_COLOR
        )
    )

@bot.tree.command(name="warn", description="Warn a user")
@adminlock()
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await interaction.response.send_message(
        embed=discord.Embed(
            title="⚠️ User Warned",
            description=f"{member.mention} was warned. Reason: {reason}",
            color=CYBER_COLOR
        )
    )

# 🛡️ Administration Commands
@bot.tree.command(name="addrole", description="Add a role to a user")
@adminlock()
async def addrole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await interaction.response.send_message(
        embed=discord.Embed(
            title="✅ Role Added",
            description=f"{role.name} was added to {member.mention}",
            color=CYBER_COLOR
        )
    )

@bot.tree.command(name="removerole", description="Remove a role from a user")
@adminlock()
async def removerole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await interaction.response.send_message(
        embed=discord.Embed(
            title="✅ Role Removed",
            description=f"{role.name} was removed from {member.mention}",
            color=CYBER_COLOR
        )
    )

@bot.tree.command(name="clear", description="Clear messages in a channel")
@adminlock()
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(
        embed=discord.Embed(
            title="✅ Messages Cleared",
            description=f"{amount} messages were cleared in this channel.",
            color=CYBER_COLOR
        ),
        ephemeral=True
    )

# 🗄️ /data_backup Command
@bot.tree.command(name="data_backup", description="Backup system data")
@cyberlock()
async def data_backup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🗄️ DATA BACKUP INITIATED",
        description="System data is being backed up securely.",
        color=CYBER_COLOR
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

# 🛠️ Logging Setup
LOGGING_CHANNEL_ID = None

@bot.tree.command(name="setup_logging", description="Set up a logging channel")
@cyberlock()
async def setup_logging(interaction: discord.Interaction):
    class LoggingModal(Modal):
        def __init__(self):
            super().__init__(title="Setup Logging Channel", timeout=120)
            self.channel_id = TextInput(
                label="Enter Channel ID",
                style=TextStyle.short,
                placeholder="123456789012345678",
                required=True
            )
            self.add_item(self.channel_id)

        async def on_submit(self, interaction: discord.Interaction):
            global LOGGING_CHANNEL_ID
            try:
                LOGGING_CHANNEL_ID = int(self.channel_id.value)
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="✅ Logging Channel Set",
                        description=f"Logging channel set to ID: {LOGGING_CHANNEL_ID}",
                        color=CYBER_COLOR
                    ),
                    ephemeral=True
                )
            except ValueError:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="⛔ Invalid Channel ID",
                        description="Please enter a valid numeric channel ID.",
                        color=0xFF0000
                    ),
                    ephemeral=True
                )

    modal = LoggingModal()
    await interaction.response.send_modal(modal)

# 🛠️ Logging Event
@bot.event
async def on_message(message):
    if LOGGING_CHANNEL_ID and message.guild:
        logging_channel = bot.get_channel(LOGGING_CHANNEL_ID)
        if logging_channel and not message.author.bot:
            embed = discord.Embed(
                title="📩 New Message Logged",
                description=f"**Author:** {message.author.mention}\n**Channel:** {message.channel.mention}\n**Content:** {message.content}",
                color=CYBER_COLOR
            )
            await logging_channel.send(embed=embed)
    await bot.process_commands(message)

# 🚀 Startup
# 🛠️ Branding hinzufügen
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    try:
        await bot.tree.sync()  # Global Sync
        print("✅ Commands synced globally.")
    except Exception as e:
        print(f"Error syncing: {e}")

    # Branding-Nachricht in einem bestimmten Kanal senden
    channel = bot.get_channel(SECURE_CHANNEL)
    if channel:
        await channel.send(embed=discord.Embed(
            title="🤖 BOT ONLINE",
            description=f"**{bot.user.name}** ist jetzt aktiv!\nEntwickelt von **Mika**",
            color=CYBER_COLOR
        ))

    # Benutzerdefinierte Statusnachricht setzen
    await bot.change_presence(
        activity=discord.Game(name="coded by 2b53/Linaru"),
        status=discord.Status.online
    )

# 🛡️ Intrusion Detection
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.user.id not in MASTER_IDS:
        if "rm -rf" in str(interaction.data):
            await bot.get_user(MASTER_IDS[0]).send(
                f"INTRUSION ATTEMPT DETECTED FROM {interaction.user}"
            )

# der token ist im .env gespeichert
# bot.run(token.TOKEN)
bot.run(token)

