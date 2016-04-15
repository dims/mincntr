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

import abc
import six


@six.add_metaclass(abc.ABCMeta)
class APIBase(object):
    def __init__(self):
        pass

    @abc.abstractmethod
    def container_create(self, container):
        pass

    @abc.abstractmethod
    def container_delete(self, container_uuid):
        pass

    @abc.abstractmethod
    def container_show(self, container_uuid):
        pass

    @abc.abstractmethod
    def container_reboot(self, container_uuid):
        pass

    @abc.abstractmethod
    def container_stop(self, container_uuid):
        pass

    @abc.abstractmethod
    def container_start(self, container_uuid):
        pass

    @abc.abstractmethod
    def container_pause(self, container_uuid):
        pass

    @abc.abstractmethod
    def container_unpause(self, container_uuid):
        pass

    @abc.abstractmethod
    def container_logs(self, container_uuid):
        pass

    @abc.abstractmethod
    def container_exec(self, container_uuid, command):
        pass
