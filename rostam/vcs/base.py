from abc import ABCMeta, abstractmethod


class Base:
    __metaclass__ = ABCMeta

    def __init__(self, repo_url, repo_path):
        self.repo_url = repo_url
        self.repo_path = repo_path
        self.repo = None

    @abstractmethod
    def pull(self):
        pass

    @abstractmethod
    def push(self):
        pass