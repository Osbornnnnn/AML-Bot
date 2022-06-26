from telegram import Update
from ..models.users import Users
from ..filters.is_user import IsUser
from ..keyboards import KeyboardMarkup
from ..filters.is_access import IsAccess
from ..keyboards.user_keybd import UserKeyboard
from telegram.ext import ConversationHandler, MessageHandler, Filters, CallbackQueryHandler


# Это обработчик диалогов, который позволяет пользователю изменить адрес своего кошелька.
class ProfileConversation:
    def __init__(self):
        # Это обработчик разговоров.
        self.NEW_WALLET = range(1)
        self.handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(callback=self.start, pattern="profile_change_wallet")],
            states={
                self.NEW_WALLET: [MessageHandler(~Filters.text("❌ Отмена") & IsUser() & IsAccess(), self.update_address)]
            },
            fallbacks=[MessageHandler(Filters.text("❌ Отмена") & IsUser() & IsAccess(), self.cancel)])

    def start(self, update: Update, _):
        """
        Функция вызывается, когда пользователь нажимает кнопку «Изменить кошелёк».
        Функция удаляет сообщение кнопкой и отправляет пользователю сообщение с запросом нового адреса кошелька.

        :param update: объект обновления, содержащий новую информацию о пользователе или чате.
        :param _: Это объект контекста, который передается функции обратного вызова.
        :return: Следующее состояние в разговоре.
        """
        query = update.callback_query

        user = Users.get(query.from_user.id)

        query.bot.delete_message(query.from_user.id, query.message.message_id)

        query.bot.send_message(query.from_user.id,
                               f"<b>Ваш предыдущий кошелёк: <code>{user.wallet}</code>\n"
                               f"Введите новый адрес:</b>" if user.wallet else "<b>Вы еще не добавили кошелёк.\n"
                                                                               "Введите ваш первый адрес:</b>",
                               reply_markup=KeyboardMarkup.reply_keybd(["❌ Отмена"], row=1))

        return self.NEW_WALLET

    def update_address(self, update: Update, _):
        """
        Принимает сообщение от пользователя, обновляет адрес кошелька пользователя в базе данных и
        отправляет пользователю сообщение с новым адресом кошелька.

        :param update: объект обновления, содержащий новую информацию о пользователе или чате.
        :param _: Это объект контекста, который передается функции обратного вызова.
        :return: Константа ConversationHandler.END
        """
        msg = update.message

        wallet = Users.update_wallet(msg.from_user.id, msg.text)

        msg.reply_text(f"<b>Ваш новый адрес кошелька: <code>{wallet}</code></b>", reply_markup=UserKeyboard.main_menu())
        return ConversationHandler.END

    def cancel(self, update: Update, _):
        """
        Отправляет сообщение пользователю и возвращает константу ConversationHandler.END

        :param update: объект обновления, содержащий новую информацию о пользователе или чате.
        :param _: Это объект контекста, который передается функции обратного вызова.
        :return: Константа ConversationHandler.END
        """

        update.message.reply_text("<b>❌ Действие отменено</b>", reply_markup=UserKeyboard.main_menu())
        return ConversationHandler.END

# Singleton (Одиночка)
ProfileConversation = ProfileConversation()
