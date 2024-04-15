import ccxt
import logging
from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
import responses

# Logging info
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

# Discord Token
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# BingX API
API_KEY = os.getenv("API_KEY")
S_KEY = os.getenv("S_KEY")

# BingX exchange
bingx_exchange = ccxt.bingx({
    'apiKey': API_KEY,
    'secret': S_KEY,
})

# Bot prefix
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Fetch the market price for a given symbol
def fetch_market_price(symbol):
    try:
        ticker = bingx_exchange.fetch_ticker(symbol)
        return ticker['last']
    except ccxt.NetworkError as e:
        logging.error(f"Network error occurred while fetching market price for {symbol}:")
        return None
    except ccxt.ExchangeError as e:
        logging.error(f"Exchange error occurred while fetching market price for {symbol}:")
        return None
    except Exception as e:
        logging.error(f"Error fetching market price for {symbol}: {e}")
        return None
    
@bot.event
async def on_ready():
    logging.info("Bot ready & online!")
    channel = bot.get_channel(1227992905596145694)
    await channel.send("Bot is ready.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Type !help to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing required argument, Check the command prefix.")
    else:
        await ctx.send(f"An error occured: {error}") 

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.mention} ")

@bot.command(aliases=["gm", "morning"])
async  def goodmorning(ctx):
      await ctx.send(f"Goodmorning, {ctx.author.mention} ")

# Fetch ticker data
@bot.command()
async def track(ctx, *, phrase):
    try:
        ticker = bingx_exchange.fetch_ticker(phrase)
        message = (
            f"Ticker for {phrase}\n"
            f"High: {ticker['high']}\n"
            f"Low: {ticker['low']}\n"
        )
        await ctx.send(message)
    except ccxt.NetworkError as e:
        await ctx.send(f"Network error occured: {e}")
    except ccxt.ExchangeError as e:
        await ctx.send(f"Exchange error occured: {e}")
    except Exception as e:
        await ctx.send(f"An error occured: {e}")

open_positions = {}

@bot.command()
async def long (ctx, symbol: 'str', leverage: 'int'):
    try:
        symbol = f"{symbol.upper()}/USDT"
        market_price = fetch_market_price(symbol)
        if market_price:
            entry_price = market_price
            open_positions[symbol] = {'entry_price': entry_price, 'leverage': leverage}
            await ctx.send(f"Opened long position for {symbol} with {leverage}x")
# Log the action
            logging.info(f"Opened long position for {symbol} with {leverage}x")
        else:
            await ctx.send(f"Failed to open long position for {symbol}: Unable to fetch market price")
    except Exception as e:
        await ctx.send(f"An error occured: {e}")
# Execute long position

@bot.command()
async def short (ctx, symbol: 'str', leverage: 'int'):
    try:
        symbol = f"{symbol.upper()}/USDT"
        market_price = fetch_market_price(symbol)
        if market_price:
            entry_price = market_price
            open_positions[symbol] = {'entry_price': entry_price, 'leverage': leverage}
            await ctx.send(f"Opened short position for {symbol} with {leverage}x")
# Log the action
            logging.info(f"Opened short position for {symbol} with {leverage}x")
        else:
            await ctx.send(f"Failed to open short position for {symbol}: Unable to fetch market price")
    except Exception as e:
        await ctx.send(f"An error occured: {e}")
# Execute short position

@bot.command()
async def close (ctx, symbol: 'str'):
    try:
        symbol = f"{symbol.upper()}/USDT"
        market_price = fetch_market_price(symbol)
        if market_price:
            if symbol in open_positions:
                entry_price = open_positions[symbol]['entry_price']
                leverage = open_positions[symbol]['leverage']
                profit = ((market_price - entry_price) * leverage / entry_price) * 100 

                embed = discord.Embed(title="Position Closed", color=0x00ff00)
                embed.add_field(name="Symbol", value=symbol, inline=False)
                embed.add_field(name="Entry Price", value=entry_price, inline=False)
                embed.add_field(name="Current Price", value=market_price, inline=False)
                embed.add_field(name="Profit", value=f"{profit:.2f}%", inline=False)
                
                await ctx.send(embed=embed)
                await ctx.send(f"Closed position for {symbol}. Entry price : {entry_price}, Current price: {market_price}, Profit: {profit}")
# Log the action
                logging.info(f"Closed position for {symbol}")
# Remove the position from open_positions
                del open_positions[symbol]
            else:
                await ctx.send(f"No open position found for {symbol}")
        else:
            await ctx.send(f"Failed to close position for {symbol}: Unable to fetch market price")
    except Exception as e:
        await ctx.send(f"An error occured: {e}")
# Close position

# View open positions
@bot.command()
async def view(ctx):
    try:
        if open_positions:
            embed = discord.Embed(title="Open Positions", color=discord.Color.default())
            position_info = ""
            for symbol, position in open_positions.items():
                entry_price = position ['entry_price']
                leverage = position['leverage']
                market_price = fetch_market_price(symbol)
                if market_price is not None:
                    profit = ((market_price - entry_price) * leverage / entry_price) * 100
                else:
                    profit = None
                position_info += f"Symbol: {symbol}, Entry Price: {entry_price}, Leverage: {leverage}, Profit:{profit}"

# Set color based on position type
                symbol_color = discord.Color.default()
                if bot.command('long'):
                    print("green")
                    symbol_color = discord.Color.green()
                elif bot.command('short'):
                    print("red")
                    symbol_color = discord.Color.red()

                embed = discord.Embed(title="Open Positions", color=symbol_color)
# Embed fields
                embed.add_field(name="Symbol", value=symbol, inline=False)
                embed.add_field(name="Entry Price ", value=entry_price, inline=True)
                embed.add_field(name="Current Price", value=market_price, inline=True)
                embed.add_field(name="Profit", value=f"{profit:.2f}%", inline=True)

            await ctx.send(embed=embed)
        else:
            await ctx.send("No open positions found.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


bot.run(DISCORD_TOKEN)


