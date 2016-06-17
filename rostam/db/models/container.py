from datetime import datetime
from abc import ABCMeta


class Base:
    __metaclass__ = ABCMeta

    def __init__(self, name, tag=None):
        self.name = name
        if tag is None:
            self.tag = "latest"
        else:
            self.tag = tag


class Docker(Base):
    def __init__(self, name, tag=None, interval=None):
        super(Docker, self).__init__(name=name, tag=tag)
        if interval is None:
            self.interval = 60
        elif int(interval) % 10 != 0:
            self.interval = (int(interval / 10) + 1) * 10
        else:
            self.interval = int(interval)

    def __str__(self):
        res = str(self.name) + ":" + str(self.tag)
        return res


class TimeEntry(Base):
    def __init__(self, name, tag=None, timestamp=None):
        super(TimeEntry, self).__init__(name=name, tag=tag)
        if timestamp is None:
            self.timestamp = datetime.now()
        else:
            self.timestamp = timestamp
