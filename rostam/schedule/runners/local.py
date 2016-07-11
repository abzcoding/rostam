# -*- coding: utf-8 -*-
'''
Inhereted from ``BaseRunner`` and will represent a Runnable Object
'''

# Import Python libs
import logging
from datetime import datetime
from os import path

# Import third party libs
from docker.errors import DockerException, InvalidVersion
from gittle import Gittle

# Import rostam libs
from rostam.db.models.timeentry import TimeEntry
from rostam.docker.api import DockerApi
from rostam.schedule.runners.base import BaseRunner
from rostam.utils.constants import Loader, Settings
from rostam.vcs.git import Git

Database = Loader.class_loader(Settings.DB_CONNECTOR())
BASE_FOLDER = Settings.BASE_FOLDER()

log = logging.getLogger(__name__)


class Runner(BaseRunner):
    '''
    a runnable class that will pull from vcs and build the container
    '''

    def __init__(self):
        super(Runner, self).__init__()

    @classmethod
    def pull(cls, container_id, repo_url, repo_path):
        '''
        pull to get the latest revision of the repository

        :param container_id: int
        id of the container
        :param repo_url: string
        repository url
        :param repo_path: string
        repository path in local os
        '''
        db = Database(path.join(BASE_FOLDER, "rostam.db"))
        item = Git(repo_url=repo_url, repo_path=repo_path)
        item.pull()
        log.info("pulled from {0} to {1}".format(str(repo_url), str(repo_path)))
        db.update_vcs_revision(container_id=container_id, latest_revision=item.repo.head)
        db.db.close()

    @classmethod
    def push(cls, name, remote_name, remote_registry, container_id, repo, repo_path, timeout=600, tag="latest", stream=True, insecure_registry=False):
        '''
        push images to docker repository

        :param name: string
        container's name
        :param tag: string : 'latest'
        container's tag
        :param remote_name: string
        name of the image on the `remote_registry`
        :param remote_registry: string
        remote docker registry server
        :param container_id: int
        id of the container
        :param repo_url: string
        repository url
        :param repo_path: string
        path that contains Dockerfile
        :param timeout: int : 600
        amount of timeout in seconds
        :param stream: bool : True
        Stream the output as a blocking generator
        :param insecure_registry: bool : False
        Use http:// to connect to the registry
        '''
        db = Database(path.join(BASE_FOLDER, "rostam.db"))
        cli = DockerApi(timeout=timeout)
        try:
            if Runner.build(container_id, repo, repo_path, timeout, str(name).replace(' ', '-') + ":" + str(tag)):
                if cli.tag(str(name).replace(' ', '-') + ":" + str(tag), str(remote_registry) + "/" + str(remote_name), str(tag)):
                    output = cli.push(name=str(remote_registry) + "/" + str(remote_name),
                                      tag=str(tag), stream=stream, insecure_registry=insecure_registry)
                    log.warn('push result : {0}'.format(''.join(output)))
                    db.db.close()
                    return True
                else:
                    log.warn('cannot tag the following image : {0}')
            db.db.close()
            return False
        except Exception as e:
            log.warn('pushing {0} failed : {1}'.format(name, e))
            db.db.close()
            return False

    @classmethod
    def build(cls, container_id, repo_url, repo_path, timeout, tag):
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
        db = Database(path.join(BASE_FOLDER, "rostam.db"))
        cli = DockerApi(timeout=timeout)
        if db.time_to_build(container_id):
            try:
                output = cli.build(directory=repo_path, timeout=timeout, tag=tag)
                log.debug("build result : {0}".format(''.join(output)))
                time_entry = datetime.now()
                build_time = time_entry.strftime("%Y-%m-%d %H:%M:%S.%f")
                item = Git(repo_url=repo_url, repo_path=repo_path)
                item.pull()
                built_revision = item.repo.head
                # repo = Gittle.clone(repo_url, repo_path)
                # built_revision = repo.commit_info(end=1)[0]
                db.update_vcs_revision(container_id=container_id, built_revision=built_revision)
                entry = TimeEntry(container_id=container_id, timestamp=build_time, build_output=''.join(output))
                db.insert(entry)
                log.info("successfully build {0} at revision : {1}".format(
                    str(container_id), str(built_revision)))
                db.db.close()
                return True
            except (TypeError, DockerException, InvalidVersion):
                log.warn("building {0} failed".format(str(container_name) + ":" + str(container_tag)))
                db.db.close()
                return False
        else:
            db.db.close()
            return True
