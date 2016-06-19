from time import sleep
from rostam.db.sqlite import Database
from rostam.schedule.async import Scheduler
from rostam.utils.sync import sync


def main():
    # sync repos from properties file
    sync(properties_file="/opt/rostam/containers.properties")
    db = Database(location="/opt/rostam/rostam.db")
    sched = Scheduler()
    try:
        # TODO: git pull, if something new was there, then pull and build and add to db , and push
        rows = db.db.query('SELECT * FROM containers')
        for r in rows:
            repo_id, repo = db.get_container_repo_id(container_name=r['name'], container_tag=r['tag'])[0]
            if repo_id > 0:
                sched.add_job(minutes=(int(r['interval']) * 2) / 3,
                              job_id="pull-" + str(r['name']) + '-' + str(r['tag']),
                              args=[repo],
                              job_type="pull")
            sched.add_job(minutes=r['interval'], job_id="build-" + str(r['name']) + '-' + str(r['tag']))
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
