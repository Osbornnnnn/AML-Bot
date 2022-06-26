from ..models.users import Users
from telegram.ext import UpdateFilter
from telegram import ReplyKeyboardRemove, Message


# Фильтр для проверки, является ли пользователь обычным
class IsUser(UpdateFilter):
    def filter(self, update) -> bool:
        """
        Если пользователь является обычным, вернуть True, в другом случае False

        :param update: объект обновления, содержащий сообщение
        :return: Значение атрибута is_admin объекта пользователя.
        """

        msg = update.message
        query = update.callback_query
        if isinstance(msg, Message):
            if msg.from_user.username is None:
                msg.reply_text("<b>У вас должен быть выбран @Username</b>", reply_markup=ReplyKeyboardRemove())
                return False
        else:
            if query.from_user.username is None:
                query.bot.send_message(query.from_user.id, "<b>У вас должен быть выбран @Username</b>", reply_markup=ReplyKeyboardRemove())
                return False
        user = Users.update(msg.from_user.id if msg else query.from_user.id, msg.from_user.username if msg else query.from_user.username)
        return not user.is_admin
