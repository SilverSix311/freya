import asyncio
import datetime
import json
import os
import re
import sys
import discord
import emoji
from discord.ext import commands
from dotenv import load_dotenv

BOT_NAME = "Freya"

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
BOT_CHANNEL_ID = os.getenv("BOT_CHANNEL_ID")
TWITTER_CHANNEL_ID = os.getenv("TWITTER_CHANNEL_ID")
intents = discord.Intents.default()
intents.message_content = True
# client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", intents=intents)
botActivity = discord.Game("with the API.")
configFileLocation = os.path.join(
    os.path.dirname(__file__), "config/config.json")

@bot.event
async def on_ready():
    print(f'{bot.user} has logged in.')


## create bot command !status to return the current time
@bot.command(name="status", help="Returns the current time.")
async def status(ctx):
    now = datetime.datetime.now()
    await ctx.send(now.strftime("%Y-%m-%d %H:%M:%S"))


## create bot command !addnotif with arguments name, cron, channel_id, messageContents and append to notifications array in config/config.json
@bot.command(name="addnotif", help="Add a notification to the Bot.")
async def addnotif(ctx, name, cron, channel_id, messageContents):
    ## check if the message is from the bot
    if message.author == bot.user:
        return
    ## check if the message is from the bot channel
    if message.channel.id != int(BOT_CHANNEL_ID):
        return
    ## check if cron is in "HH:MM" format
    if not re.match(r"([01]?[0-9]|2[0-3]):[0-5][0-9]", cron):
        await ctx.send("Cron must be in HH:MM format.")
        return
    ## check if channel_id is a valid channel
    if not bot.get_channel(int(channel_id)):
        await ctx.send("Channel ID is invalid.")
        return
    ## check if messageContents is a valid string
    if not isinstance(messageContents, str):
        await ctx.send("Message contents must be a string.")
        return
    ## check if name is a valid string
    if not isinstance(name, str):
        await ctx.send("Name must be a string.")
        return
    ## check if name is already in use
    with open(configFileLocation, "r") as configFile:
        configData = json.load(configFile)
        notifications = configData["notifications"]
    for notification in notifications:
        if notification["name"] == name:
            await ctx.send("Name is already in use.")
            return
    ## append to notifications array in config/config.json
    with open(configFileLocation, "r") as configFile:
        configData = json.load(configFile)
        notifications = configData["notifications"]
    notifications.append({
        "name": name,
        "cron": cron,
        "channel_id": channel_id,
        "messageContents": messageContents
    })
    with open(configFileLocation, "w") as configFile:
        json.dump(configData, configFile, indent=4)
    await ctx.send("Notification added.")


## create bot command !delnotif with arguments name and remove from notifications array in config/config.json
@bot.command(name="delnotif", help="Delete a notification from the Bot.")
async def delnotif(ctx, name):
    ## check if the message is from the bot
    if message.author == bot.user:
        return
    ## check if the message is from the bot channel
    if message.channel.id != int(BOT_CHANNEL_ID):
        return
    ## check if name is a valid string
    if not isinstance(name, str):
        await ctx.send("Name must be a string.")
        return
    ## check if name is not in use
    with open(configFileLocation, "r") as configFile:
        configData = json.load(configFile)
        notifications = configData["notifications"]
    for notification in notifications:
        if notification["name"] == name:
            break
    else:
        await ctx.send("Name is not in use.")
        return
    ## remove from notifications array in config/config.json
    with open(configFileLocation, "r") as configFile:
        configData = json.load(configFile)
        notifications = configData["notifications"]
    for notification in notifications:
        if notification["name"] == name:
            notifications.remove(notification)
            break
    with open(configFileLocation, "w") as configFile:
        json.dump(configData, configFile, indent=4)
    await ctx.send("Notification removed.")


