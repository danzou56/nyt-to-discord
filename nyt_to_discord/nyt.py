from __future__ import annotations

import datetime
from datetime import timedelta
from typing import Optional

import requests
from bs4 import BeautifulSoup, PageElement
from requests.adapters import HTTPAdapter, Retry
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, Mapped, mapped_column

RANKING_BOARD_DATE_CLASS = "lbd-type__date"
RANKING_BOARD_ITEMS_CLASS = "lbd-board__items"

RANKING_BOARD_ROW_CLASS = "lbd-score"
RANKING_BOARD_RANK_CLASS = f"{RANKING_BOARD_ROW_CLASS}__rank"
RANKING_BOARD_NAME_CLASS = f"{RANKING_BOARD_ROW_CLASS}__name"
RANKING_BOARD_TIME_CLASS = f"{RANKING_BOARD_ROW_CLASS}__time"


class Leaderboard:
    NYT_BASE_URL = "https://www.nytimes.com"
    LEADERBOARD_ENDPOINT = "puzzles/leaderboards"
    LEADERBOARD_URL = f"{NYT_BASE_URL}/{LEADERBOARD_ENDPOINT}"

    __session = requests.Session()
    __session.mount(
        "https://",
        HTTPAdapter(
            max_retries=Retry(
                total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504]
            )
        ),
    )

    def __init__(self, cookies):
        self._scores = None
        self._date = None
        self._bs_soup = None
        self._cookies = cookies

    @property
    def _soup(self) -> BeautifulSoup:
        if self._bs_soup is not None:
            return self._bs_soup

        headers = {"cookie": self._cookies}
        r = self.__session.get(self.LEADERBOARD_URL, headers=headers)
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
            CrosswordResult.from_row_soup(self.date, result_soup)
            for result_soup in ranking_table.children
        ]
        return self._scores

    @property
    def date(self) -> datetime.date:
        if self._date is not None:
            return self._date

        date_str = self._soup.find(class_=RANKING_BOARD_DATE_CLASS).contents[0].strip()
        # Example str: Monday, May 8, 2023
        date_format = "%A, %B %d, %Y"
        datetime_ = datetime.datetime.strptime(date_str, date_format)
        return datetime.date(
            year=datetime_.year,
            month=datetime_.month,
            day=datetime_.day,
        )


class Base(DeclarativeBase):
    pass


class CrosswordResult(MappedAsDataclass, Base):
    __tablename__ = "results"

    date: Mapped[datetime.date] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(primary_key=True)
    time: Mapped[Optional[datetime.timedelta]]

    @staticmethod
    def from_row_soup(date: datetime.date, soup: PageElement) -> CrosswordResult:
        if soup.name != "div" and soup["class"] != RANKING_BOARD_ROW_CLASS:
            raise ValueError("Unexpected soup!")

        name = soup.find(class_=RANKING_BOARD_NAME_CLASS).contents[0].strip()
        try:
            (min_str, sec_str) = (
                soup.find(class_=RANKING_BOARD_TIME_CLASS)
                .contents[0]
                .strip()
                .split(":")
            )
            time = timedelta(minutes=int(min_str), seconds=int(sec_str))
            return CrosswordResult(date, name, time)
        except:
            return CrosswordResult(date, name, None)
