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

import collections

import abc
import six

Container = collections.namedtuple('Container', ['uuid', 'name'])

@six.add_metaclass(abc.ABCMeta)
class APIBase(object):
    @abc.abstractmethod
    def list(self):
        pass

    @abc.abstractmethod
    def create(self, name, image, **kwargs):
        pass

    @abc.abstractmethod
    def start(self, container_uuid):
        pass

    @abc.abstractmethod
    def stop(self, container_uuid):
        pass

    @abc.abstractmethod
    def restart(self, container_uuid):
        pass

    @abc.abstractmethod
    def pause(self, container_uuid):
        pass

    @abc.abstractmethod
    def unpause(self, container_uuid):
        pass

    @abc.abstractmethod
    def delete(self, container_uuid):
        pass

    @abc.abstractmethod
    def inspect(self, container_uuid):
        pass

    @abc.abstractmethod
    def logs(self, container_uuid):
        pass

    @abc.abstractmethod
    def execute(self, container_uuid, command):
        pass