## create bot command !listnotif to list all notifications in notifications array in config/config.json
@bot.command(name="listnotif", help="List all notifications from the Bot.")
async def listnotif(ctx):
    ## check if the message is from the bot
    if message.author == bot.user:
        return
    ## check if the message is from the bot channel
    if message.channel.id != int(BOT_CHANNEL_ID):
        return
    ## list all notifications in notifications array in config/config.json
    with open(configFileLocation, "r") as configFile:
        configData = json.load(configFile)
        notifications = configData["notifications"]
    for notification in notifications:
        await ctx.send(
            f"Name: {notification['name']}, Cron: {notification['cron']}, Channel ID: {notification['channel_id']}, Message Contents: {notification['messageContents']}"
        )
    ## check if the message is from the bot
    if message.author == bot.user:
        return
    ## check if the message is from the bot channel
    if message.channel.id != int(BOT_CHANNEL_ID):
        return
    ## check if role_name is a valid string
    if not isinstance(role_name, str):
        await ctx.send("Role name must be a string.")
        return
    ## check if role_name is not in use
    with open(configFileLocation, "r") as configFile:
        configData = json.load(configFile)
        roles = configData["roles"]
    for role in roles:
        if role["role_name"] == role_name:
            break
    else:
        await ctx.send("Role name is not in use.")
        return
    ## remove from roles array in config/config.json
    with open(configFileLocation, "r") as configFile:
        configData = json.load(configFile)
        roles = configData["roles"]
    for role in roles:
        if role["role_name"] == role_name:
            roles.remove(role)
            break
    with open(configFileLocation, "w") as configFile:
        json.dump(configData, configFile, indent=4)
    await ctx.send("Role removed.")
    await role_system()


## create bot command !listrole to list all roles in roles array in config/config.json
@bot.command(name="listrole", help="List all roles from the Bot.")
async def listrole(ctx):
    ## check if the message is from the bot
    if message.author == bot.user:
        return
    ## check if the message is from the bot channel
    if message.channel.id != int(BOT_CHANNEL_ID):
        return
    ## list all roles in roles array in config/config.json
    with open(configFileLocation, "r") as configFile:
        configData = json.load(configFile)
        roles = configData["roles"]
    for role in roles:
        await ctx.send(f"Role name: {role['role_name']}")
    await ctx.send("Roles listed.")


## create bot command !addrole with arguments role, react, description, and add to roles array in config/config.json
@bot.command(name="addrole", help="Add a role to the Bot.")
async def addrole(ctx, role_name, react, description):
    ## check if the message is from the bot
    if message.author == bot.user:
        return
    ## check if the message is from the bot channel
    if message.channel.id != int(BOT_CHANNEL_ID):
        return
    ## check if role_name is a valid string
    if not isinstance(role_name, str):
        await ctx.send("Role name must be a string.")
        return
    ## check if role_name is already in use
    with open(configFileLocation, "r") as configFile:
        configData = json.load(configFile)
        roles = configData["roles"]
    for role in roles:
        if role["role_name"] == role_name:
            await ctx.send("Role name is already in use.")
            return
    ## check if react is a valid string
    if not isinstance(react, str):
        await ctx.send("React must be a string.")
        return
    ## check if description is a valid string
    if not isinstance(description, str):
        await ctx.send("Description must be a string.")
        return
    ## append to roles array in config/config.json
    with open(configFileLocation, "r") as configFile:
        configData = json.load(configFile)
        roles = configData["roles"]
    roles.append({
        "react": react,
        "react_id": 0,
        "role": role_name,
        "description": description,
        "role_id": 0
    })
    with open(configFileLocation, "w") as configFile:
        json.dump(configData, configFile, indent=4)
    await ctx.send("Role added.")


## create bot command !delrole with arguments role and remove from roles array in config/config.json
@bot.command(name="delrole", help="Delete a role from the Bot.")
async def delrole(ctx, role_name):
    ## check if the message is from the bot
    if message.author == bot.user:
        return
    ## check if the message is from the bot channel
    if message.channel.id != int(BOT_CHANNEL_ID):
        return
    ## check if role_name is a valid string
    if not isinstance(role_name, str):
        await ctx.send("Role name must be a string.")
        return
    ## check if role_name is not in use
    with open(configFileLocation, "r") as configFile:
        configData = json.load(configFile)
        roles = configData["roles"]
    for role in roles:
        if role["role_name"] == role_name:
            break
    else:
        await ctx.send("Role name is not in use.")
        return
    ## remove from roles array in config/config.json
    with open(configFileLocation, "r") as configFile:
        configData = json.load(configFile)
        roles = configData["roles"]
    for role in roles:
        if role["role_name"] == role_name:
            roles.remove(role)
            break
    with open(configFileLocation, "w") as configFile:
        json.dump(configData, configFile, indent=4)
    await ctx.send("Role removed.")


## create bot command !restart to restart the bot
@bot.command(name="restart", help="Restart the Bot.")
async def restart(ctx):
    ## check if the message is from the bot
    if message.author == bot.user:
        return
    ## check if the message is from the bot channel
    if message.channel.id != int(BOT_CHANNEL_ID):
        return
    ## restart the bot
    await ctx.send("Restarting...")
    os.execl(sys.executable, sys.executable, *sys.argv)


