from rostam.db.models.vcs import GITRepo
from rostam.db.sqlite import Database
from rostam.db.models.container import Docker


def read_properties_file(properties_file="examples/containers.properties"):
    containers = {}
    with open(properties_file, mode='r') as inp:
        lines = inp.readlines()
        for line in lines:
            try:
                name, tag, repo, interval = line.strip().split(',')
                containers[str(name) + ":" + str(tag)] = {'name': name, 'tag': tag, 'repo': repo,
                                                          'interval': int(interval)}
            except Exception:
                pass
    return containers


def sync(properties_file="examples/containers.properties"):
    db = Database(location="/opt/rosta/rostam.db")
    rows = db.db.query('SELECT * FROM containers')
    # TODO: read from a properties file and sync all the repositories
    containers = read_properties_file(properties_file)
    # STEP 1: make sure all repositories exist in containers table
    for item in containers.values():
        if db.get_container_id(item['name'], item['tag']) is None:
            cn = Docker(name=item['name'], tag=item['tag'], interval=item['interval'])
            db.insert(cn)
    # STEP 2: make sure all containers have a VCS repo
    for r in rows:
        if 'tag' not in r:
            vcs_id = db.get_container_repo_id(container_name=r['name'])
            container_id = db.get_container_id(container_name=r['name'])
        else:
            vcs_id = db.get_container_repo_id(container_name=r['name'], container_tag=r['tag'])
            container_id = db.get_container_id(container_name=r['name'], container_tag=r['tag'])
        if vcs_id < 0:
            # there is no vcs for this container, add it yourself
            item = GITRepo(container_id=container_id, repo=containers[r['name'] + ":" + r['tag']]['repo'])
            db.insert(item)
    db.db.close()
