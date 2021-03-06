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

import api as mincntr_api

LOG = logging.getLogger(__name__)


class KubernetesAPI(mincntr_api.APIBase):
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

    def list(self):
        with self.k8s_for_container() as api:
            return [mincntr_api.Container(item.metadata.uid,
                                          item.metadata.name)
                    for item in api.list_pod().items]

    def create(self, name, image, **kwargs):
        pod_manifest = {'apiVersion': 'v1',
                        'kind': 'Pod',
                        'metadata': {'color': 'blue',
                                     'name': name},
                        'spec': {'containers': [{'image': image,
                                                 'name': name}]}}

        with self.k8s_for_container() as api:
            return api.create_namespaced_pod(body=pod_manifest,
                                             namespace='default')

    def start(self, container_uuid):
        pass

    def stop(self, container_uuid):
        pass

    def restart(self, container_uuid):
        pass

    def pause(self, container_uuid):
        pass

    def unpause(self, container_uuid):
        pass

    def delete(self, container_uuid):
        pass

    def inspect(self, container_uuid):
        pass

    def logs(self, container_uuid):
        with self.k8s_for_container() as api:
            response = api.read_namespaced_pod_log(
                'default', container_uuid)
            return {'output': self._client.last_response.data}

    def execute(self, container_uuid, command):
        with self.k8s_for_container() as api:
            response = api.connect_get_namespaced_pod_exec(
                'default', container_uuid, command=command)
            return {'output': self._client.last_response.data}
