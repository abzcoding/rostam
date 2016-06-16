from rostam.vcs.base import Base
from gittle import Gittle, GittleAuth


class Git(Base):
    def __init__(self, repo_url, repo_path):
        super(Git, self).__init__(repo_url, repo_path)
        self.__cloned = False

    def clone(self, key_file=None, username=None, password=None):
        if self.__cloned is False:
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
