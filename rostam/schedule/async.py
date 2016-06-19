from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from rostam.schedule.runner import pull, build


class Scheduler(object):
    def __int__(self):
        executors = {
            'default': ThreadPoolExecutor(20),
            'processpool': ProcessPoolExecutor(5)
        }
        self.scheduler = BackgroundScheduler(executors=executors)

    def add_job(self, minutes=2, job_id=None, args=None, job_type="build"):
        if job_type == "build":
            job = build
        elif job_type == "clone":
            job = pull
        else:
            return
        if job_id is None:
            self.scheduler.add_job(job, 'interval', minutes=minutes, args=args)
        else:
            self.scheduler.add_job(job, 'interval', minutes=minutes, id=job_id, args=args)

    def start(self):
        self.scheduler.start()

    def shutdown(self):
        self.scheduler.shutdown()
