from apscheduler.schedulers.blocking import BlockingScheduler
from Config.ConfigManager import config
from Notify.NotifyManager import register_notify
from Log.LogManager import log

import datetime

class ProxySchedule(BlockingScheduler):
    def __init__(self, **kwargs):
        super(ProxySchedule, self).__init__(**kwargs)
        self.task_handler_hash = {}

    def update_job_interval(self, job_id):
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
            register_notify(name, self.update_job_interval)

            value = getattr(config.setting.Interval, name)
            self.add_job(handler, "interval", id=name, minutes=value, next_run_time=now)

        self.start()