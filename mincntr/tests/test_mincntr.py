# -*- coding: utf-8 -*-

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

"""
test_mincntr
----------------------------------

Tests for `mincntr` module.
"""

from mincntr import k8s_api
from mincntr import docker_api
from mincntr.tests import base


class TestMincntr(base.TestCase):

    def test_docker_api(self):
        api = docker_api.DockerAPI()
        print(api.list())

    def test_k8s_api(self):
        api = k8s_api.KubernetesAPI()
        print(api.list())