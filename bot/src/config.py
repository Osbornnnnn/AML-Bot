import pytz
from envparse import env


# Способ получить часовой пояс из переменной среды. Если он не установлен, будет использоваться значение по умолчанию.
TIMEZONE = env.str("TZ", default=pytz.timezone("Europe/Moscow"))

# Способ получить токен телеграмма из переменной окружения. Если он не установлен, будет использоваться значение по умолчанию.
TELEGRAM_TOKEN = env.str("TELEGRAM_TOKEN", default="")

# Способ получить URI базы данных из переменной среды. Если он не установлен, будет использоваться значение по умолчанию.
DATABASE_URI = env.str("MARIADB_URI", default="mariadb+mariadbconnector://root:root@127.0.0.1/aml_bot")
