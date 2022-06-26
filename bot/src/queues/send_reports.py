import os
import ujson
import base64
import shutil
import datetime
from pathlib import Path
from zipfile import ZipFile
from ..models.users import Users
from ..models.reports import Reports
from telegram import File
from telegram.ext import CallbackContext


class SendReports:
    app_dir: Path = Path(__file__).parent.parent.parent
    tmp_dir: Path = Path(app_dir, "tmp")
    report_dir: Path = Path(app_dir, "reports", "waiting")

    @staticmethod
    def start(context: CallbackContext):
        now_date: datetime.date = datetime.datetime.today().date() - datetime.timedelta(days=1)
        path_to_reports: Path = Path(SendReports.tmp_dir, now_date.strftime("%d.%m.%Y"))
        report_list: list = Reports.get_by_date(now_date)
        admin_list: list = Users.get_admins()

        if not admin_list:
            return
        if not report_list:
            [context.bot.send_message(admin.user_id, "<b>Вчера отправили 0 репортов -_-</b>") for admin in admin_list]
            return

        for report in report_list:
            path_to_report: Path = Path(path_to_reports, str(report.user_id), report.report_id)
            if not os.path.exists(path_to_report):
                os.makedirs(path_to_report)

            with open(Path(path_to_report, "Данные.json"), "w", encoding="UTF-8") as out:
                out.write(ujson.dumps({
                    "report_id": report.report_id,
                    "wallets": f"{f'BTC|{report.btc_address},' if report.btc_address else ''}"
                               f"{f'ETH|{report.eth_address},' if report.eth_address else ''}"
                               f"{f'TRX|{report.trx_address}' if report.trx_address else ''}",
                    "contact": report.contact,
                    "category": report.category,
                    "description": report.description,
                    "topic_link": report.topic_link,
                    "website_link": report.website_link,
                    "seller_lang": report.seller_lang,
                    "website_lang": report.website_lang
                }, indent=4, ensure_ascii=False, escape_forward_slashes=False))

            buf: File = context.bot.get_file(report.welcome_screen)
            buf.download(str(Path(path_to_report, f"Знакомство{os.path.splitext(buf.file_path)[-1]}")))

            buf: File = context.bot.get_file(report.contact_screen)
            buf.download(str(Path(path_to_report, f"Контакт{os.path.splitext(buf.file_path)[-1]}")))

            for i in range(len(report.chat_screen)):
                buf: File = context.bot.get_file(report.chat_screen)
                buf.download(str(Path(path_to_report, f"{i+1}{os.path.splitext(buf.file_path)[-1]}")))

            try:
                base64.b64decode(report.chat_text)
            except:
                buf: File = context.bot.get_file(report.chat_text)
                buf.download(str(Path(path_to_report, "Переписка.txt")))

        path_to_zip = Path(SendReports.report_dir, now_date.strftime("%m.%Y"))
        if not os.path.exists(path_to_zip):
            os.makedirs(path_to_zip)

        with ZipFile(Path(path_to_zip, now_date.strftime("%d.%m.%Y.zip")), "w") as zipObj:
            for root, dirs, files in os.walk(path_to_reports):
                for file in files:
                    zipObj.write(os.path.join(root, file),
                                 os.path.relpath(os.path.join(root, file),
                                                 os.path.join(path_to_reports, '../..')))

        [context.bot.send_document(admin.user_id, open(Path(path_to_zip, now_date.strftime("%d.%m.%Y.zip")), "rb"),
                                   caption="<b>На проверку</b>") for admin in admin_list]
        shutil.rmtree(path_to_reports)
