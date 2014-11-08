__author__ = 'harry'

#!/usr/bin/python3
import string
import sys, os, re, getpass, argparse, yaml
from paramiko import SSHClient, SSHConfig, AutoAddPolicy
from threading import Thread, Event

# for debuging
import time


class SshConnector:
    host = ""
    user = ""
    ssh_config = None
    ssh_client = None
    ssh_log = ""

    def __init__(self, host, user=None):
        if user is None:
            self.host = host
            self.read_ssh_config(host)
            self.connect_with_config()
        else:
            self.host = host
            self.user = user
            self.connect(host, user)

    # connect to host with config
    def connect_with_config(self):
        self.ssh_client = SSHClient()
        self.ssh_client.load_system_host_keys()
        self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        self.ssh_client.connect(self.ssh_config['hostname'], username=self.ssh_config['user'])

    # connect with user parameter
    def connect(self, host, user):
        password = getpass.getpass()
        self.ssh_client = SSHClient()
        self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        self.ssh_client.connect(host, username=user, password=password)

    # read ssh config of user
    def read_ssh_config(self, hostname):
        config_file = os.path.join(os.getenv('HOME'), '.ssh/config')
        config = SSHConfig()
        config.parse(open(config_file, 'r'))
        self.ssh_config = config.lookup(hostname)
        if len(self.ssh_config.keys()) < 2:
            print("Hostname no found in .ssh/config")

    # execute command on the host
    def exec_command(self, cmd):
        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh_client.exec_command(cmd)
        self.ssh_log += str(ssh_stderr.read())
        return str(ssh_stdout.read())


class Batchsystem:
    file_name = "batchconf.yaml"
    config_templ = "templconf.yaml"

    def create_config(self):
        stream_templ = open(self.config_templ, 'r')
        templ = yaml.load(stream_templ)
        stream_templ.close()

        for entry in templ.keys():
            print("Please insert the command for {0}".format(entry))
            text = sys.stdin.readline()
            templ[entry] = text.strip()

        stream = open(self.file_name, 'a')
        yaml.dump(templ, stream)
        stream.close()


parser = argparse.ArgumentParser()
parser.add_argument("host", help="host address")
parser.add_argument("user", help="username")
args = parser.parse_args()

ssh_connector = SshConnector(args.host, args.user)
print(ssh_connector.exec_command("ls -l"))

b = Batchsystem()
b.create_config()

