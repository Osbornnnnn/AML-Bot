from telegram import ParseMode
from telegram.ext import Updater, Defaults

try:
    from bot.src import handlers, queues, config
except:
    from . import handlers, queues, config

def main() -> None:
    defaults = Defaults(parse_mode=ParseMode.HTML, run_async=True, disable_web_page_preview=True, tzinfo=config.TIMEZONE)
    updater = Updater(config.TELEGRAM_TOKEN, use_context=True, defaults=defaults)

    dispatcher = updater.dispatcher
    handlers.setup(dispatcher)
    queues.setup(updater.job_queue)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
