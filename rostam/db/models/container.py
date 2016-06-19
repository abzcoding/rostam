class Docker(object):
    def __init__(self, name, tag=None, interval=None, timeout=600):
        self.timeout = timeout
        self.name = name
        if tag is None:
            self.tag = "latest"
        else:
            self.tag = tag
        if interval is None:
            self.interval = 60
        elif int(interval) % 10 != 0:
            self.interval = (int(interval / 10) + 1) * 10
        else:
            self.interval = int(interval)

    def __str__(self):
        res = str(self.name) + ":" + str(self.tag)
        return res
