from docker import Client
from os import path
import platform


class Client(object):
    def __init__(self, base_url=None):
        os_type = platform.system()
        if os_type == 'Windows':
            import docker.tls as tls
            CERTS = path.join(path.expanduser('~'), '.docker', 'machine', 'machines', 'default')
            tls_config = tls.TLSConfig(
                client_cert=(path.join(CERTS, 'cert.pem'), path.join(CERTS, 'key.pem')),
                ca_cert=path.join(CERTS, 'ca.pem'),
                verify=True
            )
            if base_url is None:
                base_url = 'https://192.168.99.100:2376'
            self.cli = Client(base_url=base_url, tls=tls_config)
        elif os_type == 'Linux':
            base_url = 'unix://var/run/docker.sock'
            self.cli = Client(base_url=base_url)
        else:
            raise RuntimeError

    def build(self, directory=None, tag=None, timeout=None):
        if directory is None:
            raise RuntimeError("the directory of Dockerfile cannot be empty")
        elif not path.exists(directory):
            raise RuntimeError("the given directory does not exist!")
        else:
            output = self.cli.build(path=directory, rm=True, pull=True, tag=tag, timeout=timeout)
            return output
        return None

    def version(self):
        return self.cli.version()
