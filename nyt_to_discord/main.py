import os

from nyt_to_discord.nyt.Leaderboard import Leaderboard

NYT_COOKIES_ENV_VAR_NAME = "NYT_COOKIES"


def main():
    leaderboard = Leaderboard(os.environ[NYT_COOKIES_ENV_VAR_NAME])


if __name__ == "__main__":
    main()
