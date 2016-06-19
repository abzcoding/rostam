from rostam.vcs.base import Base
from os import path
from gittle import Gittle, GittleAuth


class Git(Base):
    def __init__(self, repo_url, repo_path):
        super(Git, self).__init__(repo_url, repo_path)
        self._cloned = path.exists(repo_path)

    def clone(self, key_file=None, username=None, password=None):
        if self._cloned is False:
            if key_file is not None:
                # Authentication with RSA private key
                key_file = open(key_file)
                Gittle.clone(self.repo_url, self.repo_path, auth=GittleAuth(pkey=key_file))
            elif username is not None and password is not None:
                # With username and password
                Gittle.clone(self.repo_url, self.repo_path,
                             auth=GittleAuth(username=username, password=password))
            Gittle.clone(self.repo_url, self.repo_path)

    def pull(self):
        self.clone()
        self.repo = Gittle(self.repo_path, origin_uri=self.repo_url)
        self.repo.pull()

    def push(self):
        raise NotImplementedError
