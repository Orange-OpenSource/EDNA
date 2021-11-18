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

import sys, subprocess, os

version = sys.argv[1]

if os.path.exists("./master_files/.bash_history"):
    subprocess.call(["sudo", "rm", "-r", "./master_files/.bash_history"])

if os.path.exists("./master_files/srv/pki/"):
    subprocess.call(["sudo", "rm", "-r", "./master_files/srv/pki"])

if os.path.exists("./proxy_files/edna/.bash_history"):
    subprocess.call(["sudo", "rm", "-r", "./proxy_files/edna/.bash_history"])




subprocess.call(["mv", "Dockerfile-master", "Dockerfile"])
subprocess.call(["xterm", "-e", "docker build -t elkinaguas/salt-master:v"+str(version)+" ."])
subprocess.call(["mv", "Dockerfile", "Dockerfile-master"])

subprocess.call(["mv", "Dockerfile-minion", "Dockerfile"])
subprocess.call(["xterm", "-e", "docker build -t elkinaguas/salt-minion:v"+str(version)+" ."])
subprocess.call(["mv", "Dockerfile", "Dockerfile-minion"])

subprocess.call(["mv", "Dockerfile-proxy", "Dockerfile"])
subprocess.call(["xterm", "-e", "docker build -t elkinaguas/salt-proxy:v"+str(version)+" ."])
subprocess.call(["mv", "Dockerfile", "Dockerfile-proxy"])

