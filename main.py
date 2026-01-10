import discord
import os
import aiohttp
import asyncio
from datetime import datetime
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("TOKEN")
weatherAPIKey = os.getenv("weatherAPIKey")

if not TOKEN:
    raise RuntimeError("missing bot token, add it please!!")

if not weatherAPIKey:
    raise RuntimeError("missing openweather api key")

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
    params = {
        "q": city,
        "appid": weatherAPIKey,
        "units": "metric"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    await interaction.followup.send(
                        "False city name"
                    )
                    return

                data = await response.json()

    except aiohttp.ClientError:
        await interaction.followup.send("failure with api")
        return
    except asyncio.TimeoutError:
        await interaction.followup.send("timedout")
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