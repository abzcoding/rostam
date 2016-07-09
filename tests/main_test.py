import sys
import unittest

from mock import patch

from rostam.start import auto_build, main
from rostam.utils.constants import Loader, Settings


class MainTest(unittest.TestCase):

    def test_auto_build(self):
        sample = auto_build(base_dir="", db_type="sqlite", job_runner="local")
        self.assertEqual(Settings.BASE_FOLDER(), "")
        DATABASE = Loader.class_loader(Settings.DB_CONNECTOR())
        db = DATABASE()
        self.assertEqual(db.location, "rostam.db")
        db.delete_db()

    def test_main(self):
        testargs = ["start.py", "-l", "examples", "-o", "examples/rostam.log", "-t", "True"]
        with patch.object(sys, 'argv', testargs):
            sample = main()


if __name__ == '__main__':
    unittest.main()
