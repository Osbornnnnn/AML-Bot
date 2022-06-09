from telegram import Update
from ..models.user import User
from ..filters.is_user import IsUser
from ..filters.is_access import IsAccess
from ..keyboards.user_keybd import UserKeyboard


class UserHandler:
    @staticmethod
    def start_command_handler(update: Update, _):
        update.message.reply_text(f"<b>С возвращением @{update.message.chat.username}</b>",
                                  reply_markup=UserKeyboard.main_menu())

    @staticmethod
    def start_command_callback(update: Update, _):
        if IsAccess().filter(update) and IsUser().filter(update):
            update.callback_query.delete_message()
            update.callback_query.bot.send_message(update.callback_query.from_user.id,
                                                   f"<b>Приветствую, @{update.callback_query.message.from_user.username}\n"
                                                   f"Можете продолжать работу ^^</b>",
                                                   reply_markup=UserKeyboard.main_menu())

    @staticmethod
    def profile_meesage_handler(update: Update, _):
        msg = update.message

        user = User.get(msg.from_user.id)

        profile = [
            "<b>",
            "Ваш профиль:",
            "➖➖➖➖➖➖➖➖➖",
            f"Ваш ID: <code>{user.user_id}</code>",
            f"Ваше имя: @{user.username}",
            f"Ваш кошелек: <code>{user.wallet}</code>",
            f"Дата вступления: <code>{user.create_date.date()}</code>",
            "➖➖➖➖➖➖➖➖➖",
            "Баланс:",
            f"На выплату: <code>{user.pending_balance}$</code>",
            f"За всё время: <code>{user.total_balance}$</code>",
            "➖➖➖➖➖➖➖➖➖",
            "Заявки:",
            f"Отправленные: <code>{user.pending_reports} шт.</code>",
            f"Принятые: <code>{user.approved_reports} шт.</code>",
            f"Всего принято: <code>{user.paid_reports} шт.</code>",
            f"Всего отклонено: <code>{user.decline_reports} шт.</code>",
            "➖➖➖➖➖➖➖➖➖",
            "</b>"
        ]
        msg.reply_text("\n".join(profile), reply_markup=UserKeyboard.profile_change_address())

    @staticmethod
    def cancel_message_handler(update: Update, _):
        update.message.reply_text("<b>❌ Действие отменено</b>", reply_markup=UserKeyboard.main_menu())

UserHandler = UserHandler()
