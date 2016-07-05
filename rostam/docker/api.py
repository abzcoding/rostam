# -*- coding: utf-8 -*-
'''
this module implements the required API of docker host
'''

# Import Python libs
import logging
import platform
from os import path

# Import third party libs
from docker import Client
from docker.errors import DockerException

log = logging.getLogger(__name__)


class DockerApi(object):
    '''
    API for Docker
    '''

    def __init__(self, base_url=None, timeout=None):
        '''
        decide how to connect to docker based on the system's platform

        :param base_url: string
        connection url for docker host
        :param timeout: int : 10
        timeout amount in seconds

        :raises: ``RuntimeError`` if cannot os is not windows or linux , ``DockerException`` if cannot connect to docker
        '''
        os_type = platform.system()
        if timeout is None:
            timeout = 10
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
            self.cli = Client(base_url=base_url, tls=tls_config, timeout=timeout)
        elif os_type == 'Linux':
            base_url = 'unix://var/run/docker.sock'
            self.cli = Client(base_url=base_url, timeout=timeout)
        else:
            log.error("os is nor Windows nither Linux")
            raise RuntimeError

    def build(self, directory=None, tag=None, timeout=None):
        '''
        docker build the given DockerFile

        :param directory: string
        directory that contains Dockerfile
        :param tag: string : None
        container's tag
        :param timeout: int : 10
        timeout for docker build command

        :return: output of the docker build command
        :rtype: array of strings
        '''
        if directory is None:
            log.error("the directory of Dockerfile cannot be empty")
            return None
        elif not path.exists(directory):
            log.error("the given directory does not exist!")
            return None
        else:
            output = self.cli.build(path=directory, rm=True, pull=True, tag=tag, timeout=timeout)
            build_output = [line for line in output]
            return build_output

    def version(self):
        '''
        docker api version

        :return: version of the docker host's api
        :rtype: string
        '''
        return self.cli.version()
