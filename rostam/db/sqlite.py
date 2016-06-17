import records
from os import path, remove
from sqlalchemy.exc import OperationalError
from rostam.db.models.container import Docker, TimeEntry


class Database(object):
    def __init__(self, location=None):
        if location is None:
            location = 'rostam.db'
        self.location = location
        self.db = records.Database("sqlite:///" + str(location))
        self.create_db()

    def create_db(self):
        self.db.query(
            "CREATE TABLE IF NOT EXISTS containers(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, tag TEXT NOT NULL, interval INT, UNIQUE (name,tag) ON CONFLICT ROLLBACK)")
        self.db.query(
            "CREATE TABLE IF NOT EXISTS timetable(id INTEGER PRIMARY KEY AUTOINCREMENT , build_date TIMESTAMP NOT NULL, container_id INTEGER, FOREIGN KEY(container_id) REFERENCES containers(id))")

    def insert(self, value=None):
        if value is None:
            raise RuntimeError("cannot insert None object")
        elif isinstance(value, Docker):
            self.db.query('INSERT INTO containers(name, tag, interval) VALUES (:name,:tag,:interval)',
                          name=value.name, tag=value.tag, interval=value.interval)
        elif isinstance(value, TimeEntry):
            self.db.query('INSERT INTO timetable(container_id, build_date) VALUES (:container_id, :build_date)',
                          container_id=self.get_container_id(container_name=value.name, container_tag=value.tag),
                          build_date=value.timestamp)

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

    def delete_db(self):
        self.db.close()
        if path.isfile(self.location):
            remove(self.location)
