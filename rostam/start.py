# Import Python libs
import argparse
import logging
from os import path
from time import sleep

from rostam.utils.constants import Loader, Settings

log = logging.getLogger(__name__)


def auto_build(base_dir="/opt/rostam/", db_type="sqlite", db_name="rostam", db_username=None, db_password=None,
               job_runner="local", log_file="rostam.log"):
    # set the default db
    if str(db_type).lower() == "mysql":
        db_choice = "rostam.db.mysql.Database"
    elif str(db_type).lower() == "postgresql":
        db_choice = "rostam.db.postgresql.Database"
    else:
        db_choice = "rostam.db.sqlite.Database"
    # set the default runner module
    if str(job_runner).lower() == "saltstack":
        runner_choice = "rostam.schedule.runners.saltstack.Runner"
    elif str(job_runner).lower() == "ansible":
        runner_choice = "rostam.schedule.runners.ansible.Runner"
    else:
        runner_choice = "rostam.schedule.runners.local.Runner"
    Settings(db_connector=db_choice, base_folder=base_dir, runner=runner_choice, log_file=log_file)


def create_jobs(db, sched, runner):
    rows = db.db.query('SELECT * FROM containers')
    log.info(len(rows))
    for r in rows:
        container_id = db.get_container_id(container_name=r['name'], container_tag=r['tag'])
        repo_id, repo = db.get_container_repo_id(container_name=r['name'], container_tag=r['tag'])
        repo_path = path.join(Settings.BASE_FOLDER(), "repos", str(r['name']) + '-' + str(r['tag']))
        if repo_id > 0:
            sched.add_job(job_type=runner.pull, minutes=(int(r['interval']) * 2) / 3,
                          job_id="pull-" + str(r['name']) + '-' + str(r['tag']),
                          args=[container_id, repo, repo_path])
            sched.add_job(job_type=runner.build, minutes=r['interval'],
                          job_id="build-" + str(r['name']) + '-' + str(r['tag']),
                          args=[container_id, repo, repo_path, r['timeout'], r['tag']])
            set_container_status(container_id=container_id, enabled=True)


def main():
    parser = argparse.ArgumentParser(description='automatic docker pull and build system aka "rostam".')
    parser.add_argument('-l', '--location', help='default directory for this application')
    parser.add_argument('-db', '--database', choices=['sqlite', 'postgresql', 'mysql'], help='database type')
    parser.add_argument('-r', '--runner', choices=['local', 'ansible', 'saltstack'], help='runner type')
    parser.add_argument('--dbname', help="name of the default database")
    parser.add_argument('--dbuser', help="username of the database")
    parser.add_argument('--dbpass', help="password of the database")
    parser.add_argument('-o', '--output', help="log output file location")
    args = parser.parse_args()

    auto_build(base_dir=args.location, db_type=args.database, job_runner=args.runner,
               db_name=args.dbname, db_username=args.dbuser, db_password=args.dbpass, log_file=args.output)

    '''
    from rostam.db.sqlite import Database
    from rostam.schedule.runners.local import Runner
    DB_CONNECTOR = Database
    BASE_FOLDER = "/opt/rostam/"
    '''
    # sync repos from properties file
    runner = Loader.class_loader(Settings.RUNNER())
    from rostam.utils.file_sync import sync_properties
    db_location = path.join(Settings.BASE_FOLDER(), "rostam.db")
    sync_properties(properties_file=path.join(Settings.BASE_FOLDER(), "containers.properties"), db_file=db_location)
    db = Loader.class_loader(Settings.DB_CONNECTOR())(location=db_location)
    from rostam.schedule.async import Scheduler
    sched = Scheduler()
    try:
        while True:
            create_jobs(db, sched, runner)
            sleep(60)
    except (KeyboardInterrupt, SystemExit):
        try:
            sched.shutdown()
            db.db.close()
        except Exception:
            pass


if __name__ == '__main__':
    main()
