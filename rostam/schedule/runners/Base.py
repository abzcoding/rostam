from abc import ABCMeta, abstractmethod


class BaseRunner:
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def pull(self, repo_url, repo_path):
        pass

    @abstractmethod
    def build(self, directory, timeout, tag):
        pass
