from __future__ import annotations
import datetime
import os
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup, PageElement

from nyt_to_discord.nyt import NYT_BASE_URL

LEADERBOARD_ENDPOINT = "puzzles/leaderboards"
LEADERBOARD_URL = f"{NYT_BASE_URL}/{LEADERBOARD_ENDPOINT}"

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

        return CrosswordResult(
            soup.find(class_="lbd-score__name").contents[0].strip(),
            soup.find(class_="lbd-score__time").contents[0].strip(),
        )


def scrape():
    headers = {"cookie": os.environ[NYT_COOKIES_ENV_VAR_NAME]}
    r = requests.get(LEADERBOARD_URL, headers=headers)
    if r.status_code != 200:
        raise RuntimeError(r)

    soup = BeautifulSoup(r.text, "html.parser")
    ranking_table = soup.find(class_=RANKING_BOARD_ITEMS_CLASS)
    results = [
        CrosswordResult.from_row_soup(result_soup)
        for result_soup in ranking_table.children
    ]
    return results
