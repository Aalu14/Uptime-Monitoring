from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from url import check_and_alert  
import time

scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
scheduler.start()

def run_monitoring_task():
    print("Running scheduled monitoring task...")
    check_and_alert()  

job = scheduler.add_job(
    run_monitoring_task,
    CronTrigger(hour="15", minute="17"),  
)

print("Cron job added:", job)

try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
    print("Scheduler shut down.")
