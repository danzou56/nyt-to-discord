from __future__ import annotations
import datetime
from datetime import timedelta
import os
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup, PageElement

from nyt_to_discord.nyt import NYT_BASE_URL


NYT_COOKIES_ENV_VAR_NAME = "NYT_COOKIES"
RANKING_BOARD_ITEMS_CLASS = "lbd-board__items"
RANKING_BOARD_NAME_CLASS = "lbd-score__name"
RANKING_BOARD_TIME_CLASS = "lbd-score__time"


@dataclass(frozen=True)
class CrosswordResult:
    name: str
    time: datetime.timedelta

    @staticmethod
    def from_row_soup(soup: PageElement) -> CrosswordResult:
        if soup.name != "div" and soup["class"] != "lbd-score":
            raise ValueError("Unexpected soup!")

        name = soup.find(class_="lbd-score__name").contents[0].strip()
        (min_str, sec_str) = (
            soup.find(class_="lbd-score__time").contents[0].strip().split(":")
        )
        time = timedelta(minutes=int(min_str), seconds=int(sec_str))
        return CrosswordResult(name, time)


class Leaderboard:
    LEADERBOARD_ENDPOINT = "puzzles/leaderboards"
    LEADERBOARD_URL = f"{NYT_BASE_URL}/{LEADERBOARD_ENDPOINT}"

    def __init__(self):
        self._scores = None
        self._date = None
        self._bs_soup = None

    @property
    def _soup(self) -> BeautifulSoup:
        if self._bs_soup is not None:
            return self._bs_soup

        headers = {"cookie": os.environ[NYT_COOKIES_ENV_VAR_NAME]}
        r = requests.get(self.LEADERBOARD_URL, headers=headers)
        if r.status_code != 200:
            raise RuntimeError(r)

        self._bs_soup = BeautifulSoup(r.text, "html.parser")
        return self._bs_soup

    @property
    def scores(self) -> list[CrosswordResult]:
        if self._scores is not None:
            return self._scores

        ranking_table = self._soup.find(class_=RANKING_BOARD_ITEMS_CLASS)
        self._scores = [
            CrosswordResult.from_row_soup(result_soup)
            for result_soup in ranking_table.children
        ]
        return self._scores

    @property
    def date(self):
        if self._date is not None:
            return self._date

        date_soup = self._soup.find("lbd-type__date")
        return None
