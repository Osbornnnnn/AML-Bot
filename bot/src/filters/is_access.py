from telegram.ext import UpdateFilter
from datetime import datetime, timedelta
from ..keyboards.user_keybd import UserKeyboard
from telegram import ReplyKeyboardRemove, Message


# Фильтр для проверки того, находится ли пользователь в канале.
class IsAccess(UpdateFilter):
    def filter(self, update) -> bool:
        """
        Если пользователя нет в канале, бот отправит пользователю сообщение с просьбой присоединиться к каналу.

        :param update: объект обновления, содержащий сообщение.
        :return: Логическое значение.
        """

        msg = update.message
        query = update.callback_query
        if isinstance(msg, Message):
            user_status = msg.bot.get_chat_member("-1001601093444", msg.from_user.id)
            if user_status["status"] == "left":
                msg.reply_text(f"<b>Приветики @{msg.from_user.username}</b>", reply_markup=ReplyKeyboardRemove())
                expire_time = datetime.now() + timedelta(minutes=10)
                link = msg.bot.create_chat_invite_link("-1001601093444", expire_time, 1,
                                                       name=f"{msg.from_user.id}, @{msg.from_user.username}")
                msg.reply_text("<b>Необходимо подписаться на наш канал ^^</b>",
                               reply_markup=UserKeyboard.chanel_invite(link.invite_link))
                return False
        else:
            user_status = query.bot.get_chat_member("-1001601093444", query.from_user.id)
            if user_status["status"] == "left":
                query.answer("Я не вижу вас в канале, попробуйте еще раз!")
                return False
        return True
