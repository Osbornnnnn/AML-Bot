import pytz
from envparse import env


TIMEZONE = env.str("TZ", default=pytz.timezone("Europe/Moscow"))
TELEGRAM_TOKEN = env.str("TELEGRAM_TOKEN", default="")
DATABASE_URI = env.str("MARIADB_URI", default="mariadb+mariadbconnector://root:root@127.0.0.1/aml_bot")
