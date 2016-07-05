from time import sleep

from rostam.schedule.async import Scheduler

DB_CONNECTOR = None
BASE_FOLDER = ""
RUNNER = None


def auto_build(base_dir="/opt/rostam/", db_type="sqlite", db_name="rostam", db_username=None, db_password=None,
               job_runner="local"):
    # set the default db
    if str(db_type).lower() == "sqlite":
        from rostam.db.sqlite import Database
    elif str(db_type).lower() == "postgresql":
        from rostam.db.postgresql import Database
    elif str(db_type).lower() == "mysql":
        from rostam.db.mysql import Database
    # set the default runner module
    if str(job_runner).lower() == "local":
        from rostam.schedule.runners.local import Runner
    elif str(job_runner).lower() == "ansible":
        from rostam.schedule.runners.ansible import Runner
    elif str(job_runner).lower() == "saltstack":
        from rostam.schedule.runners.saltstack import Runner
    DB_CONNECTOR = Database
    BASE_FOLDER = base_dir
    RUNNER = Runner


def main():
    # use the default settings : local runner + sqlite
    auto_build()
    '''
    from rostam.db.sqlite import Database
    from rostam.schedule.runners.local import Runner
    DB_CONNECTOR = Database
    BASE_FOLDER = "/opt/rostam/"
    '''
    # sync repos from properties file
    runner = RUNNER()
    from rostam.utils.file_sync import sync_properties
    sync_properties(properties_file=BASE_FOLDER + "containers.properties")
    db = Database(location=BASE_FOLDER + "rostam.db")
    sched = Scheduler()
    try:
        rows = db.db.query('SELECT * FROM containers')
        for r in rows:
            container_id = b.get_container_id(container_name=r['name'], container_tag=r['tag'])
            repo_id, repo = db.get_container_repo_id(container_name=r['name'], container_tag=r['tag'])[0]
            repo_path = BASE_FOLDER + "repos/" + str(r['name']) + '-' + str(r['tag'])
            if repo_id > 0:
                sched.add_job(job_type=runner.pull, minutes=(int(r['interval']) * 2) / 3,
                              job_id="pull-" + str(r['name']) + '-' + str(r['tag']),
                              args=[container_id, repo, repo_path])
                sched.add_job(job_type=runner.build, minutes=r['interval'],
                              job_id="build-" + str(r['name']) + '-' + str(r['tag']),
                              args=[container_id, repo, repo_path, r['timeout'], r['tag']])
        while False:
            # TODO:10 check if any new repo has been added and add it to the jobs queue
            pass
    except (KeyboardInterrupt, SystemExit):
        try:
            sched.shutdown()
            db.db.close()
        except Exception:
            pass


if __name__ == '__main__':
    main()
