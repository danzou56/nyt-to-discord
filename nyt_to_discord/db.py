import copy
import datetime
import os.path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from nyt import CrosswordResult
from nyt_to_discord import ROOT_DIR


class DB:
    DB_NAME = "nyt_to_discord"
    DB_PATH = os.path.abspath(os.path.join(ROOT_DIR, "../", f"{DB_NAME}.sqlite"))

    def __init__(self):
        self.engine = create_engine(f"sqlite+pysqlite:///{DB.DB_PATH}", echo=True)

    def update_scores(self, scores: list[CrosswordResult]) -> list[CrosswordResult]:
        """Add scores into database, returning previous scores if they already existed"""
        scores = copy.deepcopy(scores)
        with Session(self.engine) as session:
            old_scores = []
            for new_score in scores:
                stmt = (
                    select(CrosswordResult)
                    .where(CrosswordResult.name == new_score.name)
                    .where(CrosswordResult.date == new_score.date)
                )
                old_score = session.scalars(stmt).one_or_none()
                if old_score is None:
                    session.add(new_score)
                elif old_score.time != new_score.time:
                    old_scores.append(
                        CrosswordResult(old_score.date, old_score.name, old_score.time)
                    )
                    old_score.time = new_score.time

            session.commit()

            return old_scores

    def most_recent_date(self) -> datetime.date:
        with Session(self.engine) as session:
            results_table = CrosswordResult.__table__
            stmt = select(results_table.c.date).order_by(results_table.c.date.desc())
            return session.scalars(stmt).first()
