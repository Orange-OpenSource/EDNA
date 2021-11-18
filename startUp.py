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

import sys, subprocess

version = 2.3

header_compose = "\
version: '2.1'\n\n\
services:\n"

header_top = "base:\n"

header_bottom = "networks:\n\
      net-a:\n\
      net-2:\n\
      net-3:\n\n"

master_compose = '\
  salt-master:\n\
    image: elkinaguas/salt-master:v'+str(version)+'\n\
    hostname: salt-master\n\
    container_name: salt-master\n\
    environment:\n\
      - LOG_LEVEL=debug\n\
      - LOG_LEVEL_LOGFILE=debug\n\
    volumes:\n\
      - ./master_files/srv/:/etc/salt/\n\
      - ./master_files/:/root/\n\
    networks:\n\
      net-2:\n\
      net-3:\n\n'

minion_compose = '\
  salt-minion:\n\
    image: elkinaguas/salt-minion:v'+str(version)+'\n\
    hostname: minion\n\
    container_name: salt-minion\n\
    volumes:\n\
      - ./minion_files/minion:/etc/salt/minion\n\
      - ./minion_files/edna/:/root/\n\
    environment:\n\
      - LOG_LEVEL=debug\n\
      - LOG_LEVEL_LOGFILE=info\n\
    depends_on:\n\
      - salt-master\n\
    networks:\n\
      net-3:\n\n'

body_top = "\
  proxy0:\n\
    - dummy_pillar\n"

def define_proxy(i):
    instance = 'proxy'+str(i)
    proxy_compose = '\
  salt-proxy'+str(i)+':\n\
    image: elkinaguas/salt-proxy:v'+str(version)+'\n\
    hostname: '+str(instance)+'\n\
    container_name: salt-proxy-'+str(i)+'\n\
    volumes:\n\
      - ./proxy_files/proxy:/etc/salt/proxy\n\
      - ./proxy_files/edna/:/root/\n\
    environment:\n\
      - LOG_LEVEL=debug\n\
      - PROXYID='+str(instance)+'\n\
      - LOG_LEVEL_LOGFILE=info\n\
    depends_on:\n\
      - salt-master\n\
    networks:\n\
      net-a:\n\
      net-2:\n\n'

    return proxy_compose


def define_body_top(i):
    instance = 'proxy'+str(i)
    body_top = "  "+str(instance)+':\n    - '+str(instance)+'\n'

    return body_top


def file_builder(proxies):
    with open('./docker-compose.yml', 'w') as f:
        f.write(header_compose)
        f.write(master_compose)
        f.write(minion_compose)
        for i in range(int(proxies)):
            f.write(define_proxy(i))
        f.write(header_bottom)

    with open('./master_files/srv/pillar/top.sls', 'w') as f:
        f.write(header_top)
        for i in range(int(proxies)):
            f.write(define_body_top(i))


file_builder(sys.argv[1])
subprocess.call(['docker-compose', 'up', '-d'])
