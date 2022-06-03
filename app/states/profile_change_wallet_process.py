from telegram import Update
from app.models.user import User
from app.filters.is_user import IsUser
from app.keyboards import KeyboardMarkup
from app.filters.is_access import IsAccess
from app.keyboards.user_keybd import UserKeyboard
from telegram.ext import ConversationHandler, MessageHandler, Filters, CallbackQueryHandler


class ProfileConversation:
    def __init__(self):
        self.NEW_WALLET = range(1)
        self.handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(callback=self.start, pattern="profile_change_wallet")],
            states={
                self.NEW_WALLET: [MessageHandler(~Filters.text("❌ Отмена") & IsUser() & IsAccess(), self.update_address)]
            },
            fallbacks=[MessageHandler(Filters.text("❌ Отмена") & IsUser() & IsAccess(), self.cancel)])

    def start(self, update: Update, _):
        query = update.callback_query

        user = User.get(query.from_user.id)

        query.bot.delete_message(query.from_user.id, query.message.message_id)

        query.bot.send_message(query.from_user.id,
                               f"<b>Ваш предыдущий кошелёк: <code>{user.wallet}</code>\n"
                               f"Введите новый адрес:</b>" if user.wallet else "<b>Вы еще не добавили кошелёк.\n"
                                                                               "Введите ваш первый адрес:</b>",
                               reply_markup=KeyboardMarkup.reply_keybd(["❌ Отмена"], row=1))

        return self.NEW_WALLET

    def update_address(self, update: Update, _):
        msg = update.message

        wallet = User.update_wallet(msg.from_user.id, msg.text)

        msg.reply_text(f"<b>Ваш новый адрес кошелька: <code>{wallet}</code></b>", reply_markup=UserKeyboard.main_menu())
        return ConversationHandler.END

    def cancel(self, update: Update, _):
        update.message.reply_text("<b>❌ Действие отменено</b>", reply_markup=UserKeyboard.main_menu())
        return ConversationHandler.END

ProfileConversation = ProfileConversation()
