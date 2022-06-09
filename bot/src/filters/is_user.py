from ..models.user import User
from telegram.ext import UpdateFilter
from telegram import ReplyKeyboardRemove, Message


class IsUser(UpdateFilter):
    def filter(self, update) -> bool:
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
        user = User.update(msg.from_user.id if msg else query.from_user.id, msg.from_user.username if msg else query.from_user.username)
        return not user.is_admin
