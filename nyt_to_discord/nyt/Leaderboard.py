from __future__ import annotations

import datetime
import os
from dataclasses import dataclass
from datetime import timedelta

import requests
from bs4 import BeautifulSoup, PageElement

from nyt_to_discord.nyt import NYT_BASE_URL

NYT_COOKIES_ENV_VAR_NAME = "NYT_COOKIES"

RANKING_BOARD_DATE_CLASS = "lbd-type__date"
RANKING_BOARD_ITEMS_CLASS = "lbd-board__items"

RANKING_BOARD_ROW_CLASS = "lbd-score"
RANKING_BOARD_RANK_CLASS = f"{RANKING_BOARD_ROW_CLASS}__rank"
RANKING_BOARD_NAME_CLASS = f"{RANKING_BOARD_ROW_CLASS}__name"
RANKING_BOARD_TIME_CLASS = f"{RANKING_BOARD_ROW_CLASS}__time"


@dataclass(frozen=True)
class CrosswordResult:
    name: str
    time: datetime.timedelta

    @staticmethod
    def from_row_soup(soup: PageElement) -> CrosswordResult:
        if soup.name != "div" and soup["class"] != RANKING_BOARD_ROW_CLASS:
            raise ValueError("Unexpected soup!")

        name = soup.find(class_=RANKING_BOARD_NAME_CLASS).contents[0].strip()
        (min_str, sec_str) = (
            soup.find(class_=RANKING_BOARD_TIME_CLASS).contents[0].strip().split(":")
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
    def date(self) -> datetime.date:
        if self._date is not None:
            return self._date

        date_str = (
            self._soup.find(RANKING_BOARD_DATE_CLASS).date_element.contents[0].strip()
        )
        # Example str: Monday, May 8, 2023
        date_format = "%A, %B %d, %Y"
        datetime_ = datetime.datetime.strptime(date_str, date_format)
        return datetime.date(
            year=datetime_.year,
            month=datetime_.month,
            day=datetime_.day,
        )
