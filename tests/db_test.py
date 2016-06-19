from os import path, remove
import unittest
from rostam.db.sqlite import Database
from rostam.db.models.container import Docker
from rostam.db.models.timeentry import TimeEntry
from datetime import datetime


class SQLITETest(unittest.TestCase):
    def test_database_create(self):
        location = 'rostam.db'
        if path.isfile(location):
            remove(location)
        db = Database()
        self.assertTrue(path.isfile(db.location), "Sqlite.create() did not create the appropriate file")
        table_names = db.db.get_table_names()
        self.assertTrue('containers' in table_names)
        self.assertTrue('timetable' in table_names)

    def test_database_get_container_id(self):
        location = 'rostam.db'
        if path.isfile(location):
            remove(location)
        db = Database()
        container_id = db.get_container_id(container_name="doesnotexist")
        self.assertIsNone(container_id)
        box = Docker(name="justfortest")
        db.insert(value=box)
        container_id = db.get_container_id(container_name="justfortest")
        self.assertEqual(container_id, 1)

    def test_database_insert(self):
        location = 'rostam.db'
        if path.isfile(location):
            remove(location)
        db = Database()
        container_id = db.get_container_id(container_name="doesnotexist")
        self.assertIsNone(container_id)
        box = Docker(name="insertTest")
        db.insert(value=box)
        dc1 = {'name': 'insertTest'}
        rows = db.db.query("select name from containers")
        self.assertIn(dc1, rows.all(as_dict=True))
        time_entry = datetime(2014, 1, 5, 16, 52, 57, 523000)
        entry = TimeEntry(container_id=1, timestamp=time_entry, build_output="something")
        db.insert(entry)
        rows = db.db.query("select build_date,container_id,build_output,build_result from timetable")
        dc2 = {'build_date': time_entry.strftime("%Y-%m-%d %H:%M:%S.%f"), 'build_output': 'something',
               'build_result': 'succeed', 'container_id': 1}
        self.assertIn(dc2, rows.all(as_dict=True))

    def test_database_remove(self):
        location = 'rostam.db'
        db = Database()
        db.delete_db()
        self.assertFalse(path.isfile(location))


if __name__ == '__main__':
    unittest.main()
