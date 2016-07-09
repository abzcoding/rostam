# -*- coding: utf-8 -*-
'''
some functions to help start the project from ground up
'''

# Import Python libs
import logging

# Import rostam libs
import rostam.utils.log_setup
from rostam.db.models.container import Docker
from rostam.db.models.vcs import GITRepo
from rostam.db.sqlite import Database
from rostam.utils.constants import Settings

log = logging.getLogger(__name__)


def read_properties_file(properties_file="examples/containers.properties"):
    '''
    read from a properties_file to create containers

    :param properties_file: string : 'examples/containers.properties'
    location of the properties file

    :return: array that contains all of the mentioned containers in the ``properties_file``
    :rtype: array
    '''
    containers = {}
    with open(properties_file, mode='r') as inp:
        lines = inp.readlines()
        for line in lines:
            try:
                name, tag, repo, interval = line.strip().split(',')
                containers[str(name) + ":" + str(tag)] = {'name': name, 'tag': tag, 'repo': repo,
                                                          'interval': int(interval)}
            except Exception as e:
                log.warn("exception happend while reading from {0} : {1}".format(properties_file, e))
    return containers


def sync_properties(properties_file="examples/containers.properties", db_file="rostam.db"):
    '''
    add all the repositories in the properties file to the database
    and then make sure all them have their own vcs repository in the db

    :param properties_file: string : 'examples/containers.properties'
    location of the properties file
    '''
    db = Database(location=db_file)
    rows = db.db.query('SELECT * FROM containers')
    containers = read_properties_file(properties_file)
    # STEP 1: make sure all repositories exist in containers table
    for item in containers.values():
        if db.get_container_id(item['name'], item['tag']) is None:
            cn = Docker(name=item['name'], tag=item['tag'], interval=item['interval'])
            db.insert(cn)
    log.info("finished reading from {0}".format(properties_file))
    # STEP 2: make sure all containers have a VCS repo
    rows = db.db.query('SELECT * FROM containers')
    for r in rows:
        if r['tag'] is None:
            vcs_id, vcs_repo = db.get_container_repo_id(container_name=r['name'])
            container_id = db.get_container_id(container_name=r['name'])
        else:
            vcs_id, vcs_repo = db.get_container_repo_id(container_name=r['name'], container_tag=r['tag'])
            container_id = db.get_container_id(container_name=r['name'], container_tag=r['tag'])
        if vcs_id < 0:
            # there is no vcs for this container, add it yourself
            item = GITRepo(container_id=container_id, repo=containers[r['name'] + ":" + r['tag']]['repo'])
            db.insert(item)
            log.info("added {0} to vcs table".format(r['name']))
    db.db.close()
