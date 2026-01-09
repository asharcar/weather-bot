import discord
import os
import requests
from datetime import datetime
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("TOKEN")
weatherAPIKey = os.getenv("weatherAPIKey")

if not TOKEN:
    raise RuntimeError("missing bot token, add it please!!")

intents = discord.Intents.default()
client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
    await client.tree.sync()
    print(f"bot online")
    

@client.tree.command(name="weather", description="Find the weather of a city")
@app_commands.describe(city="City name")
async def weather(interaction: discord.Interaction, city: str):
    await interaction.response.defer()

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={weatherAPIKey}&units=metric"
    )

    try:
        response = requests.get(url, timeout=10)
        data = response.json()
    except Exception:
        await interaction.followup.send("api error")
        return

    if response.status_code != 200:
        await interaction.followup.send("False city name")
        return

    temp = data["main"]["temp"]
    feelsLike = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    condition = data["weather"][0]["description"].title()

    icon_thing = data["weather"][0]["icon"]
    icon_url = f"http://openweathermap.org/img/wn/{icon_thing}.png"

    embed = discord.Embed(
        title=f"Weather in {city.title()}",
        color=discord.Color.blue()
    )

    embed.add_field(name="Temperature", value=f"{temp}°C")
    embed.add_field(name="Feels like", value=f"{feelsLike}°C")
    embed.add_field(name="Humidity", value=f"{humidity}%")
    embed.add_field(name="Condition", value=condition, inline=False)

    embed.set_thumbnail(url=icon_url)

    current_time = datetime.now().strftime("%I:%M %p")
    embed.set_footer(text=f"Requested by {interaction.user} • {current_time}")

    await interaction.followup.send(embed=embed)


client.run(TOKEN)