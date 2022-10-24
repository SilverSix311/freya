import discord
import os
import sys
import emoji
import json
import DiscordUtils
import re
from dotenv import load_dotenv
from discord.ext import commands


BOT_NAME = "Freya"

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
BOT_CHANNEL_ID = os.getenv("BOT_CHANNEL_ID")
TWITTER_CHANNEL_ID = os.getenv("TWITTER_CHANNEL_ID")
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", intents=intents)
botActivity = discord.Game("with the API.")
configFileLocation = os.path.join(
    os.path.dirname(__file__), "config/config.json")

@client.event
async def on_ready():
    print(f'{client.user} has logged in.')

@client.event
async def on_message(message):
    global roleMessage
    ## If message.id == "BOT_CHANNEL_ID"
    if message.channel.id == int(BOT_CHANNEL_ID):
    ## if message is from bot, return
        if message.author == client.user:
            return
        if message.content == "!restart":
            await message.channel.send("Restarting...")
            python = sys.executable
            os.execl(python, python, *sys.argv)
        if message.content == "!roles":
            ## List roles of the author
            author = message.author
            roles = author.roles
            roles = [role.name for role in roles]
            roles = "\n".join(roles)
            await message.channel.send(f"Your roles are:\n{roles}")
            return
        ## if message.content contains "!addrole" then set new_role variable to the 2nd word in the message and set new_description variable to the 3rd word in the message and set new_react variable to the 4th word in the message
        if "!addrole" in message.content:
            if message.content.split()[1] == "help":
                await message.channel.send("Usage: !addrole Test_Role Test_Description <:gimmetail:872298447393419294>")
                return
            ## if 4th word in message.content exists send message "Usage: !addrole Test_Role Test_Description <:gimmetail:872298447393419294>"
            if len(message.content.split()) > 4:
                await message.channel.send("You entered incorrect arguments. Usage: !addrole Test_Role Test_Description <:gimmetail:872298447393419294>")
                return
            new_role = message.content.split()[1]
            new_description = message.content.split()[2]
            new_react = message.content.split()[3]
            new_react_emoji = re.sub(r'[0-9<>]', '', new_react)

            roles = message.guild.roles
            if new_role in roles:
                await message.channel.send("Role already exists.")
            else:
                # Get the ID of the emoji from the server and set it to new_react_id
                for custom_emoji in client.emojis:
                    if custom_emoji.name in new_react:
                        new_react_id = custom_emoji.id
                        # Add the new role to the config file
                        with open(configFileLocation, "r") as configFile:
                            configData = json.load(configFile)
                            configuredRoles = configData["roles"]
                        configuredRoles.append(
                            {
                                "react": new_react_emoji,
                                "react_id": new_react_id,
                                "role": new_role,
                                "description": new_description,
                                "role_id": 0
                            }
                        )
                configData["roles"] = configuredRoles
                with open(configFileLocation, "w") as configFile:
                    json.dump(configData, configFile, indent=4)
                # Send a message to the channel to confirm the role has been added
                await message.channel.send(f"Added role {new_role} to the config file.")
                return
                
        ## Remove a role from the config file
        if "!delrole" in message.content:
            if message.author == client.user:
                return
            ## if 2nd word in message.content exists send message "Usage: !delrole Test_Role"
            if len(message.content.split()) > 2:
                await message.channel.send("You entered incorrect arguments. Usage: !delrole Test_Role")
                return
            role_to_remove = message.content.split()[1]
            ## check if role_to_remove is in the config file
            with open(configFileLocation, "r") as configFile:
                configData = json.load(configFile)
                configuredRoles = configData["roles"]
            for role in configuredRoles:
                if role_to_remove == role["role"]:
                    configuredRoles.remove(role)
                    configData["roles"] = configuredRoles
                    with open(configFileLocation, "w") as configFile:
                        json.dump(configData, configFile, indent=4)
                    await message.channel.send(f"Removed role {role_to_remove} from the config file.")
                    return


        ## List all roles in the config file
        if "!listroles" in message.content:
            with open(configFileLocation, "r") as configFile:
                configData = json.load(configFile)
                configuredRoles = configData["roles"]
            configuredRoles = [role["role"] for role in configuredRoles]
            configuredRoles = "\n".join(configuredRoles)
            await message.channel.send(f"Configured roles are:\n{configuredRoles}")
            return

        ## Reload reaction message
        if "!reload" in message.content:
            if message.author == client.user:
                return
            await message.channel.send("Reloading reaction message...")
            channel = await client.fetch_channel(CHANNEL_ID)
            roles = await client.guilds[0].fetch_roles()
            map_role_ID(roles)
            map_emoji_ids()

            if role_message_exists():
                roleMessage = get_message_id()
                if roleMessage != 0:
                    try :
                        roleMessage = await channel.fetch_message(roleMessage)
                    except discord.errors.NotFound:
                        roleMessage = await channel.send(content=build_message())
                        store_message_id(roleMessage.id)
                await roleMessage.edit(content=build_message())
            else:
                roleMessage = await channel.send(content=build_message())
                store_message_id(roleMessage.id)
            # Remove all reactions from the bot on the message.
            for react in roleMessage.reactions:
                await react.remove(client.user)
        
            # Add a reaction from the bot for each in the config
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
    user = client.get_user(payload.user_id)
    # If the user reacting is the bot, return
    if user == client.user:
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
            for custom_emoji in client.emojis:
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
        for custom_emoji in client.emojis:
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

@client.event
async def on_raw_reaction_add(payload):
    if eligible_for_action(payload):
        role = interpret_emoji(payload)
        if role == None:
            return
        await payload.member.add_roles(role)
        print(
            f"The user {payload.member} was added to the role {role.name}")


@client.event
async def on_raw_reaction_remove(payload):
    if eligible_for_action(payload):
        role = interpret_emoji(payload)
        if role == None:
            return
        guild = client.get_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)
        await member.remove_roles(role)
        print(
            f"The user {member.name} was removed from the role {role.name}")


@client.event
async def on_ready():
    global roles, roleMessage
    # Set bot status in the server
    await client.change_presence(activity=botActivity)
    channel = await client.fetch_channel(CHANNEL_ID)
    roles = await client.guilds[0].fetch_roles()
    map_role_ID(roles)
    map_emoji_ids()

    if role_message_exists():
        roleMessage = get_message_id()
        if roleMessage != 0:
            try :
                roleMessage = await channel.fetch_message(roleMessage)
            except discord.errors.NotFound:
                roleMessage = await channel.send(content=build_message())
                store_message_id(roleMessage.id)
        await roleMessage.edit(content=build_message())
    else:
        roleMessage = await channel.send(content=build_message())
        store_message_id(roleMessage.id)

    # Remove all reactions from the bot on the message.
    for react in roleMessage.reactions:
        await react.remove(client.user)

    # Add a reaction from the bot for each in the config
    default_reacts = get_all_reacts()
    for react in default_reacts:
        await roleMessage.add_reaction(emoji.emojize(react, language='alias'))



client.run(DISCORD_TOKEN)