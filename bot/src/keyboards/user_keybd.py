from . import KeyboardMarkup


class UserKeyboard:
    main_buttons = [
        "📤 Отправить добычу",
        "👤 Профиль"
    ]
    profile_change_address_buttons = [
        {"text": "💰 Изменить адрес", "callback_data": "profile_change_wallet"}
    ]

    @staticmethod
    def chanel_invite(link):
        chanel_invite_buttons = [
            {"text": "Я подписался", "callback_data": "sub_accept"},
            {"text": "Наш канал", "url": link}
        ]
        return KeyboardMarkup.inline_keybd(chanel_invite_buttons)

    @staticmethod
    def main_menu():
        return KeyboardMarkup.reply_keybd(UserKeyboard.main_buttons)

    @staticmethod
    def profile_change_address():
        return KeyboardMarkup.inline_keybd(UserKeyboard.profile_change_address_buttons)
