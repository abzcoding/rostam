class GITRepo(object):
    def __int__(self, container_id, repo, built_revision=None, latest_revision=None):
        self.repo = repo
        self.container_id = container_id
        self.built_revision = built_revision
        if self.latest_revision is None:
            latest_revision = built_revision
        self.latest_revision = latest_revision
