import records
from os import path, remove
from sqlalchemy.exc import OperationalError
from rostam.db.models.container import Docker
from rostam.db.models.timeentry import TimeEntry
from rostam.db.models.vcs import GITRepo
from rostam.db.base import BaseDB


class Database(BaseDB):
    def __init__(self, location=None):
        super(Database,self).__init__()
        if location is None:
            location = 'rostam.db'
        self.location = location
        self.db = records.Database("sqlite:///" + str(location))
        self.create_db()

    def create_db(self):
        self.db.query(
            "CREATE TABLE IF NOT EXISTS containers(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, tag TEXT NOT NULL,timeout INT, interval INT, UNIQUE (name,tag) ON CONFLICT ROLLBACK)")
        self.db.query(
            "CREATE TABLE IF NOT EXISTS timetable(id INTEGER PRIMARY KEY AUTOINCREMENT , build_date TIMESTAMP NOT NULL,build_output TEXT,build_result TEXT, container_id INTEGER, FOREIGN KEY(container_id) REFERENCES containers(id))")
        self.db.query(
            "CREATE TABLE IF NOT EXISTS vcs(id INTEGER PRIMARY KEY AUTOINCREMENT, repo TEXT NOT NULL , built_revision TEXT, latest_revision TEXT,container_id INTEGER, FOREIGN KEY(container_id) REFERENCES containers(id),UNIQUE (id,container_id) ON CONFLICT ROLLBACK)")

    def insert(self, value=None):
        if value is None:
            raise RuntimeError("cannot insert None object")
        elif isinstance(value, Docker):
            self.db.query('INSERT INTO containers(name, tag, interval,timeout) VALUES (:name,:tag,:interval,:timeout)',
                          name=value.name, tag=value.tag, interval=value.interval, timeout=value.timeout)
        elif isinstance(value, TimeEntry):
            self.db.query(
                'INSERT INTO timetable(container_id, build_date,build_output,build_result) VALUES (:container_id, :build_date,:build_output,:build_result)',
                container_id=value.container_id, build_date=value.timestamp, build_output=value.build_output,
                build_result=value.build_result)
        elif isinstance(value, GITRepo):
            self.db.query(
                'INSERT INTO vcs(container_id,built_revision,latest_revision,repo) VALUES (:container_id,:built_revision,:latest_revision:repo)',
                container_id=value.container_id, built_revision=value.built_revision,
                latest_revision=value.latest_revision, repo=value.repo)

    def get_container_id(self, container_name, container_tag=None):
        container_id = None
        try:
            if container_tag is None:
                container_tag = "latest"
            rows = self.db.query("SELECT * FROM containers WHERE name=:container_name", container_name=container_name)
            for r in rows:
                if r.name == container_name and r.tag == container_tag:
                    container_id = r.id
                    break
        except OperationalError:
            pass
        return container_id

    def get_container_repo_id(self, container_name, container_tag=None):
        container_id = self.get_container_id(container_name, container_tag)
        try:
            res = self.db.query('SELECT * FROM vcs WHERE container_id=:idd', idd=container_id)
            return int(res[0]['id']), res[0]['repo']
        except OperationalError:
            # no container vcs found
            return -1, None

    def delete_db(self):
        self.db.close()
        if path.isfile(self.location):
            remove(self.location)
