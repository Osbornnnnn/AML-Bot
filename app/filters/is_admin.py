from app.models.user import User
from telegram.ext import UpdateFilter


class IsAdmin(UpdateFilter):
    def filter(self, update):
        user = User.get(update.message.from_user.id)
        if not user:
            return False
        return user.is_admin
