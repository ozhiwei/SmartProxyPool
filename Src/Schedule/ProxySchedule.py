from apscheduler.schedulers.blocking import BlockingScheduler
from Config.ConfigManager import config
from Notify.NotifyManager import register_event, NOTIFY_EVENT
from Log.LogManager import log

import datetime

DISPATCH_EVENT_LIST = [
    "fetch_new_proxy_interval",
    "verify_raw_proxy_interval",
    "verify_useful_proxy_interval",
    "clean_raw_proxy_interval",
    "clean_useful_proxy_interval",
]

class ProxySchedule(BlockingScheduler):
    def __init__(self, **kwargs):
        super(ProxySchedule, self).__init__(**kwargs)
        self.task_handler_hash = {}

        register_event(NOTIFY_EVENT["AFTER_SETTING_CHANGE"], self.dispatch_event)

    def dispatch_event(self, **kwargs):
        event_name = kwargs.get("event_name")
        event_data = kwargs.get("event_data")

        if event_name in DISPATCH_EVENT_LIST:
            self.update_job_interval(**event_data)


    def update_job_interval(self, **kwargs):
        job_id = kwargs.get("job_id")

        value = getattr(config.setting.Interval, job_id)
        trigger_args = { "minutes": value }
        trigger='interval'
        job = self._update_job(job_id, trigger, **trigger_args)
        log.info("update_job_interval: {job_id}, {job}".format(job_id=job_id, job=job))
        return job

    def _update_job(self, job_id, trigger, **trigger_args):
        return self.reschedule_job(job_id, trigger=trigger, **trigger_args)

    def run(self):
        now = datetime.datetime.now()
        for name, handler in self.task_handler_hash.items():
            value = getattr(config.setting.Interval, name)
            self.add_job(handler, "interval", id=name, minutes=value, next_run_time=now)

        self.start()