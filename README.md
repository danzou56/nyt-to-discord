# nyt-to-discord

A bot that takes your NYT Mini leaderboard and sends a message with it in Discord.

## Setup

Create a file `.env` in the root of the repository with the following values:

```
NYT_COOKIES=<cookie-content>
DISCORD_BOT_TOKEN=<bot-token>
DISCORD_CHANNEL_ID=<channel-id>
```

* `NYT_COOKIES`
  1. Go to the [NYT login page](https://myaccount.nytimes.com/auth/login) in an incognito window
  2. Login
  3. Open the developer console and go to the "Network" tab
  4. Go to the [NYT Mini leaderboard page](https://www.nytimes.com/puzzles/leaderboards)
  5. Select the first request in the developer console; it should be called "leaderboards"
  6. Under the request headers, there should be an entry for cookie
  7. Store that value in `NYT_COOKIES`; make sure to single quote the string/look out for characters that need to be escaped
* `DISCORD_BOT_TOKEN` - obtain a discord bot token
* `DISCORD_CHANNEL_ID` - obtain the channel ID where you want the message to be sent