import datetime
import logging
import traceback
from typing import Any

import discord
from discord.ext import tasks
from tabulate import tabulate

from nyt_to_discord.db import DB
from nyt_to_discord.nyt import Leaderboard

_log = logging.getLogger(__name__)


def _async_reportable_error(func):
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except Exception as e:
            try:
                channel = self.get_channel(self._err_channel_id)
                await channel.send(traceback.format_exc())
            except Exception:
                _log.error(
                    f"Unhandled exception in error handler while handling exception from {func.__name__}:\n"
                    f"{traceback.format_exc()}\n"
                    f"Now reraising original exception"
                )
            finally:
                raise e

    return wrapper


class NytDiscordBot(discord.Client):
    MSG_DATE_FORMAT = "%A, %B %-d, %Y"
    REFRESH_SECONDS = 120
    NOTIF_ROLE_ID = 1108558393679040643

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

    async def setup_hook(self) -> None:
        self.refresh_scores.start()

    @tasks.loop(seconds=REFRESH_SECONDS)
    @_async_reportable_error
    async def refresh_scores(self) -> None:
        self._leaderboard = None

        latest_date = self._db.most_recent_date()
        updated_scores = self._db.update_scores(self.leaderboard.scores)
        mini_date = self.leaderboard.date
        if mini_date != latest_date or updated_scores:
            await self._send_or_update_leaderboard_message()

    @refresh_scores.before_loop
    async def _refresh_scores_before(self):
        await self.wait_until_ready()

    async def _send_or_update_leaderboard_message(self) -> None:
        scores = self.leaderboard.scores
        date = datetime.datetime.strftime(self.leaderboard.date, self.MSG_DATE_FORMAT)

        channel = self.get_channel(self._channel_id)
        messages = channel.history(
            after=datetime.datetime.now() - datetime.timedelta(days=3),
            oldest_first=False,
        )
        async for message in messages:
            if message.author.id != self.user.id:
                continue
            if date in message.content:
                await message.edit(content=self._build_leaderboard_msg(date, scores))
                break
        else:
            await channel.send(self._build_leaderboard_msg(date, scores))

        if all(score.time is not None for score in scores):
            await channel.send(
                f"<@&{self.NOTIF_ROLE_ID}> Check it out, all the scores are in!"
            )

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

    @staticmethod
    def _build_leaderboard_msg(date, scores) -> str:
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
