from ..filters.is_user import IsUser
from ..filters.is_admin import IsAdmin
from ..filters.is_access import IsAccess
from .user_handler import UserHandler
from .admin_handler import AdminHandler
from ..states.user_upload_process import UserUploadConversation
from ..states.admin_upload_process import AdminUploadConversation
from ..states.profile_change_wallet_process import ProfileConversation
from telegram.ext import Dispatcher, Filters, CommandHandler, CallbackQueryHandler, MessageHandler


def setup(dispatcher: Dispatcher):
    # Start Command
    dispatcher.add_handler(CommandHandler(callback=UserHandler.start_command_handler, command="start", filters=IsUser() & IsAccess()))
    dispatcher.add_handler(CommandHandler(callback=AdminHandler.start_command_handler, command="start", filters=IsAdmin()))
    dispatcher.add_handler(CallbackQueryHandler(callback=UserHandler.start_command_callback, pattern="sub_accept"))

    # User Profile
    dispatcher.add_handler(MessageHandler(callback=UserHandler.profile_meesage_handler, filters=Filters.text("👤 Профиль") & IsUser() & IsAccess()))
    dispatcher.add_handler(ProfileConversation.handler)

    # User Upload State
    dispatcher.add_handler(UserUploadConversation.handler)

    # Admin Upload State
    dispatcher.add_handler(AdminUploadConversation.handler)

    # Cancel Handlers
    dispatcher.add_handler(MessageHandler(callback=UserHandler.cancel_message_handler, filters=Filters.text("❌ Отмена") & IsUser() & IsAccess()))
    dispatcher.add_handler(MessageHandler(callback=AdminHandler.cancel_message_handler, filters=Filters.text("❌ Отмена") & IsAdmin()))
