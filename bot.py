import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

# تفعيل intents صريحة (مطلوبة لمعالجة بعض الأحداث)
intents = discord.Intents.default()
intents.message_content = True  # لازم عشان تقدر تقرأ محتوى الرسائل في on_message

activity = discord.Activity(type=discord.ActivityType.watching, name="Avatars")
bot = commands.Bot(command_prefix="!", activity=activity, intents=intents)

@bot.event
async def on_ready() -> None:
    print(f"Bot is ready! Logged in as {bot.user} (ID: {bot.user.id})")
    print(f"Invite link: https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot\n")

@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return

    if message.content.lower() == "hello":  # جعلها غير حساسة لحالة الحروف
        await message.channel.send("hi")

    await bot.process_commands(message)

cogs_list = [
    "misc",
    "psn",
    "psprices"
]

if __name__ == "__main__":
    for cog in cogs_list:
        try:
            print(f"Loading cog: {cog}...")
            bot.load_extension(f"cogs.{cog}")
            print(f"Loaded cog: {cog}.")
        except Exception as e:
            print(f"Failed to load cog {cog}: {e}")
    
    print("\nStarting bot...")
    bot.run(os.getenv("TOKEN"))
