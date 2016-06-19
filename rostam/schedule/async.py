from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

class Scheduler(object):
    def __int__(self):
        executors = {
            'default': ThreadPoolExecutor(20),
            'processpool': ProcessPoolExecutor(5)
        }
        self.scheduler = BackgroundScheduler(executors=executors)

    def add_job(self, job_type, minutes=2, job_id=None, args=None):
        if job_id is None:
            self.scheduler.add_job(job, 'interval', minutes=minutes, args=args)
        else:
            self.scheduler.add_job(job, 'interval', minutes=minutes, id=job_id, args=args)

    def start(self):
        self.scheduler.start()

    def shutdown(self):
        self.scheduler.shutdown()
