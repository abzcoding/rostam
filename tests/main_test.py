import unittest

from rostam.start import auto_build
from rostam.utils.constants import Loader, Settings


class MainTest(unittest.TestCase):

    def test_auto_build(self):
        sample = auto_build(base_dir="", db_type="sqlite", job_runner="local")
        self.assertEqual(Settings.BASE_FOLDER(), "")
        DATABASE = Loader.class_loader(Settings.DB_CONNECTOR())
        db = DATABASE()
        self.assertEqual(db.location, "rostam.db")
        db.delete_db()


if __name__ == '__main__':
    unittest.main()
