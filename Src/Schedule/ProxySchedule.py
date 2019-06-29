from apscheduler.schedulers.blocking import BlockingScheduler
from Config import ConfigManager
from Notify import NotifyManager
from Log.LogManager import log

import logging
import datetime

DISPATCH_EVENT_LIST = [
    "fetch_new_proxy_interval",
    "verify_raw_proxy_interval",
    "verify_useful_proxy_interval",
    "clean_raw_proxy_interval",
    "clean_useful_proxy_interval",
]

SCHEDULE_LOG_PATH = "logs/schedule.log"

logger = logging.getLogger() 
file_handler = logging.FileHandler(SCHEDULE_LOG_PATH)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

class ProxySchedule(BlockingScheduler):
    def __init__(self, **kwargs):
        super(ProxySchedule, self).__init__(logger=logger, **kwargs)
        self.task_handler_hash = {}

        NotifyManager.register_event(NotifyManager.NOTIFY_EVENT["AFTER_SETTING_CHANGE"], self.dispatch_event)

    def dispatch_event(self, **kwargs):
        event_name = kwargs.get("event_name")
        event_data = kwargs.get("event_data")

        if event_name in DISPATCH_EVENT_LIST:
            self.update_job_interval(**event_data)


    def update_job_interval(self, **kwargs):
        job_name = kwargs.get("job_name")

        value = ConfigManager.setting_config.setting.get(job_name)
        trigger_args = { "minutes": value }
        trigger='interval'
        job = self._update_job(job_name, trigger, **trigger_args)
        log.info("update_job_interval: {job_name}, {job}".format(job_name=job_name, job=job))
        return job

    def _update_job(self, job_name, trigger, **trigger_args):
        return self.reschedule_job(job_name, trigger=trigger, **trigger_args)

    def run(self):
        now = datetime.datetime.now()
        for name, handler in self.task_handler_hash.items():
            value = ConfigManager.setting_config.setting.get(name)
            self.add_job(handler, "interval", id=name, minutes=value, next_run_time=now)

        self.start()