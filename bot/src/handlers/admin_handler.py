from telegram import Update
from ..keyboards.admin_keybd import AdminKeyboard


class AdminHandler:
    @staticmethod
    def start_command_handler(update: Update, _):
        update.message.reply_text(f"<b>С возвращением @{update.message.from_user.username}. Мой Господин!</b>",
                                  reply_markup=AdminKeyboard.main_menu())

    @staticmethod
    def cancel_message_handler(update: Update, _):
        update.message.reply_text("<b>❌ Действие отменено</b>", reply_markup=AdminKeyboard.main_menu())