## create bot command !shutdown to shutdown the bot
## only the role "Submit to Me" can use this command
@bot.command(name="shutdown", help="Shutdown the Bot.")
async def shutdown(ctx):
    ## check if the message is from the bot
    if message.author == bot.user:
        return
    ## check if the message is from the bot channel
    if message.channel.id != int(BOT_CHANNEL_ID):
        return
    ## check if the message is from the role "Submit to Me"
    if "Submit to Me" not in [role.name for role in message.author.roles]:
        return
    ## shutdown the bot
    await ctx.send("Shutting down...")
    await bot.logout()


## create bot command !role to list roles of the author
@bot.command(name="roles", help="List roles of the author.")
async def role(ctx):
    ## check if the message is from the bot
    if message.author == bot.user:
        return
    ## check if the message is from the bot channel
    if message.channel.id != int(BOT_CHANNEL_ID):
        return
    ## list roles of the author
    for role in message.author.roles:
        await ctx.send(f"Role: {role.name}")


## create bot command !reload to reload the reaction roles
@bot.command(name="reload", help="Reload the reaction roles.")
async def reload(ctx):
    ## reload the reaction roles
    await ctx.send("Reloading...")
    await role_system()


## create bot command !listcommands to list all commands
@bot.command(name="listcommands", help="List all commands.")
async def help(ctx):
    ## for loop to list all commands and append to helpMessage
    helpMessage = ""
    for command in bot.commands:
        helpMessage += f"Command: {command.name}\n"
    ## send helpMessage as a message to the author
    await ctx.send(helpMessage)


## create command to build message array from

## create bot command !testnotify with arguments nameNotify and search for the name in the config/config.json
@bot.command(name="testnotify", help="Test the notification system.")
async def testnotify(ctx, nameNotify):
    ## load notification data from config/config.json
    with open(configFileLocation, "r") as configFile:
        configData = json.load(configFile)
        notifications = configData["notifications"]
        ## if notification name is found, send message containing description
        for notification in notifications:
            if notification["name"] == nameNotify:
                await ctx.send(f"Notification: {notification['description']}")
                return
    ## if notification name is not found, send message containing error
    await ctx.send(notification['name'] + " notification not found.")


## create function to send messages at specific time intervals to notification channel in config/config.json
async def notify_system():
    ## read config/config.json
    with open(configFileLocation, "r") as configFile:
        configData = json.load(configFile)
        notificationChannel = configData["notification_channel"]
        notifications = configData["notifications"]
    ## set nextMinute to how many seconds till next minute
    nextMinute = 60 - datetime.datetime.now().second
    ## wait for next minute
    await asyncio.sleep(nextMinute)
    ## loop forever
    while True:
        ## loop through notifications
        for notification in notifications:
            ## get current time
            now = datetime.datetime.now()
            ## check if current MM matches notification MM
            if now.minute == notification["minute"]:
                ## send notification to notification channel
                await bot.get_channel(int(notificationChannel)).send(notification["message"])
        await asyncio.sleep(60)

## create role_system function to load roles from config/config.json and add reactions to the bot message
async def role_system():
    global roles, roleMessage
    channel = await bot.fetch_channel(CHANNEL_ID)
    roles = await bot.guilds[0].fetch_roles()
    map_role_ID(roles)
    map_emoji_ids()

    if role_message_exists():
        roleMessage = get_message_id()
        if roleMessage != 0:
            try:
                roleMessage = await channel.fetch_message(roleMessage)
            except discord.errors.NotFound:
                roleMessage = await channel.send(content=build_message())
                store_message_id(roleMessage.id)
    else:
        roleMessage = await channel.send(content=build_message())
        store_message_id(roleMessage.id)

        for react in roleMessage.reactions:
            await react.remove(bot.user)

        default_reacts = get_all_reacts()
        for react in default_reacts:
            await roleMessage.add_reaction(emoji.emojize(react, language='alias'))


def interpret_emoji(payload):
    """
    Handle logic from both add/remove emoji reacts here. DRY you idiot.
    """
    if payload.emoji.is_custom_emoji():
        emoji_name = f":{payload.emoji.name}:"
    else:
        emoji_name = emoji.demojize(payload.emoji.name)

    role_ID = get_role_ID(emoji_name)

    for role in roles:
        if role_ID == role.id:
            return role

    return None


