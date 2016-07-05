# -*- coding: utf-8 -*-
'''
this module represents the Scheduler Object that will Schedule jobs for us
'''

# Import Python libs
import logging

# Import third party libs
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.schedulers import (SchedulerAlreadyRunningError,
                                    SchedulerNotRunningError)
from apscheduler.schedulers.background import BackgroundScheduler

log = logging.getLogger(__name__)


class Scheduler(object):
    '''
    Schedules Jobs for us asynchronously
    '''

    def __init__(self):
        '''
        it defaults to ``ThreadPoolExecutor`` with 20 threads
        and 5 ``ProcessPoolExecutor`` in the memory
        '''
        executors = {
            'default': ThreadPoolExecutor(20),
            'processpool': ProcessPoolExecutor(5)
        }
        self.scheduler = BackgroundScheduler(executors=executors)

    def add_job(self, job, minutes=2, job_id=None, args=None):
        '''
        add a runnable job to the queue

        :param job: string
        a runnable function
        :param minutes: int : 2
        time between each run of this runnable job
        :param job_id: string : None
        optional, if you want to name a job
        :param args: array : None
        additional parameters to the runnable job

        :return: can add the job or not
        :rtype: boolean
        '''
        try:
            if job_id is None:
                self.scheduler.add_job(job, 'interval', minutes=minutes, args=args)
            else:
                self.scheduler.add_job(job, 'interval', minutes=minutes, id=job_id, args=args)
            return True
        except ConflictingIdError:
            log.error("conflicting id : {0}".format(str(job_id)))
            return False

    def start(self):
        '''
        start the scheduler
        '''
        try:
            self.scheduler.start()
        except SchedulerAlreadyRunningError:
            log.info("scheduler is already running!")

    def shutdown(self):
        '''
        stop the scheduler
        '''
        try:
            self.scheduler.shutdown()
        except SchedulerNotRunningError:
            log.info("scheduler was already stopped!")
