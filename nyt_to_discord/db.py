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
        with Session(self.engine) as session:
            old_scores = []
            for new_score in scores:
                stmt = (
                    select(CrosswordResult)
                    .where(CrosswordResult.name == new_score.name)
                    .where(CrosswordResult.date == new_score.date)
                )
                old_score = session.scalars(stmt).one_or_none()
                if old_score:
                    old_scores.append(
                        CrosswordResult(old_score.date, old_score.name, old_score.time)
                    )
                    old_score.time = new_score.time
                else:
                    session.add(new_score)

            session.commit()

            return old_scores
