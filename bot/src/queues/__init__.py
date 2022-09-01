import datetime
from telegram.ext import JobQueue
from .send_reports import SendReports
from .. import config

def setup(job_queue: JobQueue):
    # send_reports_time = (datetime.datetime.now()+datetime.timedelta(seconds=3)).time()
    send_reports_time = datetime.time(hour=9, tzinfo=config.TIMEZONE)

    job_queue.run_daily(SendReports.start, send_reports_time)
