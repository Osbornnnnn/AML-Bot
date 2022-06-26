import sys
from loguru import logger


# Удаляет все обработчики из логгера.
logger.remove()

# Добавление лог-файла в регистратор.
logger.add("../../logs/bot_{time:YYYY-MM-DD}.log", retention="60 days",
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {file}:{line} | {message}")

# Добавление обработчика `ERROR` в логгер.
logger.add(sys.stderr, colorize=True, level="ERROR", filter=lambda msg: msg["level"].name == "ERROR",
           format="<yellow>{time:YYYY-MM-DD HH:mm:ss}</yellow> <white>|</white> <cyan>{level}</cyan> <white>|</white> "
                  "<blue>{file}:{line}</blue> <white>|</white> <red>{message}</red>")

# Добавление обработчика `INFO` в логгер.
logger.add(sys.stderr, colorize=True, level="INFO", filter=lambda msg: msg["level"].name == "INFO",
           format="<yellow>{time:YYYY-MM-DD HH:mm:ss}</yellow> <white>|</white> <cyan>{level}</cyan> <white>|</white> <green>{message}</green>")
