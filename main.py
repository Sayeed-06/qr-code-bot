import discord
from discord import app_commands
from discord.ext import commands
import qrcode
from PIL import Image, ImageColor
import os
from dotenv import load_dotenv

# Load the bot token from .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Intents and bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Check if color is valid
def is_valid_color(color: str) -> bool:
    try:
        ImageColor.getrgb(color)
        return True
    except ValueError:
        return False

# Generate QR code with custom color and size
def generate_qr_code(text: str, color: str = "black", size: int = 300) -> str:
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color=color, back_color="white").convert("RGB")
    img = img.resize((size, size), Image.LANCZOS)
    path = "qrcode.png"
    img.save(path)
    return path

# Slash command for QR code
@bot.tree.command(name="qrcode", description="Generate a QR code from text")
@app_commands.describe(
    text="Text to encode into the QR code",
    color="Color of the QR code (default: black)",
    size="Size of the QR code image in pixels (default: 300)"
)
async def qrcode_command(interaction: discord.Interaction, text: str, color: str = "black", size: int = 300):
    await interaction.response.defer()

    if not is_valid_color(color):
        await interaction.followup.send("❌ Invalid color. Use a valid color name or hex code (e.g., red or #00FF00).")
        return
    if not (100 <= size <= 1000):
        await interaction.followup.send("❌ Size must be between 100 and 1000 pixels.")
        return

    image_path = generate_qr_code(text, color=color, size=size)
    await interaction.followup.send(file=discord.File(image_path))

# Sync commands when bot is ready
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"⚠️ Failed to sync commands: {e}")

# Start the bot
bot.run(TOKEN)