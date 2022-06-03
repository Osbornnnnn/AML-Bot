from app.keyboards import KeyboardMarkup


class AdminKeyboard:
    main_buttons = [
            "💸 Выплаты",
            "📤 Отправить на проверку",
            "⚙ Настройки бота"
    ]

    @staticmethod
    def main_menu():
        return KeyboardMarkup.reply_keybd(AdminKeyboard.main_buttons)
