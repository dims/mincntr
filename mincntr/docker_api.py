# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import contextlib
import functools
import logging
import os
import uuid

from distutils.version import StrictVersion
import six

import docker
from docker import client
from docker import errors
from docker import tls

import api

LOG = logging.getLogger(__name__)


def compare_version(v1, v2):
    """Compare docker versions

    >>> v1 = '1.9'
    >>> v2 = '1.10'
    >>> compare_version(v1, v2)
    1
    >>> compare_version(v2, v1)
    -1
    >>> compare_version(v2, v2)
    0
    """
    s1 = StrictVersion(v1)
    s2 = StrictVersion(v2)
    if s1 == s2:
        return 0
    elif s1 > s2:
        return -1
    else:
        return 1


def is_docker_library_version_atleast(version):
    if compare_version(docker.version, version) <= 0:
        return True
    return False


def is_docker_api_version_atleast(docker, version):
    if compare_version(docker.version()['ApiVersion'], version) <= 0:
        return True
    return False


def parse_docker_image(image):
    image_parts = image.split(':', 1)

    image_repo = image_parts[0]
    image_tag = None

    if len(image_parts) > 1:
        image_tag = image_parts[1]

    return image_repo, image_tag


class DockerHTTPClient(client.Client):
    def __init__(self, url='unix://var/run/docker.sock',
                 ver='1.20',
                 timeout=60,
                 ca_cert=None,
                 client_key=None,
                 client_cert=None):

        if ca_cert and client_key and client_cert:
            ssl_config = tls.TLSConfig(client_cert=(client_cert, client_key),
                                       verify=ca_cert,
                                       assert_hostname=False)
        else:
            ssl_config = False

        super(DockerHTTPClient, self).__init__(base_url=url,
                                               version=ver,
                                               timeout=timeout,
                                               tls=ssl_config)

    def list_instances(self, inspect=False):
        res = []
        for container in self.containers(all=True):
            info = self.inspect_container(container['Id'])
            if not info:
                continue
            if inspect:
                res.append(info)
            else:
                res.append(info['Config'].get('Hostname'))
        return res


def wrap_container_exception(f):
    def wrapped(self, *args, **kwargs):
        try:
            return f(self, *args, **kwargs)
        except Exception as e:
            container_uuid = None
            if 'container_uuid' in kwargs:
                container_uuid = kwargs.get('container_uuid')
            elif 'container' in kwargs:
                container_uuid = kwargs.get('container').uuid

            LOG.exception("Error while connect to docker "
                          "container %s", container_uuid)
            raise Exception("Docker internal Error: %s" % str(e))

    return functools.wraps(f)(wrapped)


class DockerAPI(api.APIBase):
    def __init__(self):
        pass

    _client = None

    @contextlib.contextmanager
    def docker_for_container(self):
        if self._client is None:
            self._client = DockerHTTPClient(
                url=os.getenv('DOCKER_HOST', 'unix://var/run/docker.sock'))
        yield self._client

    @staticmethod
    def _find_container_by_name(docker, name):
        try:
            for info in docker.list_instances(inspect=True):
                if info.get('Name') == name:
                    return info
        except errors.APIError as e:
            if e.response.status_code != 404:
                raise
        return {}

    def _encode_utf8(self, value):
        if six.PY2 and not isinstance(value, unicode):
            value = unicode(value)
        return value.encode('utf-8')

    # Container operations

    @wrap_container_exception
    def list(self):
        with self.docker_for_container() as docker:
            return docker.list_instances()

    @wrap_container_exception
    def create(self, name, image, **kwargs):
        with self.docker_for_container() as docker:
            container_uuid = kwargs.get(uuid)
            LOG.debug('Creating container with image %s name %s', image, name)
            try:
                image_repo, image_tag = parse_docker_image(image)
                docker.pull(image_repo, tag=image_tag)
                docker.inspect_image(self._encode_utf8(image))
                container_kwargs = {'name': name,
                                    'hostname': container_uuid,
                                    'command': kwargs.get('command'),
                                    'environment': kwargs.get('environment')}
                memory = kwargs.get('memory')
                if is_docker_api_version_atleast(docker, '1.19'):
                    if memory is not None:
                        container_kwargs['host_config'] = {'mem_limit': memory}
                else:
                    container_kwargs['mem_limit'] = memory

                docker.create_container(image, **container_kwargs)
                return True
            except errors.APIError:
                return False

    @wrap_container_exception
    def delete(self, container_uuid):
        LOG.debug("container_delete %s", container_uuid)
        with self.docker_for_container() as docker:
            docker_id = self._find_container_by_name(docker,
                                                     container_uuid)
            if not docker_id:
                return None
            return docker.remove_container(docker_id)

    @wrap_container_exception
    def inspect(self, container_uuid):
        LOG.debug("container_show %s", container_uuid)
        with self.docker_for_container() as docker:
            # container = objects.Container.get_by_uuid(
            #  container_uuid)
            try:
                docker_id = self._find_container_by_name(docker,
                                                         container_uuid)
                if not docker_id:
                    LOG.exception("Can not find docker instance with %s,"
                                  "set it to Error status",
                                  container_uuid)
                    # container.status = 'ERROR'
                    # container.save()
                    # return container
                result = docker.inspect_container(docker_id)
                status = result.get('State')
                # if status:
                #     if status.get('Error') is True:
                #         container.status = 'ERROR'
                #     elif status.get('Paused'):
                #         container.status = 'PAUSED'
                #     elif status.get('Running'):
                #         container.status = 'RUNNING'
                #     else:
                #         container.status = 'STOPPED'
                #     container.save()
                # return container
                return status
            except errors.APIError as api_error:
                error_message = str(api_error)
                if '404' in error_message:
                    # container.status = 'ERROR'
                    # container.save()
                    # return container
                    return
                raise

    @wrap_container_exception
    def _container_action(self, container_uuid, status, docker_func):
        LOG.debug("%s container %s ...", docker_func, container_uuid)
        with self.docker_for_container() as docker:
            docker_id = self._find_container_by_name(docker,
                                                     container_uuid)
            result = getattr(docker, docker_func)(docker_id)
            # container = objects.Container.get_by_uuid(
            #                                           container_uuid)
            # container.status = status
            # container.save()
            return result

    def restart(self, container_uuid):
        return self._container_action(container_uuid,
                                      'RUNNING',
                                      'restart')

    def stop(self, container_uuid):
        return self._container_action(container_uuid,
                                      'STOPPED', 'stop')

    def start(self, container_uuid):
        return self._container_action(container_uuid,
                                      'RUNNING', 'start')

    def pause(self, container_uuid):
        return self._container_action(container_uuid,
                                      'PAUSED', 'pause')

    def unpause(self, container_uuid):
        return self._container_action(container_uuid,
                                      'RUNNING',
                                      'unpause')

    @wrap_container_exception
    def logs(self, container_uuid):
        LOG.debug("container_logs %s", container_uuid)
        with self.docker_for_container() as docker:
            docker_id = self._find_container_by_name(docker,
                                                     container_uuid)
            return {'output': docker.logs(docker_id)}

    @wrap_container_exception
    def execute(self, container_uuid, command):
        LOG.debug("container_exec %s command %s",
                  container_uuid, command)
        with self.docker_for_container() as docker:
            docker_id = self._find_container_by_name(docker,
                                                     container_uuid)
            if is_docker_library_version_atleast('1.2.0'):
                create_res = docker.exec_create(docker_id, command, True,
                                                True, False)
                exec_output = docker.exec_start(create_res, False, False,
                                                False)
            else:
                exec_output = docker.execute(docker_id, command)
            return {'output': exec_output}
