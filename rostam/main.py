from time import sleep
from rostam.schedule.async import Scheduler
from rostam.utils.sync import sync


def autobuild(base_dir="/opt/rostam", db_type="sqlite", db_name="rostam", db_username=None, db_password=None,
              job_runner="local"):
    if str(db_type).lower() == "sqlite":
        from rostam.db.sqlite import Database
    elif str(db_type).lower() == "postgresql":
        from rostam.db.postgresql import Database
    elif str(db_type).lower() == "mysql":
        from rostam.db.mysql import Database
    if str(job_runner).lower() == "local":
        from rostam.schedule.runners.local import Runner
    elif str(job_runner).lower() == "ansible":
        from rostam.schedule.runners.ansible import Runner
    elif str(job_runner).lower() == "saltstack":
        from rostam.schedule.runners.saltstack import Runner


def main():
    from rostam.db.sqlite import Database
    from rostam.schedule.runners.local import Runner
    # sync repos from properties file
    runner = Runner()
    sync(properties_file="/opt/rostam/containers.properties")
    db = Database(location="/opt/rostam/rostam.db")
    sched = Scheduler()
    try:
        # TODO: git pull, if something new was there, then pull and build and add to db , and push
        rows = db.db.query('SELECT * FROM containers')
        for r in rows:
            repo_id, repo = db.get_container_repo_id(container_name=r['name'], container_tag=r['tag'])[0]
            if repo_id > 0:
                sched.add_job(job_type=runner.pull, minutes=(int(r['interval']) * 2) / 3,
                              job_id="pull-" + str(r['name']) + '-' + str(r['tag']),
                              args=[repo, "/opt/rostam/repos/" + str(r['name']) + '-' + str(r['tag'])])
            sched.add_job(job_type=runner.build, minutes=r['interval'],
                          job_id="build-" + str(r['name']) + '-' + str(r['tag']),
                          args=["/opt/rostam/repos/" + str(r['name']) + '-' + str(r['tag']), r['timeout'], r['tag']])
            '''
            TODO: check if they're version has been changed and datetime.now() - their_latest_date >= interval
            then schedule their build
            '''
        while True:
            # TODO: check if any new repo has been added and add it to the jobs queue
            pass
    except (KeyboardInterrupt, SystemExit):
        sched.shutdown()
        try:
            db.db.close()
        except Exception:
            pass


if __name__ == '__main__':
    main()
