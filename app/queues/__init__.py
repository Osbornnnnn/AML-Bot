import datetime
from telegram.ext import JobQueue
from .send_reports import SendReports


def setup(job_queue: JobQueue):
    # send_reports_time = (datetime.datetime.now()+datetime.timedelta(seconds=3)).time()
    send_reports_time = datetime.time(9, 0, 0, 000000)

    job_queue.run_daily(SendReports.start, send_reports_time)
