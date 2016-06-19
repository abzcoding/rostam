from rostam.vcs.git import Git
from rostam.docker.api import DockerApi
from datetime import datetime
from rostam.schedule.runners.base import BaseRunner


class Runner(BaseRunner):
    def __init__(self):
        pass

    def pull(self, repo_url, repo_path):
        item = Git(repo_url=repo_url, repo_path=repo_path)
        item.pull()
        # TODO: update latest_revision in vcs table

    def build(self, directory, timeout, tag):
        cli = DockerApi(timeout=10 * 60)
        output = cli.build(directory=directory, timeout=timeout, tag=tag)
        time_entry = datetime.now()
        build_time = time_entry.strftime("%Y-%m-%d %H:%M:%S.%f")
        # TODO: insert build_time and output into timetable table and update built_version in vcs table
