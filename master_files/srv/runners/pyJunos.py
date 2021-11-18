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

from napalm_base import get_network_driver
import napalm_yang, salt.client, ipaddress
import xml.etree.ElementTree as et


import json

candidate = napalm_yang.base.Root()
candidate.add_model(napalm_yang.models.openconfig_network_instance)

running = napalm_yang.base.Root()
running.add_model(napalm_yang.models.openconfig_network_instance)

def use_real_devices():
    caller = salt.client.LocalClient()
    #user = caller.cmd('junos', 'pillar.get', ['proxy:username'])['junos']
    #password = caller.cmd('junos', 'pillar.get', ['proxy:passwd'])['junos']
    #optArgs = caller.cmd('junos', 'pillar.get', ['proxy:optional_args'])['junos']

    junos_attackedConf = {
        'hostname': '192.168.7.2',
        'username': 'root',
        'password': 'Juniper'
    }

    junos_attackerConf = {
        'hostname': '192.168.8.2',
        'username': 'root',
        'password': 'Juniper'
    }

    junos = get_network_driver("junos")
    junos_attacker = junos(**junos_attackerConf)
    junos_attacked = junos(**junos_attackedConf)

    return junos_attacker, junos_attacked

def pretty_print(dictionary):
    print(json.dumps(dictionary, sort_keys=True, indent=4))

junos_attacker, junos_attacked= use_real_devices()

#__________________________________________________________________________________
'''
As there is a  bug in the napalm-yang project that does not allow the correct manipulation of the ``next-hop`` field in the network instance model for Junos routers, it was necessary to manually add this fields to the configuration before applying it to the device.
'''
def bug2Attack(nextHopIP):
    config2 = candidate.translate_config(profile=junos_attacker.profile, merge=running)
    root = et.fromstring(config2)
    for i in root.iter('route'):
        next_hop = et.Element("next-hop")
        next_hop.text = nextHopIP
        i.append(next_hop)

    return et.tostring(root)

'''
As there is a  bug in the napalm-yang project that does not allow the correct manipulation of the ``next-hop`` field in the network instance model for Junos routers, it was necessary to manually add this fields to the configuration before applying it to the device.
'''
def bug2Heal():
    config2 = candidate.translate_config(profile=junos_attacked.profile, merge=running)
    root = et.fromstring(config2)
    for i in root.iter('route'):
        next_hop = et.Element("next-hop")
        next_hop.text = i[0].text[:-3]
        i.append(next_hop)

    return et.tostring(root)

'''
This method configures the attack on the attacker's device.
'''
def confAttacker(ip, mask, next_hop):
    with junos_attacker as r3:
        candidate.parse_config(device=r3)
        pretty_print(candidate.get(filter=True))
        
        '''
        This section is in charge of getting the subnets of the prefix that has been hijacked.
        and add it to the candidate configuration.
        '''
        prefix = unicode(str(ip)+'/'+str(mask-1))
        numIPs = len(list(ipaddress.ip_network(prefix).subnets()))
        IPs = list(ipaddress.ip_network(prefix).subnets())
        for i in range(numIPs):
            candidate.network_instances.network_instance["global"].protocols.protocol["static static"].static_routes.static.add(str(IPs[i]))
        
        running.parse_config(device=r3)
        
        #print bug2(next_hop)
        r3.load_merge_candidate(config=bug2Attack(str(next_hop)))
        #print(r3.compare_config())
        #d.discard_config()
        r3.commit_config()

'''
This method configures the attack countermeasure on the affected device.
'''
def confHealer(ip, mask):
    with junos_attacked as r2:
        candidate.parse_config(device=r2)
        pretty_print(candidate.get(filter=True))

        '''
        This section is in charge of getting the subnets of the prefix that has been hijacked
        and add it to the candidate configuration.
        '''
        prefix = unicode(str(ip)+'/'+str(mask))
        numIPs = len(list(ipaddress.ip_network(prefix).subnets()))
        IPs = list(ipaddress.ip_network(prefix).subnets())
        for i in range(numIPs):
            candidate.network_instances.network_instance["global"].protocols.protocol["static static"].static_routes.static.add(str(IPs[i]))
        
        running.parse_config(device=r2)
        
        #print bug2()

        r2.load_merge_candidate(config=bug2Heal())
        #print(r2.compare_config())
        #d.discard_config()
        r2.commit_config()

'''
This method modifies the healer file in the minion by writing in it the ip that has been hijacked
by the attacker. This can be seen as the event alerting about the attack.
'''
def modifyHealer(ip, mask):
    local = salt.client.LocalClient()
    local.cmd('minion', 'file.seek_write', ['/root/healer', str(ip)+'/'+str(mask), '0'])

