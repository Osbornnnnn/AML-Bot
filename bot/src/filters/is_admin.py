from ..models.users import Users
from telegram.ext import UpdateFilter


# Фильтр для проверки, является ли пользователь администратором
class IsAdmin(UpdateFilter):
    def filter(self, update):
        """
        Если пользователь является администратором, вернуть True, в другом случае False

        :param update: объект обновления, содержащий сообщение
        :return: Значение атрибута is_admin объекта пользователя.
        """

        user = Users.get(update.message.from_user.id)
        if not user:
            return False
        return user.is_admin
