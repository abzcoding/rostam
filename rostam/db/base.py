from abc import ABCMeta, abstractmethod


class BaseDB:
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def create_db(self):
        pass

    @abstractmethod
    def insert(self, value=None):
        pass

    @abstractmethod
    def get_container_id(self, container_name, container_tag=None):
        pass

    @abstractmethod
    def get_container_repo_id(self, container_name, container_tag=None):
        pass

    @abstractmethod
    def delete_db(self):
        pass
