import discord
import requests
import gspread
from discord.ext import commands
import logging
import sys

# Set verification database
gc = gspread.service_account(filename="HRFSheets-b9a1fbb500e8.json")


# Set command prefix and description
with open("token.txt") as fp:
    TOKEN = fp.read().strip()
bot = commands.Bot(command_prefix="%")

# Initiate logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

@bot.listen("on_start")
async def on_start_print_bot_info():
    """Prints out some info about the bot once it's ready to go"""
    owner = (await bot.application_info()).owner

    print(dedent(
        f"""
        I'm ready to go!
        Logged in as: {bot.user}
        User ID: {bot.user.id}
        Owner: {owner}
        """
        ))

@bot.listen("on_message")
async def on_mention_reply_prefix(message: discord.Message) -> None:
    """Replies the bot's prefix when mentioned"""
    if bot.user.mentioned_in(message):
        await messcage.channel.send(f"**Hiya! My prefix is `{bot.command_prefix}`.**")

@bot.command(
    name="verify",aliases=["v"],brief="Verify nation status."
)
async def verify(ctx, nation_to_verify: str, verify_token: str):
        """
        Verifies nation, attaches nation to user, and saves in database.
        Database lookup coming soon.
        """
        sh = gc.open_by_key("1eQQK6QcKYq7duUWYWcJJjs53uHJ1XWmeT4tsUqTn72Q")
        ws = sh.worksheet("database")
        headers = {
       'User-Agent' : "Email: aav.verinhall@gmail.com, Nation: United Calanworie"
        }

        payload = {
           'a' :'verify' , 'nation' : nation_to_verify, "checksum" : verify_token
        }

        response = requests.get('https://www.nationstates.net/cgi-bin/api.cgi', headers=headers, params=payload)

        verified = response.text

        if int(verified) == 1:
            await ctx.send(f"User is verified!")
            role = discord.utils.get(ctx.guild.roles, name='Verified')
            await ctx.author.add_roles(role,reason="User has been verified",atomic=True)
            id = str(ctx.author.id)
            username = str(ctx.author.mention)
            val = ws.acell('E1').value
            ws.update('A'+str(val),nation_to_verify)
            ws.update('B'+str(val),verify_token)
            ws.update('C'+str(val),username)
            ws.update('D'+str(val),id)
            ws.add_rows(1)

        elif int(verified) == 0:
           await ctx.send(f"User is not verified! Is the token valid?")
@bot.command(
    name="ping", brief="Returns ping, can be used to check latency."
)
async def ping(ctx):
    await ctx.send('Pong! {0}s'.format(round(bot.latency, 1)))

@bot.command(
    name="queryDatabase", alias=["qd, query"], brief="Queries database by nation, discord mention, or discord ID"
)
async def queryDatabase(ctx, name : str):
    """
    @mention a user to get their nation and Discord ID
    Use a nation name to get their discord ID and @mention
    Use a discord ID to get their nation and @mention
    When supplying a nation name, you must enclose it in quotes if the nation name has (a) space(s)
    """
    sh = gc.open_by_key("1eQQK6QcKYq7duUWYWcJJjs53uHJ1XWmeT4tsUqTn72Q")
    ws = sh.worksheet("database")
    cell = ws.find(name)
    values_list = ws.row_values(cell.row)
    nation = values_list[0]
    discord_mention = values_list[2]
    discord_id = values_list[3]
    await ctx.send(f"Nation Name: {nation}")
    await ctx.send(f"Discord Name: {discord_mention}")
    await ctx.send(f"Discord ID: {discord_id}")


#@bot.command(
#    name="editNickname", brief="Changes user nickname"
#)
#async def editNickname(ctx, member : discord.Member, new_nick : str):
#    await member.edit(member,reason=None, nick)
#    await ctx.send("Nickname successfully changed.")
# Owner only commands below here
async def is_owner(ctx):
    return ctx.author.id == 247818655742558218
@bot.command(
    name="shutdown", alias=["terminate","sd"], brief="Shuts down bot."
)
@commands.check(is_owner)
async def shutdown(ctx):
    await ctx.send(f"Shutting down...")
    sys.exit()

# Single use setup command
@bot.command(
    name="prepareDatabase", alias=["pd","pdata"], brief="Sets up verification database for server. Defaults to Hartfelden Verification Database."
)
@commands.check(is_owner)
async def prepareDatabase(ctx, key : str="1eQQK6QcKYq7duUWYWcJJjs53uHJ1XWmeT4tsUqTn72Q", database : str = "Verification Database"):
    """
    Prepares the verification database for the server. It defaults to the Hartfelden Verification Database if no key and name are provided.
    If you are planning to use a different database, you need to update the Google Sheets Service Account accordingly, and provide a new
    key.json file. This command may only be run by the owner of the bot, also known as the person who owns the bot token associated with
    the bot instance.
    """
    # Sets up verification database.
    sh = gc.open_by_key(key)
    ws = sh.add_worksheet(title="database", rows="1", cols="4")
    ws.update('A1',"Nation")
    ws.update('B1',"Token")
    ws.update('C1',"Discord Mention")
    ws.update('D1',"Discord UID")
bot.run(TOKEN)
