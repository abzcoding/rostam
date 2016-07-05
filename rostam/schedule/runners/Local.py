# -*- coding: utf-8 -*-
'''
Inhereted from ``BaseRunner`` and will represent a Runnable Object
'''

# Import Python libs
import logging
from datetime import datetime

# Import third party libs
from docker.errors import DockerException, InvalidVersion

# Import rostam libs
from rostam.db.models.timeentry import TimeEntry
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

    def pull(self, container_id, repo_url, repo_path):
        '''
        pull to get the latest revision of the repository

        :param container_id: int
        id of the container
        :param repo_url: string
        repository url
        :param repo_path: string
        repository path in local os
        '''
        db = Database(BASE_FOLDER + "rostam.db")
        item = Git(repo_url=repo_url, repo_path=repo_path)
        item.pull()
        log.info("pulled from {0} to {1}".format(str(repo_url), str(repo_path)))
        db.update_vcs_revision(container_id=container_id, latest_revision=item.repo.commit_info(end=1)[0])
        db.db.close()

    def build(self, container_id, repo_url, repo_path, timeout, tag):
        '''
        build container

        :param container_id: int
        id of the container
        :param repo_url: string
        repository url
        :param repo_path: string
        path that contains Dockerfile
        :param timeout: int : 600
        amount of timeout in seconds
        :param tag: string
        tag of the container
        '''
        db = Database(BASE_FOLDER + "rostam.db")
        cli = DockerApi(timeout=10 * 60)
        if db.time_to_build(container_id):
            try:
                output = cli.build(directory=repo_path, timeout=timeout, tag=tag)
                log.debug("build result : {0}".format(output))
                time_entry = datetime.now()
                build_time = time_entry.strftime("%Y-%m-%d %H:%M:%S.%f")
                item = Git(repo_url=repo_url, repo_path=repo_path)
                built_revision = item.repo.commit_info(end=1)[0]
                db.update_vcs_revision(container_id=container_id, built_revision=built_revision)
                entry = TimeEntry(container_id=container_id, timestamp=build_time, build_output=output)
                db.insert(entry)
                log.info("successfully build {0} at revision : {1}".format(
                    str(container_name) + ":" + str(container_tag), str(built_revision)))
                return True
            except (TypeError, DockerException, InvalidVersion):
                log.warn("building {0} failed".format(str(container_name) + ":" + str(container_tag)))
                return False
        else:
            return True
        db.db.close()
