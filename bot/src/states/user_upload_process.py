import re
import uuid
import base64
from telegram import Update
from ..models.users import Users
from ..models.reports import Reports
from ..filters.is_user import IsUser
from ..keyboards import KeyboardMarkup
from ..filters.is_access import IsAccess
from ..keyboards.user_keybd import UserKeyboard
from telegram.ext import ConversationHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler


class UserUploadConversation:
    def __init__(self):
        self.WALLETS, self.TOPIC, self.WEBSITE, self.CONTACTS, self.CATEGORY, self.DESCRIPTION, self.SELLER_LANG, self.WEBSITE_LANG, \
            self.WELCOME_SCREEN, self.CONTACT_SCREEN, self.CHAT_SCREEN, self.CHAT_TEXT, self.SEND_REPORT = range(13)
        self.handler = ConversationHandler(
            entry_points=[MessageHandler(Filters.text("📤 Отправить добычу") & IsUser() & IsAccess(), self.start)],
            states={
                self.WALLETS: [MessageHandler(~Filters.text("❌ Отмена") & IsUser() & IsAccess(), self.add_wallets)],
                self.TOPIC: [MessageHandler(~Filters.text("❌ Отмена") & IsUser() & IsAccess(), self.add_topic)],
                self.WEBSITE: [MessageHandler(~Filters.text("❌ Отмена") & IsUser() & IsAccess(), self.add_website)],
                self.CONTACTS: [MessageHandler(~Filters.text("❌ Отмена") & IsUser() & IsAccess(), self.add_contacts)],
                self.CATEGORY: [MessageHandler(~Filters.text("❌ Отмена") & IsUser() & IsAccess(), self.add_category)],
                self.DESCRIPTION: [MessageHandler(~Filters.text("❌ Отмена") & IsUser() & IsAccess(), self.add_description)],
                self.SELLER_LANG: [CallbackQueryHandler(self.select_seller_lang)],
                self.WEBSITE_LANG: [CallbackQueryHandler(self.select_website_lang)],
                self.WELCOME_SCREEN: [MessageHandler(Filters.photo & IsUser() & IsAccess(), self.upload_welcome_screen)],
                self.CONTACT_SCREEN: [MessageHandler((Filters.photo | Filters.text("Пропустить")) & IsUser() & IsAccess(), self.upload_contact_screen)],
                self.CHAT_SCREEN: [MessageHandler((Filters.photo | Filters.text("🔜 Далее")) & IsUser() & IsAccess(), self.upload_chat_screen)],
                self.CHAT_TEXT: [MessageHandler((Filters.document | Filters.text("Нет её, это сайт") | ~Filters.text("❌ Отмена")) & IsUser() & IsAccess(), self.upload_chat_text)],
                self.SEND_REPORT: [MessageHandler(Filters.text("✅ Отправить") & IsUser() & IsAccess(), self.send_report)]
            },
            fallbacks=[MessageHandler(Filters.text("❌ Отмена") & IsUser() & IsAccess(), self.cancel)])
        self.seller_lang = [
            {"text": "Россия, русский", "callback_data": "lang_ru_rus"},
            {"text": "Украина, русский", "callback_data": "lang_uk_rus"},
            {"text": "Украина, украинский", "callback_data": "lang_uk_ukr"},
            {"text": "США, английский", "callback_data": "lang_en_eng"},
            {"text": "Испания, испанский", "callback_data": "lang_is_isp"},
            {"text": "Китай, китайский", "callback_data": "lang_ci_chi"},
            {"text": "ОАЭ, арабский", "callback_data": "lang_ar_ara"},
            {"text": "Франция, французский", "callback_data": "lang_fr_fra"},
            {"text": "Германия, немецкий", "callback_data": "lang_de_der"},
            {"text": "Польша, польский", "callback_data": "lang_pl_pol"}
        ]
        self.website_lang = [
            {"text": "Русский", "callback_data": "lang_rus"},
            {"text": "Английский", "callback_data": "lang_eng"},
            {"text": "Испанский", "callback_data": "lang_isp"},
            {"text": "Китайский", "callback_data": "lang_chi"},
            {"text": "Арабский", "callback_data": "lang_ara"},
            {"text": "Французский", "callback_data": "lang_fra"},
            {"text": "Немецкий", "callback_data": "lang_der"},
            {"text": "Польский", "callback_data": "lang_pol"},
        ]

    def inline_seller_lang(self):
        return KeyboardMarkup.inline_keybd(self.seller_lang, 3)

    def inline_website_lang(self):
        return KeyboardMarkup.inline_keybd(self.website_lang, 3)

    def keybd_cancel(self, button: str = None):
        if button:
            return KeyboardMarkup.reply_keybd([button, "❌ Отмена"], row=1)
        return KeyboardMarkup.reply_keybd(["❌ Отмена"], row=1)

    def start(self, update: Update, context: CallbackContext):
        msg = update.message
        user = Users.get(msg.from_user.id)
        context.user_data.clear()

        if not user.wallet:
            msg.reply_text("<b>Перед тем как начать. Добавьте кошелёк для выплаты.</b>")
            return ConversationHandler.END

        msg.reply_text("<b>Введите адрес и/или адреса BTC, ETH, TRX (USDT TRC-20), которые вам дал продавец.\n"
                       "Внимание: разделяйте адреса между собой любым знаком.</b>", reply_markup=self.keybd_cancel())

        return self.WALLETS

    def add_wallets(self, update: Update, context: CallbackContext):
        msg = update.message

        if len(msg.text) > 256:
            msg.reply_text("<b>Длина не должна быть больше 256 символов.</b>")
            return

        btc = re.findall(r"([13][a-km-zA-HJ-NP-Z1-9]{26,36}|bc1[ac-hj-np-zAC-HJ-NP-Z02-9]{39,59})", msg.text)
        eth = re.findall(r"0x[a-fA-F0-9]{40}", msg.text)
        trx = re.findall(r"T[A-Za-z1-9]{33}", msg.text)
        adr = Reports.get_by_address(btc + eth + trx)

        context.user_data.update({"btc_address": btc[0] if len(btc) and btc[0] not in list(map(lambda x: x.btc_address, adr)) else None,
                                  "eth_address": eth[0] if len(eth) and eth[0] not in list(map(lambda x: x.eth_address, adr)) else None,
                                  "trx_address": trx[0] if len(trx) and trx[0] not in list(map(lambda x: x.trx_address, adr)) else None})

        if all(i is None for i in context.user_data.values()) and btc + eth + trx:
            msg.reply_text("<b>Все введенные вами адреса уже есть в базе данных.</b>", reply_markup=UserKeyboard.main_menu())
            return ConversationHandler.END
        elif not btc + eth + trx:
            msg.reply_text("<b>Введите хотя бы один адрес.</b>")
            return
        elif adr:
            msg.reply_text("\n".join([f"<b>Кошелёк {x} уже есть в базе данных.</b>" for x in btc + eth + trx if x not in context.user_data.values()]))

        msg.reply_text("<b>Введите ссылку на тему, где вы нашли контакт продавца.\n"
                       "Пример: https://example.com/topic=4654</b>")

        return self.TOPIC

    def add_topic(self, update: Update, context: CallbackContext):
        msg = update.message

        if len(msg.text) > 2048:
            msg.reply_text("<b>Длина не должна быть больше 2048 символов.</b>")
            return

        if not msg.text.startswith("http:") and not msg.text.startswith("https:"):
            msg.reply_text("<b>Ссылка должна включать http:// или https://</b>")
            return

        context.user_data.update({"topic_link": msg.text})

        msg.reply_text("<b>Введите ссылку на главную страницу форума.\n"
                       "Пример: Ссылка на тему была https://example.com/topic=4654, значит ссылка на главную будет https://example.com/</b>")

        return self.WEBSITE

    def add_website(self, update: Update, context: CallbackContext):
        msg = update.message

        if len(msg.text) > 2048:
            msg.reply_text("<b>Длина не должна быть больше 2048 символов.</b>")
            return

        if not msg.text.startswith("http:") and not msg.text.startswith("https:"):
            msg.reply_text("<b>Ссылка должна включать http:// или https://</b>")
            return

        context.user_data.update({"website_link": msg.text})

        msg.reply_text("<b>Введите имя / никнейм продавца из приложения, где вы с ним общались.\n"
                       'Если это сайт авто-оплаты нажмите "Пропустить"</b>', reply_markup=self.keybd_cancel("Пропустить"))

        return self.CONTACTS

    def add_contacts(self, update: Update, context: CallbackContext):
        msg = update.message

        if len(msg.text) > 512:
            msg.reply_text("<b>Длина не должна быть больше 512 символов.</b>")
            return

        if msg.text == "Пропустить":
            context.user_data.update({"contact": context.user_data["website_link"]})
        else:
            context.user_data.update({"contact": msg.text})

        msg.reply_text("<b>Введите номер категории (от 1 до 61), к которой относится деятельность продавца.</b>",
                       reply_markup=self.keybd_cancel())

        return self.CATEGORY

    def add_category(self, update: Update, context: CallbackContext):
        msg = update.message

        if not msg.text.isdigit():
            msg.reply_text("<b>Используйте цифры, ничего более!</b>")
            return

        context.user_data.update({"category": msg.text})

        msg.reply_text("<b>Введите краткое описание деятельности продавца (только на английском).\n"
                       "Пример: selling credit cards (много писать не нужно).</b>")

        return self.DESCRIPTION

    def add_description(self, update: Update, context: CallbackContext):
        msg = update.message

        if len(msg.text) > 512:
            msg.reply_text("<b>Длина не должна быть больше 512 символов.</b>")
            return

        context.user_data.update({"description": msg.text})

        msg.reply_text("<b>Выберите страну и язык продавца:</b>", reply_markup=self.inline_seller_lang())

        return self.SELLER_LANG

    def select_seller_lang(self, update: Update, context: CallbackContext):
        query = update.callback_query

        context.user_data.update({"seller_lang": element["text"] for element in self.seller_lang if element["callback_data"] == query.data})

        query.message.edit_text("<b>Выберите язык форума:</b>", reply_markup=self.inline_website_lang())

        return self.WEBSITE_LANG

    def select_website_lang(self, update: Update, context: CallbackContext):
        query = update.callback_query

        context.user_data.update({"website_lang": element["text"] for element in self.website_lang if element["callback_data"] == query.data})

        query.message.edit_text(f"<b>Язык продавца: <code>{context.user_data['seller_lang']}</code>\n"
                                f"Язык форума: <code>{context.user_data['website_lang']}</code></b>")
        query.message.reply_text("<b>Вставьте скриншот темы на форуме (1 изображение).\n"
                                 "Отправьте в сжатом формате. (Как фото)</b>", reply_markup=self.keybd_cancel())

        return self.WELCOME_SCREEN

    def upload_welcome_screen(self, update: Update, context: CallbackContext):
        msg = update.message

        context.user_data.update({"welcome_screen": msg.photo[-1].file_id})

        msg.reply_text("<b>Вставьте скриншот профиля продавца в мессенджере (1 изображение).\n"
                       "Отправьте в сжатом формате. (Как фото)\n"
                       'Если это сайт авто-оплаты нажмите "Пропустить"</b>', reply_markup=self.keybd_cancel("Пропустить"))

        return self.CONTACT_SCREEN

    def upload_contact_screen(self, update: Update, context: CallbackContext):
        msg = update.message

        if msg.text == "Пропустить":
            context.user_data.update({"contact_screen": context.user_data["welcome_screen"]})
        else:
            context.user_data.update({"contact_screen": msg.photo[-1].file_id})

        msg.reply_text("<b>Пришлите скриншоты переписки с продавцом (минимум 1 изображение).\n"
                       "Внимание! Если это сайт авто-оплаты, то обязательно должен быть скриншот, где виден адрес кошельков.\n"
                       "Отправьте в сжатом формате и без группировки!\n"
                       "После завершения нажмите «🔜 Далее»</b>", reply_markup=self.keybd_cancel("🔜 Далее"))

        return self.CHAT_SCREEN

    def upload_chat_screen(self, update: Update, context: CallbackContext):
        msg = update.message

        if msg.text != "🔜 Далее":
            chat_screen = context.user_data.get("chat_screen")

            if chat_screen is None:
                return context.user_data.update({"chat_screen": [msg.photo[-1].file_id]})
            chat_screen.append(msg.photo[-1].file_id)

            return context.user_data.update({"chat_screen": chat_screen})

        if len(context.user_data.get("chat_screen")) == 0:
            msg.reply_text("<b>Загрузите хотябы 1 скриншот.</b>")
            return

        msg.reply_text(f"<b>Загрузилось {len(context.user_data.get('chat_screen'))} скриншотов.\n"
                       "Далее: Добавьте файл переписки с расширением .txt с кодировкой UTF-8\n"
                       "Если это сайт с авто-оплатой, то нажмите «Нет её, это сайт»</b>", reply_markup=self.keybd_cancel("Нет её, это сайт"))

        return self.CHAT_TEXT

    def upload_chat_text(self, update: Update, context: CallbackContext):
        msg = update.message

        if msg.text:
            context.user_data.update({"chat_text": base64.b64encode(msg.text.encode()).decode()})
        else:
            context.user_data.update({"chat_text": msg.document.file_id})

        msg.reply_text("<b>Нажмите «✅ Отправить», чтобы отправить информацию на проверку.</b>",
                       reply_markup=self.keybd_cancel("✅ Отправить"))

        return self.SEND_REPORT

    def send_report(self, update: Update, context: CallbackContext):
        msg = update.message

        context.user_data.update({"report_id": str(uuid.uuid1()), "user_id": update.message.from_user.id})
        Reports.update(context.user_data)

        Users.update_statistics(pending_reports=1)

        msg.reply_text(f"<b>№ <code>{context.user_data['report_id']}</code>\n"
                       "Ваше сообщение было отправлено на проверку.\n"
                       "Если хотите сообщить еще об одном адресе, жмите «📤 Отправить добычу»</b>", reply_markup=UserKeyboard.main_menu())

        return ConversationHandler.END

    def cancel(self, update: Update, context: CallbackContext):
        context.user_data.clear()
        update.message.reply_text("<b>❌ Действие отменено</b>", reply_markup=UserKeyboard.main_menu())
        return ConversationHandler.END

UserUploadConversation = UserUploadConversation()
