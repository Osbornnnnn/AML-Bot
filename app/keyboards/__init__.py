from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove


class KeyboardMarkup:
    @staticmethod
    def _serialize_buttons(buttons: list[str], row: int) -> list:
        return [buttons[i:i + row] for i in range(0, len(buttons), row)]

    @staticmethod
    def _serialize_inline_buttons(inline_data: list[dict]) -> list:
        return [InlineKeyboardButton(**data) for data in inline_data]

    @staticmethod
    def reply_keybd(buttons: list[str] = None, row: int = 2, resize_keyboard: bool = True) -> ReplyKeyboardMarkup | ReplyKeyboardRemove:
        if buttons:
            return ReplyKeyboardMarkup(KeyboardMarkup._serialize_buttons(buttons, row), resize_keyboard=resize_keyboard)
        return ReplyKeyboardRemove()

    @staticmethod
    def inline_keybd(inline_data: list[dict], row: int = 2) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(KeyboardMarkup._serialize_buttons(KeyboardMarkup._serialize_inline_buttons(inline_data), row))
