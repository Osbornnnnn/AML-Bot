import os
import ujson
import base64
import shutil
import requests
import datetime
from pathlib import Path
from zipfile import ZipFile
from app.models.user import User
from app.config import TELEGRAM_TOKEN
from app.models.report import Report
from telegram.ext import CallbackContext


class SendReports:
    bot_url: str = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/"
    app_dir: Path = Path(__file__).parent.parent.parent
    tmp_dir: Path = Path(app_dir, "tmp")
    report_dir: Path = Path(app_dir, "reports")
    date: datetime.date = datetime.datetime.today().date() - datetime.timedelta(days=1)

    @staticmethod
    def start(context: CallbackContext):
        reports = Report.get_by_date(SendReports.date)
        admins = User.get_admins()

        if not admins:
            return
        if not reports:
            [context.bot.send_message(admin.user_id, "<b>Вчера отправили 0 репортов -_-</b>") for admin in admins]
            return

        path_to_reports = Path(SendReports.tmp_dir, SendReports.date.strftime("%d.%m.%Y"))
        for report in reports:
            path_to_report = Path(path_to_reports, str(report.user_id), report.report_id)
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

            r = requests.get(SendReports.bot_url+report.welcome_screen).content
            open(Path(path_to_report, f"Знакомство{os.path.splitext(report.welcome_screen)[-1]}"), "wb").write(r)

            r = requests.get(SendReports.bot_url+report.contact_screen).content
            open(Path(path_to_report, f"Контакт{os.path.splitext(report.contact_screen)[-1]}"), "wb").write(r)

            for i in range(len(report.chat_screen)):
                r = requests.get(SendReports.bot_url+report.chat_screen[i]).content
                open(Path(path_to_report, f"{i+1}{os.path.splitext(report.chat_screen[i])[-1]}"), "wb").write(r)

            try:
                base64.b64decode(report.chat_text)
            except:
                r = requests.get(SendReports.bot_url+report.chat_text).content
                open(Path(path_to_report, "Переписка.txt"), "wb").write(r)

        path_to_zip = Path(SendReports.report_dir, SendReports.date.strftime("%m.%Y"))
        if not os.path.exists(path_to_zip):
            os.makedirs(path_to_zip)
        with ZipFile(Path(path_to_zip, SendReports.date.strftime("%d.%m.%Y.zip")), "w") as zipObj:
            for root, dirs, files in os.walk(path_to_reports):
                for file in files:
                    zipObj.write(os.path.join(root, file),
                                 os.path.relpath(os.path.join(root, file),
                                                 os.path.join(path_to_reports, '..')))

        [context.bot.send_document(admin.user_id, open(Path(path_to_zip, SendReports.date.strftime("%d.%m.%Y.zip")), "rb"),
                                   caption="<b>На проверку</b>") for admin in admins]
        shutil.rmtree(path_to_reports)
