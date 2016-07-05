# -*- coding: utf-8 -*-
'''
TimeEntry Object for ``timetable`` table
'''

# Import Python libs
import logging
from datetime import datetime

log = logging.getLogger(__name__)  # pylint: disable=C0103


class TimeEntry(object):
    '''
    Represent a Container build time entry object
    '''

    def __init__(self, container_id, timestamp=None, build_output=None, build_result="succeed"):
        '''
        :param container_id: integer
        id of this container in the ```containers``` table, it's a foreign key
        :param timestamp: string : datetime.datetime.now()
        build time of this entry
        :param build_output: string : ""
        container build stdout
        :param build_result: string : "succeed"
        "succeed" if the build process was successfull and "failed" otherwise
        '''
        try:
            self.container_id = int(container_id)
        except (TypeError, ValueError):
            log.error("TimeEntry container_id must be non empty and of type integer")
        if timestamp is None:
            self.timestamp = datetime.now()
        else:
            self.timestamp = timestamp
        if build_output is None:
            build_output = ""
        self.build_output = build_output
        self.build_result = build_result
