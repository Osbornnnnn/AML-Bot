import os
import re
import uuid
import ujson
import base64
import requests
import datetime
from pathlib import Path
from telegram import Update
from app.models.user import User
from app.models.report import Report
from app.config import TELEGRAM_TOKEN
from app.filters.is_admin import IsAdmin
from app.keyboards import KeyboardMarkup
from app.keyboards.admin_keybd import AdminKeyboard
from telegram.ext import ConversationHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler


class AdminUploadConversation:
    app_dir: Path = Path(__file__).parent.parent.parent

    def __init__(self):
        self.UPLOAD_FILE, self.UPLOAD_AML_LOG, self.UPDATE_STATA = range(3)
        self.handler = ConversationHandler(
            entry_points=[MessageHandler(Filters.text("📤 Отправить на проверку") & IsAdmin(), self.start)],
            states={
                self.UPLOAD_FILE: [MessageHandler(~Filters.text("❌ Отмена") & Filters.document & IsAdmin(),
                                                  self.upload_log_or_zip)],
                self.UPLOAD_AML_LOG: [MessageHandler(~Filters.text("❌ Отмена") & Filters.document & IsAdmin(),
                                                     self.upload_aml_log)],
                self.UPDATE_STATA: [MessageHandler(~Filters.text("❌ Отмена") & Filters.document & IsAdmin(),
                                                   self.update_statistics)]
            },
            fallbacks=[MessageHandler(Filters.text("❌ Отмена") & IsAdmin(), self.cancel)])
        self.date: datetime.date = datetime.datetime.today().date()
        self.log_dir: Path = Path(AdminUploadConversation.app_dir, "logs")
        self.log_file: Path = Path(self.log_dir, self.date.strftime("%m.%Y"), f"log_{self.date.strftime('%d.%m.%Y')}.txt")
        self.aml_file: Path = Path(self.log_dir, self.date.strftime("%m.%Y"), f"aml_{self.date.strftime('%d.%m.%Y')}.txt")

        if not os.path.exists(self.log_file.parent):
            os.makedirs(self.log_file.parent)

        if not os.path.exists(self.aml_file.parent):
            os.makedirs(self.aml_file.parent)

    def keybd_cancel(self, button: str = None):
        if button:
            return KeyboardMarkup.reply_keybd([button, "❌ Отмена"], row=2)
        return KeyboardMarkup.reply_keybd(["❌ Отмена"], row=1)

    def start(self, update: Update, _):
        update.message.reply_text("<b>Теперь загрузите Архив.zip или Лог.txt</b>",
                                  reply_markup=self.keybd_cancel())
        return self.UPLOAD_FILE

    def upload_log_or_zip(self, update: Update, context: CallbackContext):
        msg = update.message

        if msg.document.mime_type == "application/json":
            r = requests.get(msg.bot.get_file(msg.document.file_id)["file_path"]).json()
            open(self.log_file, "w").write(ujson.dumps(r))
            context.user_data["log_file"] = r
            msg.reply_text("<b>Теперь загрузите файл проверки AML.</b>")
            return self.UPLOAD_AML_LOG

        return ConversationHandler.END

    def upload_aml_log(self, update: Update, context: CallbackContext):
        msg = update.message

        if msg.document.mime_type == "application/json":
            r = requests.get(msg.bot.get_file(msg.document.file_id)["file_path"]).json()
            open(self.aml_file, "w").write(ujson.dumps(r))
            context.user_data["aml_file"] = r
            msg.reply_text("<b>Начинаю обновление статистики.</b>")
            return self.UPDATE_STATA

        return  # Again

    def update_statistics(self, update: Update, context: CallbackContext):
        pass

    def cancel(self, update: Update, context: CallbackContext):
        context.user_data.clear()
        update.message.reply_text("<b>❌ Действие отменено</b>", reply_markup=AdminKeyboard.main_menu())
        return ConversationHandler.END

AdminUploadConversation = AdminUploadConversation()
