import unittest

from rostam.db.sqlite import Database
from rostam.main import BASE_FOLDER
from rostam.utils.file_sync import read_properties_file, sync_properties


class FileSyncTest(unittest.TestCase):

    def test_read_properties_file(self):
        res = read_properties_file()
        self.assertTrue(len(res['hello world:latest']) == 4)
        self.assertEqual(res['hello world:latest']['interval'], 60)
        self.assertEqual(res['hello world:latest']['tag'], 'latest')
        self.assertEqual(res['hello world:latest']['repo'], 'https://github.com/docker-library/hello-world.git')

    def test_sync_properties(self):
        sync_properties()
        db = Database(location=BASE_FOLDER + "rostam.db")
        res = db.db.query('select * from vcs')
        self.assertEqual(res[0]['id'], 1)
        self.assertEqual(res[0]['repo'], 'https://github.com/docker-library/hello-world.git')
        self.assertIsNone(res[0]['built_revision'])
        self.assertIsNone(res[0]['latest_revision'])
        self.assertEqual(res[0]['container_id'], 1)
        db.delete_db()

if __name__ == '__main__':
    unittest.main()
