from rostam.db.base import BaseDB


class Database(BaseDB):
    def __init__(self):
        super(Database,self).__init__()

    def create_db(self):
        raise NotImplementedError

    def insert(self, value=None):
        raise NotImplementedError

    def get_container_id(self, container_name, container_tag=None):
        raise NotImplementedError

    def get_container_repo_id(self, container_name, container_tag=None):
        raise NotImplementedError

    def delete_db(self):
        raise NotImplementedError
