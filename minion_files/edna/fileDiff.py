"""
   Copyright 2021 Orange

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import pyinotify, subprocess, salt.client
str1 = ""
cont = 0
path_attacker = './network_event'
path_healer = './response_action'


def sendAttackEvent(ip, mask, next_hop):
    caller = salt.client.Caller('/etc/salt/minion')
    caller.sminion.functions['event.send'](
        'salt/beacon/minion/inotify//attacker',
        {
        "change": "IN_MODIFY",
        "id": "minion",
        "path": path_attacker,
        "ip": ip,
        "mask": mask,
        "next_hop": next_hop
        }
    )

def sendHealingEvent(ip, mask):
    caller = salt.client.Caller('/etc/salt/minion')
    caller.sminion.functions['event.send'](
        'salt/beacon/minion/inotify//healer',
        {
        "change": "IN_MODIFY",
        "id": "minion",
        "path": path_healer,
        "ip": ip,
        "mask": mask
        }
    )

def onAttackerChange(ev):
    fo = open(path_attacker, "r")
    str1 = fo.read();
    fo.close()
    announce = str1.split("-")[0]
    ip = announce.split("/")[0]
    mask = announce.split("/")[1]
    next_hop = str1.split("-")[1][:-1]
    print path_attacker
    print str1[:-1]
    print ip
    print mask
    print next_hop

    sendAttackEvent(ip, mask, next_hop)

def onHealerChange(ev):
    fo = open(path_healer, "r")
    str1 = fo.read();
    fo.close()
    ip = str1.split("/")[0]
    mask = str1.split("/")[1][:]
    print path_healer
    print str1[:]
    print ip
    print mask

    sendHealingEvent(ip, mask)

wm = pyinotify.WatchManager()
wm.add_watch('./network_events', pyinotify.IN_MODIFY, onAttackerChange)
wm.add_watch('./response_action', pyinotify.IN_MODIFY, onHealerChange)
notifier = pyinotify.Notifier(wm)
notifier.loop()
