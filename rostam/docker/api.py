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
            log.error(tag)
            output = self.cli.build(path=directory, rm=True, pull=False, tag=tag, timeout=timeout)
            build_output = [line for line in output]
            return build_output

    def push(self, name, tag="latest", stream=True, insecure_registry=False):
        '''
        push to remote docker registry

        :param name: string
        remote_registry+/+remote_name+:+container_tag
        :param stream: bool : True
        Stream the output as a blocking generator
        :param insecure_registry: bool : False
        Use http:// to connect to the registry

        :return: output of the docker push command
        :rtype: array of strings
        '''
        log.error(name + '---' + tag)
        output = self.cli.push(repository=str(name), tag=tag, stream=stream, insecure_registry=insecure_registry)
        push_output = [line for line in output]
        log.info('pushed {0} to remote registry!'.format(name))
        return push_output

    def tag(self, image, repository, tag="latest"):
        '''
        tag the required images

        :param image: string
        The image to tag
        :param repository: string
        The repository to set for the tag
        :param tag: string : 'latest'
        The tag name

        :return: was the tagging successfull?
        :rtype: bool
        '''
        log.error(image + '---' + repository + '---' + tag)
        result = self.cli.tag(image, repository, tag)
        return result

    def login(self, username, password, registry):
        try:
            self.cli.login(username=username, password=password, registry=registry)
            log.debug('successfully logged in {0} with {1}'.format(registry, username))
            return True
        except Exception:
            log.error('cannot login to {0} using {1} user'.format(registry, username))
            return False

    def version(self):
        '''
        docker api version

        :return: version of the docker host's api
        :rtype: string
        '''
        return self.cli.version()
