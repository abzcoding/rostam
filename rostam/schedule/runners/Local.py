# -*- coding: utf-8 -*-
'''
Inhereted from ``BaseRunner`` and will represent a Runnable Object
'''

# Import Python libs
import logging
from datetime import datetime

# Import rostam libs
from rostam.docker.api import DockerApi
from rostam.main import DB_CONNECTOR as Database
from rostam.main import BASE_FOLDER
from rostam.schedule.runners.base import BaseRunner
from rostam.vcs.git import Git

log = logging.getLogger(__name__)


class Runner(BaseRunner):
    '''
    a runnable class that will pull from vcs and build the container
    '''

    def __init__(self):
        super(Runner, self).__init__()

    def pull(self, repo_url, repo_path):
        '''
        pull to get the latest revision of the repository

        :param repo_url: string
        repository url
        :param repo_path: string
        repository path in local os
        '''
        item = Git(repo_url=repo_url, repo_path=repo_path)
        item.pull()
        log.info("pulled from [0] to [1]".format(str(repo_url), str(repo_path)))
        # TODO:40 update latest_revision in vcs table

    def build(self, directory, timeout, tag):
        '''
        build container

        :param directory: string
        path that contains Dockerfile
        :param timeout: int : 600
        amout of timeout in seconds
        :param tag: string
        tag of the container
        '''
        db = Database(BASE_FOLDER + "rostam.db")
        cli = DockerApi(timeout=10 * 60)
        # TODO:20 check if needs to be built or not
        output = cli.build(directory=directory, timeout=timeout, tag=tag)
        log.debug("build result : [0]".format(output))
        time_entry = datetime.now()
        build_time = time_entry.strftime("%Y-%m-%d %H:%M:%S.%f")
        # TODO:30 insert build_time and output into timetable table and update built_version in vcs table
        db.db.close()
