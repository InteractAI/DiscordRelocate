# DiscordRelocate

<img src="assets/DiscordRelocate.png" alt="bot-avatar" width="150" />

------

Relocate your message histories from one discord server to another

## Why

Imagine you are an **administrator** of two servers.\
Now you want to move a text channel from one server to another, but don't want to lose historical messages.\
This bot helps you do that!

## How

This bot helps pack all messages in one channel and recreate them in another channel (append if exists)

**Important**:
* Require user has Admin access on both servers
* `Views` are not transferred
* `Threads` are not transferred
* Only text channels are allowed

## Commands

```
DiscordRelocate:
  channels List text channels on a server by server id
  clear    Clear everything in channel by id (be cautious!)
  pack     Pack everything in a channel (by channel id) and download as zip file
  relocate Relocate messages from one channel to another channel (by channel id)
  servers  List shared servers between me (as admin) and bot
​No Category:
  help     Shows this message

Type !help command for more info on a command.
You can also type !help category for more info on a category.
```


## Deploy

1. Create discord bot application, get bot token.
2. Create file `.env` and paste token in following format:
    ```
    DISCORD_TOKEN={YOUR_TOKEN_HERE}
    ```
3. Initialize virtual environment:
   ```bash
   python3 -m venv venv
   source ./venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```
5. Start bot:
   ```
   python3 main.py
   ```

------

[Add to your server](https://discord.com/api/oauth2/authorize?client_id=1085393893186613368&permissions=137439341632&scope=bot)