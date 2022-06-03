from telegram import ParseMode
from app import handlers, queues, config
from telegram.ext import Updater, Defaults


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
