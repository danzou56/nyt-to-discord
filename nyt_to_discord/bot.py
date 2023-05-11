import datetime
import logging
import traceback
from typing import Any

import discord
from tabulate import tabulate

from db import DB
from nyt import Leaderboard

_log = logging.getLogger(__name__)


class NytDiscordBot(discord.Client):
    MSG_DATE_FORMAT = "%A, %B %-d, %Y"

    def __init__(
        self, nyt_cookies: str, channel_id: int, err_channel_id: int, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self._channel_id = channel_id
        self._err_channel_id = err_channel_id
        self._nyt_cookies = nyt_cookies
        self._leaderboard = None
        self._db = DB()

    @property
    def leaderboard(self) -> Leaderboard:
        if self._leaderboard is not None:
            return self._leaderboard

        self._leaderboard = Leaderboard(self._nyt_cookies)
        return self._leaderboard

    async def on_ready(self) -> None:
        mini_date = datetime.datetime.strftime(
            self.leaderboard.date, self.MSG_DATE_FORMAT
        )
        mini_date_prev = datetime.datetime.strftime(
            self.leaderboard.date - datetime.timedelta(days=1), self.MSG_DATE_FORMAT
        )
        message_content = self._build_leaderboard_msg()

        channel = self.get_channel(self._channel_id)
        messages = channel.history(
            after=datetime.datetime.now() - datetime.timedelta(days=3),
            oldest_first=False,
        )
        async for message in messages:
            if message.author.id != self.user.id:
                continue
            if mini_date in message.content:
                await message.edit(content=message_content)
                await self.close()
                return
            if mini_date_prev in message.content:
                break

        await channel.send(message_content)
        await self.close()

    async def on_error(self, event_method: str, /, *args: Any, **kwargs: Any) -> None:
        traceback.print_exc()
        _log.info(f"Trying to report error to channel id {self._err_channel_id}")
        try:
            channel = self.get_channel(self._err_channel_id)
            await channel.send(traceback.format_exc())
        except:
            _log.error(
                f"Encountered an error while trying to report a previous error to {self._err_channel_id}; "
                f"previous error may now be masked during super class on_error invocation"
            )
            await super().on_error(event_method, *args, **kwargs)
        finally:
            await self.close()

    def _build_leaderboard_msg(self) -> str:
        scores = self.leaderboard.scores
        self._db.update_scores(scores)
        date = datetime.datetime.strftime(self.leaderboard.date, self.MSG_DATE_FORMAT)
        formatted_table = tabulate(
            [
                [
                    rank + 1,
                    score.name,
                    ":".join(str(score.time).split(":")[1:]) if score.time else "N/A",
                ]
                for (rank, score) in enumerate(scores)
            ],
            headers=["Rank", "Name", "Time"],
            tablefmt="simple_grid",
        )
        return f"Mini results for {date} 👀\n```{formatted_table}```"
