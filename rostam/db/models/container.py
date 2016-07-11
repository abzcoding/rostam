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

    def __init__(self, name, tag="latest", interval=6, timeout=600, remote_name=None, remote_registry=None, enabled=False):
        '''
        :param name: string
        Name of the docker container
        :param tag: string : "latest"
        Tag of the docker container
        :param interval: int : 60
        Interval to rebuild this container in minutes, will round up to 10 minute chunks
        :param timeout: int : 600
        Build Timeout for this container
        :param remote_name: string
        name of the container on the `remote_registry`
        :param remote_registry: string
        remote docker registry server
        :param enabled: boolean : false
        is it enabled or what!?
        '''
        if name is None:
            log.error("Cannot create a docker container with empty name!")
            raise RuntimeError('name of the container cannot be empty')
        self.timeout = timeout
        self.name = name
        self.tag = tag
        if int(interval) == 666:
            # for testing purposes only , p.s: dude i'm not satanist!
            self.interval = 2
        elif int(interval) % 10 != 0 and int(interval) > 0:
            self.interval = (int(interval / 10) + 1) * 10
        else:
            self.interval = int(interval)
        self.enabled = enabled
        if remote_name is None:
            self.remote_name = self.name
        else:
            self.remote_name = remote_name
        if remote_registry is None:
            raise RuntimeError('remote registry cannot be empty')
        self.remote_registry = remote_registry

    def __str__(self):
        '''
        change string representation of this object to name:tag
        '''
        res = str(self.name) + ":" + str(self.tag)
        return res
