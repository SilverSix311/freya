## first time run of freya bot
## ask user for discord bot token by running token.py

## define start_bot() function to start the bot
## run function get_token() from token.py to get the bot's token and store it in TOKEN variable

def start_bot():
    import token
    TOKEN = token.get_token()
    import bot
    bot.client.run(TOKEN)

## run start_bot() function
start_bot()