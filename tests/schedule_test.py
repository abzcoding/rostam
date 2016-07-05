import unittest
from time import sleep

from rostam.schedule.async import Scheduler


def tick(arr):
    arr.append("success")


class AsyncTest(unittest.TestCase):

    def test_init(self):
        item = Scheduler()
        self.assertFalse(item.scheduler.running)
        jobs = item.scheduler.get_jobs()
        self.assertListEqual(jobs, [])

    def test_add_job(self):
        item = Scheduler()
        res = []
        item.add_job(tick, minutes=0, args=[res])
        item.start()
        sleep(2)
        self.assertTrue("success" in res)
        item.shutdown()

    def test_start_shutdown(self):
        item = Scheduler()
        item.start()
        self.assertTrue(item.scheduler.running)
        item.shutdown()
        self.assertFalse(item.scheduler.running)

if __name__ == '__main__':
    unittest.main()
