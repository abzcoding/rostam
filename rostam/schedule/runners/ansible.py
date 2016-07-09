from rostam.schedule.runners.base import BaseRunner


class Runner(BaseRunner):
    def __init__(self):
        pass

    def pull(self, repo_url, repo_path):
        raise NotImplementedError

    def build(self, directory, timeout, tag):
        raise NotImplementedError
