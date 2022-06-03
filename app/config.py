import pytz
from envparse import env


TIMEZONE = env.str("TZ", default=pytz.timezone("Europe/Moscow"))
TELEGRAM_TOKEN = env.str("AML_BOT_TG_TOKEN", default="")
DATABASE_URI = env.str("AML_BOT_MARIADB_URI", default="mariadb+mariadbconnector://root:root@127.0.0.1/aml_bot")
