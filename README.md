# DiscordRelocate

<img src="assets/DiscordRelocate-v2.png" alt="bot-avatar" width="150" />

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
* Replies won't get linked

## Commands

```
DiscordRelocate:
  channels List text channels on a server by server id
  clear    Clear everything in channel by id (be cautious!)
  pack     Pack everything in a channel (by channel id) and download as zip file
  relocate Relocate messages from one channel to another channel (by channel id)
  servers  List shared servers between me (as admin) and bot
No Category:
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
   python3 discord-relocate.py
   ```

------

## Command Example

First, list the server IDs where the bot is on and you are an administrator:
```
!servers
```

Next checkout the channel IDs that you want to relocate.\
Assuming your server ID is `000000000` as example:
```
!channels 000000000
```

Select the channel ID to relocate from and the channel ID to relocate to.\
Assuming you want to move messages from channel `123456789` to channel `987654321`:
```
!relocate 123456789 987654321
```

**Important**\
Make sure the bot has access to messages on both channels!

------

[Add to your server]() (link no longer available).\
We recommend running this bot locally for the security of your messages.