def eligible_for_action(payload):
    user = bot.get_user(payload.user_id)
    # If the user reacting is the bot, return
    if user == bot.user:
        return False
    # If the reaction is not on the correct message for manging roles, return.
    # Defined in config/config.json
    if get_message_id() != payload.message_id:
        return False
    return True


def map_emoji_ids():
    """
    Match Emoji ID's from the server with emojis in the config
    """
    with open(configFileLocation, "r") as settingsFile:
        settingsData = json.load(settingsFile)
        configuredRoles = settingsData["roles"]

    for item in configuredRoles:
        if item["react_id"] == 0:
            for custom_emoji in bot.emojis:
                if custom_emoji.name in item["react"]:
                    item["react_id"] = custom_emoji.id
        else:
            continue

    settingsData["roles"] = configuredRoles

    with open(configFileLocation, "w") as configFile:
        json.dump(settingsData, configFile, indent=4)


def role_message_exists():
    """
    Determine if a role message has been saved to the config
    Return Bool
    """
    with open(configFileLocation, "r") as configFile:
        configData = json.load(configFile)
        message_id = configData["role_message_id"]
    if message_id == 0:
        return False
    else:
        return True


def get_message_id():
    """
    Retreive the message ID saved in the config file
    Return Int(message_id)
    """
    with open(configFileLocation, "r") as configFile:
        configData = json.load(configFile)
        message_id = configData["role_message_id"]
    return message_id


def store_message_id(message_id):
    with open(configFileLocation, "r") as configFile:
        configData = json.load(configFile)

    configData["role_message_id"] = message_id
    with open(configFileLocation, "w") as configFile:
        json.dump(configData, configFile, indent=4)


def get_role_ID(react):
    react = emoji.demojize(react)
    with open(configFileLocation, "r") as configFile:
        configData = json.load(configFile)
        configuredRoles = configData["roles"]
    for item in configuredRoles:
        if item["react"] == react:
            return item["role_id"]


def map_role_ID(roles):
    """
    Match Role ID's from the server with Role names in the config
    roles = [Role objects]
    """
    with open(configFileLocation, "r") as settingsFile:
        settingsData = json.load(settingsFile)
        configuredRoles = settingsData["roles"]

    for item in configuredRoles:
        if item["role_id"] == 0:
            for role in roles:
                if role.name == item["role"]:
                    item["role_id"] = role.id
        else:
            continue

    settingsData["roles"] = configuredRoles

    with open(configFileLocation, "w") as configFile:
        json.dump(settingsData, configFile, indent=4)


def build_message():
    """
    Build the multi-line message combining reactions and descriptions
    from the config. 
    Return str(finalMessage)
    """
    finalMessage = """\n"""
    messageLines = []
    with open(configFileLocation) as settingsFile:
        settingsData = json.load(settingsFile)
        configuredRoles = settingsData["roles"]

    for item in configuredRoles:
        react = item["react"]
        for custom_emoji in bot.emojis:
            if custom_emoji.name in react:
                react = f"<{item['react']}{item['react_id']}>"
        roleDescription = item["description"]
        messageLines.append(f"{react} {roleDescription}")

    return finalMessage.join(messageLines)


def get_all_reacts():
    """
    Get all the reaction names from the config file
    Return [reacts]
    """
    reacts = []
    with open(configFileLocation) as settingsFile:
        settingsData = json.load(settingsFile)
        configuredRoles = settingsData["roles"]

    for item in configuredRoles:
        if item["react_id"] != 0:
            reacts.append(f"<{item['react']}{item['react_id']}>")
        else:
            reacts.append(item["react"])

    return reacts

@bot.event
async def on_raw_reaction_add(payload):
    if eligible_for_action(payload):
        role = interpret_emoji(payload)
        if role == None:
            return
        await payload.member.add_roles(role)
        print(
            f"The user {payload.member} was added to the role {role.name}")


@bot.event
async def on_raw_reaction_remove(payload):
    if eligible_for_action(payload):
        role = interpret_emoji(payload)
        if role == None:
            return
        guild = bot.get_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)
        await member.remove_roles(role)
        print(
            f"The user {member.name} was removed from the role {role.name}")


@bot.event
async def on_ready():
    global roles, roleMessage
    # Set bot status in the server
    await bot.change_presence(activity=botActivity)
    await role_system()

bot.run(DISCORD_TOKEN)