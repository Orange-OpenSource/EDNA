#   Copyright 2021 Orange
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

config_attack:
  salt.runner:
    - name: pyJunos.confAttacker
    - ip: {{ pillar['ip'] }}
    - mask: {{ pillar['mask'] }}
    - next_hop: {{ pillar['next_hop'] }}

config_notification:
  salt.runner:
    - name: pyJunos.modifyHealer
    - ip: {{ pillar['ip'] }}
    - mask: {{ pillar['mask'] }}