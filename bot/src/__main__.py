from telegram import ParseMode
from telegram.ext import Updater, Defaults

try:
    from bot.src import handlers, queues, config
    from bot.src.utils.logger import logger
except:
    from . import handlers, queues, config
    from .utils.logger import logger

def main() -> None:
    # Установка значений по умолчанию для бота.
    defaults = Defaults(parse_mode=ParseMode.HTML, run_async=True, disable_web_page_preview=True, tzinfo=config.TIMEZONE)
    # Создание объекта Updater.
    updater = Updater(config.TELEGRAM_TOKEN, use_context=True, defaults=defaults)

    dispatcher = updater.dispatcher
    handlers.setup(dispatcher)
    logger.info("Handlers setup")
    queues.setup(updater.job_queue)
    logger.info("Queues setup")

    logger.info("Polling starting...")
    # Запускает бота.
    updater.start_polling()
    logger.info("Idle starting...")
    # Блокирующий вызов, ожидающий остановки бота.
    updater.idle()

if __name__ == "__main__":
    main()
