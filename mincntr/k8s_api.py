# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import contextlib
import logging

from k8sclient.client import api_client
from k8sclient.client.apis import apiv_api
from k8sclient.tests import base

import api

LOG = logging.getLogger(__name__)


class KubernetesAPI(api.APIBase):
    def __init__(self):
        pass

    _api = None
    _client = None

    @contextlib.contextmanager
    def k8s_for_container(self):
        if self._api is None:
            self._client = api_client.ApiClient('http://127.0.0.1:8080/')
            self._api = apiv_api.ApivApi(self._client)
        yield self._api

    def container_create(self, container):
        pass

    def container_delete(self, container_uuid):
        pass

    def container_show(self, container_uuid):
        pass

    def container_reboot(self, container_uuid):
        pass

    def container_stop(self, container_uuid):
        pass

    def container_start(self, container_uuid):
        pass

    def container_pause(self, container_uuid):
        pass

    def container_unpause(self, container_uuid):
        pass

    def container_logs(self, container_uuid):
        LOG.debug("container_logs %s", container_uuid)
        with self.k8s_for_container() as api:
            response = api.read_namespaced_pod_log(
                'default', container_uuid)
            LOG.debug("container_logs %r", self._client.last_response.data)
            return {'output': self._client.last_response.data}

    def container_exec(self, container_uuid, command):
        pass
