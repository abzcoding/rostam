# -*- coding: utf-8 -*-
'''
this module will represent possible version control system objects
'''

# Import Python libs
import logging

log = logging.getLogger(__name__)  # pylint: disable=C0103


class GITRepo(object):
    '''
    Represent git version control system
    https://en.wikipedia.org/wiki/Git_(software)
    '''

    def __init__(self, container_id, repo, built_revision=None, latest_revision=None):
        '''
        :param container_id: integer
        id of this container in the ```containers``` table, it's a foreign key
        :param repo: string
        repository address of this container
        :param built_revision: string : None
        lastest build was from which revision of this repository
        :param latest_revision: string : `built_revision`
        latest available revision of this repository

        :raises: ``RuntimeError``
        '''
        try:
            self.repo = repo
            if len(self.repo) < 2:
                raise ValueError
            self.container_id = int(container_id)
        except (TypeError, ValueError):
            log.error("container_id must be a non null integer and reposity url cannot be null")
            raise RuntimeError
        self.built_revision = built_revision
        if latest_revision is None:
            latest_revision = built_revision
        self.latest_revision = latest_revision
