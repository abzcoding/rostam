# -*- coding: utf-8 -*-
'''
Inhereted from ``BaseDB`` and will represent a sqlite database
'''

# Import Python libs
import logging
from datetime import datetime, timedelta
from os import path, remove

# Import third party libs
import records
from sqlalchemy.exc import ArgumentError, OperationalError

# Import rostam libs
from rostam.db.base import BaseDB
from rostam.db.models.container import Docker
from rostam.db.models.timeentry import TimeEntry
from rostam.db.models.vcs import GITRepo

log = logging.getLogger(__name__)


class Database(BaseDB):
    '''
    represent common tasks for a sqlite database
    '''

    def __init__(self, location=None):
        '''
        initializes a sqlite db and creates a db file in ``location``

        :param location: string : 'rostam.db'
        Location of the database file
        '''
        super(Database, self).__init__()
        if location is None:
            location = 'rostam.db'
        self.location = location
        try:
            self.db = records.Database("sqlite:///" + str(location))
            self.create_db()
        except ArgumentError as e:
            log.error("Error in creating {0} : {1}".format(str(location), str(e)))
        except AttributeError as e:
            log.error("there are some problems in your query! {0}".format(str(e)))

    def create_db(self):
        '''
        creates a file containing 3 tables (containers, timetable, vcs)
        '''

        self.db.query(
            "CREATE TABLE IF NOT EXISTS containers(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, tag TEXT NOT NULL,timeout INT, interval INT,enabled BOOLEAN, UNIQUE (name,tag) ON CONFLICT ROLLBACK)")
        self.db.query(
            "CREATE TABLE IF NOT EXISTS timetable(id INTEGER PRIMARY KEY AUTOINCREMENT , build_date TIMESTAMP NOT NULL,build_output TEXT,build_result TEXT, container_id INTEGER, FOREIGN KEY(container_id) REFERENCES containers(id))")
        self.db.query(
            "CREATE TABLE IF NOT EXISTS vcs(id INTEGER PRIMARY KEY AUTOINCREMENT, repo TEXT NOT NULL , built_revision TEXT, latest_revision TEXT,container_id INTEGER, FOREIGN KEY(container_id) REFERENCES containers(id),UNIQUE (id,container_id) ON CONFLICT ROLLBACK)")

    def insert(self, value=None):
        '''
        insert an object into the database based on it's type

        :param value: (`Docker` or `TimeEntry` or `GITRepo`): None
        the object that needs to be inserted in the database

        :raises: ``RuntimeError`` when value is None
        '''
        # for using concurrent read and writes
        self.db.query('PRAGMA journal_mode=WAL')
        if value is None:
            log.warn("value cannot be None when inserting into database!")
            raise RuntimeError("cannot insert None object")
        elif isinstance(value, Docker):
            self.db.query('INSERT INTO containers(name, tag, interval,timeout,enabled) VALUES (:name,:tag,:interval,:timeout,:enabled)',
                          name=value.name, tag=value.tag, interval=value.interval, timeout=value.timeout, enabled=value.enabled)
        elif isinstance(value, TimeEntry):
            self.db.query(
                'INSERT INTO timetable(container_id, build_date,build_output,build_result) VALUES (:container_id, :build_date,:build_output,:build_result)',
                container_id=value.container_id, build_date=value.timestamp, build_output=value.build_output,
                build_result=value.build_result)
        elif isinstance(value, GITRepo):
            self.db.query(
                'INSERT INTO vcs(container_id,built_revision,latest_revision,repo) VALUES (:container_id,:built_revision,:latest_revision,:repo)',
                container_id=value.container_id, built_revision=value.built_revision,
                latest_revision=value.latest_revision, repo=value.repo)

    def get_container_id(self, container_name, container_tag=None):
        '''
        get container's id based on it's name and tag

        :param container_name: string
        name of the container
        :param container_tag: string : 'latest'
        tag of the container

        :return: container's id number
        :rtype: ``int``

        :raises: ``OperationalError``
        '''
        container_id = None
        try:
            if container_tag is None:
                container_tag = "latest"
            rows = self.db.query("SELECT * FROM containers WHERE name=:container_name", container_name=container_name)
            for r in rows:
                if r.name == container_name and r.tag == container_tag:
                    container_id = r.id
                    break
        except OperationalError as e:
            log.warn("error happend : {0}".format(e))
        return container_id

    def time_to_build(container_id):
        '''
        calculate the next time that we should build this `container_id`

        :param container_id: int
        container id that we want to calculate it's next build date

        :return: is it time to rebuild the container_id?
        :rtype: boolean
        '''
        time = datetime.now()
        try:
            build_date = self.db.query(
                'SELECT build_date FROM timetable WHERE container_id=:idd ORDER BY build_date DESC LIMIT 1', idd=container_id)[0][0]
            interval = int(self.db.query('SELECT interval FROM containers WHERE id=:idd', idd=container_id)[0][0])
            current_time = time
            build_time = datetime.strptime(build_date, "%Y-%m-%d %H:%M:%S.%f")
            if current_time >= build_time + timedelta(minutes=interval):
                return True
            return False
        except (TypeError, ValueError, OperationalError):
            log.warn("cannot calculate build time for {0}".format(str(container_id)))
            # cannot get build_date or interval
            return False

    def update_vcs_revision(self, container_id, built_revision=None, latest_revision=None):
        '''
        update the build or latest revisions

        :param container_id: int
        id of the container that need to be updated
        :param built_revision: string : None
        latest revision that were built successfully
        :param latest_revision: string : None
        latest revision that were pulled successfully

        :return: was the update operation successfull?
        :rtype: boolean
        '''
        try:
            if built_revision is not None and latest_revision is not None:
                # update both
                self.db.query("UPDATE vcs SET built_revision=:built, latest_revision=:latest WHERE container_id=:idd",
                              built=built_revision, latest=latest_revision, idd=container_id)
            elif built_revision is not None:
                # only update built_revision
                self.db.query("UPDATE vcs SET built_revision=:built WHERE container_id=:idd",
                              built=built_revision, idd=container_id)
            elif latest_revision is not None:
                # only update latest_revision
                self.db.query("UPDATE vcs SET latest_revision=:latest WHERE container_id=:idd",
                              latest=latest_revision, idd=container_id)
            else:
                # nothing has been updated
                return False
            return True
        except OperationalError:
            log.warn("updating the build or latest revision failed")

    def get_container_repo_id(self, container_name, container_tag=None):
        '''
        get containers repository id and url based on it's `container_name` and `container_tag`

        :param container_name: string
        container's name
        :param container_tag: string : None
        container's tag

        :return: container's repository id, container's repository url
        :rtype: ``int``, ``string``
        '''
        container_id = self.get_container_id(container_name, container_tag)
        try:
            res = self.db.query('SELECT * FROM vcs WHERE container_id=:idd', idd=container_id)
            return int(res[0]['id']), res[0]['repo']
        except (OperationalError, TypeError, ValueError, IndexError):
            log.info('no container vcs found for {0}:{1}'.format(str(container_name), str(container_tag)))
            # no container vcs found
            return -1, None

    def set_container_status(self, container_id, enabled):
        try:
            self.db.query("UPDATE containers SET enabled=:enabled WHERE container_id=:idd", enabled=enabled, idd=container_id)
        except OperationalError as e:
            log.warn('error while enabled container {0} : {1}'.format(str(container_id), e))

    def delete_db(self):
        '''
        close and then delete current database
        '''
        self.db.close()
        if path.isfile(self.location):
            remove(self.location)
