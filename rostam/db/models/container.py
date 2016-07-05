# -*- coding: utf-8 -*-
'''
Docker Container Object for ``containers`` table
'''

# Import Python libs
import logging

log = logging.getLogger(__name__)  # pylint: disable=C0103


class Docker(object):
    '''
    Represent a Docker container object with the support of name, tag , build interval and build timeout
    '''

    def __init__(self, name, tag=None, interval=None, timeout=600):
        '''
        :param name: string
        Name of the docker container
        :param tag: string : "latest"
        Tag of the docker container
        :param interval: int : 60
        Interval to rebuild this container in minutes, will round up to 10 minute chunks
        :param timeout: int : 600
        Build Timeout for this container
        '''
        if name is None:
            log.error("Cannot create a docker container with empty name!")
            raise RuntimeError
        self.timeout = timeout
        self.name = name
        if tag is None:
            self.tag = "latest"
        else:
            self.tag = tag
        if interval is None:
            self.interval = 60
        elif int(interval) % 10 != 0:
            self.interval = (int(interval / 10) + 1) * 10
        else:
            self.interval = int(interval)

    def __str__(self):
        '''
        change string representation of this object to name:tag
        '''
        res = str(self.name) + ":" + str(self.tag)
        return res
