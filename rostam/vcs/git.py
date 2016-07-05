# -*- coding: utf-8 -*-
'''
Inhereted from ``Base`` and will implement some common functionalities of the git vcs
'''

# Import Python libs
import logging
from os import path

# Import third party libs
from gittle import Gittle, GittleAuth

# Import rostam libs
from rostam.vcs.base import Base

log = logging.getLogger(__name__)


class Git(Base):
    '''
    a git vcs object
    '''

    def __init__(self, repo_url, repo_path):
        super(Git, self).__init__(repo_url, repo_path)
        self._cloned = path.exists(repo_path)

    def clone(self, key_file=None, username=None, password=None):
        '''
        clone the git repo

        :param key_file: string : None
        location of private key if you want to connect using RSA
        :param username: string : None
        username if you wnat to connect using basic authentication
        :param password: string : None
        password if you wnat to connect using basic authentication
        '''
        if self._cloned is False:
            if key_file is not None:
                # Authentication with RSA private key
                key_file = open(key_file)
                Gittle.clone(self.repo_url, self.repo_path, auth=GittleAuth(pkey=key_file))
            elif username is not None and password is not None:
                # With username and password
                Gittle.clone(self.repo_url, self.repo_path,
                             auth=GittleAuth(username=username, password=password))
            else:
                # Without anything , is it even possible?
                Gittle.clone(self.repo_url, self.repo_path)

    def pull(self):
        '''
        pull the latest version
        '''
        self.clone()
        self.repo = Gittle(self.repo_path, origin_uri=self.repo_url)
        self.repo.pull()

    def push(self):
        '''
        push to the remote repository
        '''
        raise NotImplementedError
