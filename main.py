import os
import discord
from discord.ext import commands

def read_token_from_file(file_path):
    with open(file_path, "r") as file:
        return file.read().strip()

token_path = r"C:\Users\Humpuusi\.vscode\test\token.txt"
token = read_token_from_file(token_path)

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot ready & online!")

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.mention} ")

@bot.command(aliases=["gm", "morning"])
async  def goodmorning(ctx):
      await ctx.send(f"Goodmorning, {ctx.author.mention} ")



bot.run(token)

await ctx.send(f"Tracking: {phrase}")
await ctx.send(f"Ticker for {phrase}: {ticker}", (message))