# -*- coding: utf-8 -*-
'''
base class for database representation
'''

# Import Python libs
from abc import ABCMeta, abstractmethod


class BaseDB:
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def create_db(self):
        '''
        create databse
        '''
        pass

    @abstractmethod
    def insert(self, value=None):
        '''
        insert value into database
        '''
        pass

    @abstractmethod
    def get_container_id(self, container_name, container_tag=None):
        '''
        get container id by using ``container_name`` and ``container_tag``

        :param container_name: string
        name of the container that we want it's id
        :param container_tag: None
        tag of the infamous container!

        :return: id of the container that we searched for by using `container_name`:`container_tag`
        :rtype: ``int``
        '''
        pass

    @abstractmethod
    def get_container_repo_id(self, container_name, container_tag=None):
        '''
        get container's repository id by using ``container_name`` and ``container_tag``

        :param container_name: string
        name of the container that we want it's repository's id
        :param container_tag: None
        tag of the infamous container!

        :return: repository id of the container that we searched for by using `container_name`:`container_tag`
        :rtype: ``int``
        '''
        pass

    @abstractmethod
    def delete_db(self):
        '''
        delete the database
        :note: be carefull while using this method
        '''
        pass
