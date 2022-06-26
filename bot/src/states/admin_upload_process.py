import os
import ujson
import datetime
from pathlib import Path
from ..models.users import Users
from telegram import Update, File
from ..filters.is_admin import IsAdmin
from ..keyboards import KeyboardMarkup
from ..keyboards.admin_keybd import AdminKeyboard
from telegram.ext import ConversationHandler, CallbackContext, MessageHandler, CommandHandler, Filters


# Это обработчик диалогов, который позволяет администраторам загружать файл журнала и файл AML, а затем обновлять статистику.
class AdminUploadConversation:
    # Путь до корневого каталога проекта.
    app_dir: Path = Path(__file__).parent.parent.parent

    def __init__(self):
        # Путь к каталогу "подготовка", в котором будут сохранены файлы.
        self.report_dir: Path = Path(AdminUploadConversation.app_dir, "reports", "preparing")

        # Это обработчик разговоров.
        self.UPLOAD_FILE, self.UPLOAD_AML_LOG = range(2)
        self.handler = ConversationHandler(
            entry_points=[MessageHandler(Filters.text("📤 Отправить на проверку") & IsAdmin(), self.start)],
            states={
                self.UPLOAD_FILE: [MessageHandler(~Filters.text("❌ Отмена") & Filters.document & IsAdmin(),
                                                  self.upload_log_or_zip)],
                self.UPLOAD_AML_LOG: [MessageHandler(~Filters.text("❌ Отмена") & Filters.document & IsAdmin(),
                                                     self.upload_aml_log)]
            },
            fallbacks=[MessageHandler(Filters.text("❌ Отмена") & IsAdmin(), self.cancel)])

    def keybd_cancel(self, button: str = None):
        """
        Создает клавиатуру с кнопкой "❌ Отмена"

        :param button: Кнопка которая будет стоять над кнопкой "❌ Отмена"
        :return: Клавиатура с кнопками "❌ Отмена" и *Созданной*
        """

        if button:
            return KeyboardMarkup.reply_keybd([button, "❌ Отмена"], row=2)
        return KeyboardMarkup.reply_keybd(["❌ Отмена"], row=1)

    def start(self, update: Update, context: CallbackContext):
        """
        Функция запускает бота, очищает user_data, отправляет сообщение пользователю и возвращает состояние UPLOAD_FILE

        :param update: объект обновления, содержащий сообщение
        :param context: Контекст как объект CallbackContext
        :return: Следующее состояние в разговоре.
        """

        context.user_data.clear()
        update.message.reply_text("<b>Теперь загрузите Архив.zip или Лог.txt</b>",
                                  reply_markup=self.keybd_cancel())
        return self.UPLOAD_FILE

    def upload_log_or_zip(self, update: Update, context: CallbackContext):
        """
        Загружает Zip-архив или log-файл из Telegram, сохраняет его в каталоге, а затем возвращает состояние.

        :param update: Update - объект обновления, содержащий сообщение
        :param context: CallbackContext — контекст разговора
        :return: Состояние, в которое должен перейти разговор.
        """

        msg = update.message

        date: datetime.date = datetime.datetime.today().date()
        log_file: Path = Path(self.report_dir, date.strftime("%m.%Y"), date.strftime("%d.%m.%Y"), f"log_{date.strftime('%d.%m.%Y')}.json")

        if not os.path.exists(log_file.parent):
            os.makedirs(log_file.parent)

        if msg.document.mime_type == "application/json":
            buf: File = context.bot.get_file(msg.document.file_id)
            buf.download(str(log_file))
            context.user_data["log_file"] = log_file
            msg.reply_text("<b>Теперь загрузите файл проверки AML.</b>")
            return self.UPLOAD_AML_LOG

        return ConversationHandler.END

    def upload_aml_log(self, update: Update, context: CallbackContext):
        """
        Загружает aml-файл из Telegram, сохраняет его в каталоге, а затем возвращает состояние. Обновляет статистику пользователя.

        :param update: объект обновления, содержащий сообщение
        :param context: контекст как объект telegram.ext.CallbackContext
        :return: Состояние, в которое должен перейти разговор.
        """

        msg = update.message

        date: datetime.date = datetime.datetime.today().date()
        aml_file: Path = Path(self.report_dir, date.strftime("%m.%Y"), date.strftime("%d.%m.%Y"), f"aml_{date.strftime('%d.%m.%Y')}.json")

        if msg.document.mime_type == "application/json":
            buf: File = context.bot.get_file(msg.document.file_id)
            buf.download(str(aml_file))
            msg.reply_text("<b>Начинаю обновление статистики.</b>")

            with open(context.user_data["log_file"]) as out_log, open(aml_file) as out_aml:
                log_file: dict = ujson.loads(out_log.read())
                aml_file: dict = ujson.loads(out_aml.read())

            log_file = {key: value if value["aml_id"] == a and b else {"user_id": value["user_id"],
                                                                       "aml_id": value["aml_id"],
                                                                       "addresses_count": 0}
                        for key, value in log_file.items() for a, b in aml_file.items()}

            report_and_aml = {key: value["aml_id"] for key, value in log_file.items()}

            user_stata = {}
            for key, value in log_file.items():
                user_stata = {value["user_id"]: {}} if user_stata.get(value["user_id"]) is None else user_stata
                match value["addresses_count"]:
                    case 1:
                        addresses_count = 0.7
                    case 2:
                        addresses_count = 1
                    case 3:
                        addresses_count = 1.2
                    case _:
                        addresses_count = 0

                user_stata.update({
                    value["user_id"]:
                        {
                            "pending_reports": user_stata[value["user_id"]].get("pending_reports", 0) + 1,
                            "approved_reports": user_stata[value["user_id"]].get("approved_reports", 0) + 1 if value["addresses_count"] else user_stata[value["user_id"]].get("approved_reports", 0),
                            "decline_reports": user_stata[value["user_id"]].get("decline_reports", 0) if value["addresses_count"] else user_stata[value["user_id"]].get("decline_reports", 0) + 1,
                            "pending_balance": user_stata[value["user_id"]].get("pending_balance", 0) + addresses_count
                        }
                })

            user_msg_list = []
            for key, value in user_stata.items():
                user = Users.update_statistics(user_id=key, pending_reports=value["pending_reports"], approved_reports=value["approved_reports"],
                                               decline_reports=value["decline_reports"], pending_balance=value["pending_balance"], after_checked=True)

                user_msg_list.append(f"<b>@{user.username} | "
                                     f"<code>{value['approved_reports']} шт.</code> | <code>{value['decline_reports']} шт.</code> | "
                                     f"<code>{value['pending_reports']} шт.</code> | <code>{value['pending_balance']}$</code></b>")

            a = 0
            b = 0
            c = 0.0
            for _, v in user_stata.items():
                a += v["approved_reports"]
                b += v["decline_reports"]
                c += v["pending_balance"]

            user_msg_str = "\n".join(user_msg_list)
            msg.reply_text(f"<b>Статистика:\n"
                           "➖➖➖➖➖➖➖➖➖\n"
                           f"Выполнено: <code>{a} шт.</code>\n"
                           f"Отклонено: <code>{b} шт.</code>\n"
                           f"Всего: <code>{a+b} шт.</code>\n"
                           f"На выплату: <code>{c}$</code>\n"
                           "➖➖➖➖➖➖➖➖➖</b>\n"
                           f"{user_msg_str}", reply_markup=AdminKeyboard.main_menu())

            return ConversationHandler.END

        return

    def cancel(self, update: Update, context: CallbackContext):
        """
        Очищает данные пользователя, отправляет сообщение пользователю и возвращает константу ConversationHandler.END

        :param update: объект обновления, содержащий новую информацию о пользователе или чате.
        :param context: Это объект контекста, который передается функции обратного вызова.
        :return: Константа ConversationHandler.END
        """

        context.user_data.clear()
        update.message.reply_text("<b>❌ Действие отменено</b>", reply_markup=AdminKeyboard.main_menu())
        return ConversationHandler.END


# Singleton (Одиночка)
AdminUploadConversation = AdminUploadConversation()
