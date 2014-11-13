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
    batch_sys = None
    ssh_log = ""

    def __init__(self, host, user=None):
        self.batch_sys = Batchsystem()
        self.batch_sys.read_config()
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

    def print_log(self):
        print("SSH LOG")
        print("=======")
        print(self.ssh_log)

    def print_modules(self):
        print(self.exec_command("module av"))


class Batchsystem:
    batchsystem_config = None
    config_filename = "batchconf.yaml"
    config_templ = "templconf.yaml"

    # create a new config based on a template
    def create_config(self):
        stream_templ = open(self.config_templ, 'r')
        templ = yaml.load(stream_templ)
        stream_templ.close()

        for entry in templ.keys():
            print("Please insert the command for {0}".format(entry))
            text = sys.stdin.readline()
            templ[entry] = text.strip()

        print("Whats the name of the system ?")
        text = sys.stdin.readline()
        temp_dict = {text.strip(): templ}
        stream = open(self.config_filename, 'a')
        yaml.dump(temp_dict, stream)
        stream.close()
        print("Config saved")

    # read the config from the yaml file
    def read_config(self):
        stream = open(self.config_filename, 'r')
        self.batchsystem_config = yaml.load(stream)
        stream.close()

    # return a list of supported batch systems
    def get_supported_systems(self):
        return [s for s in self.batchsystem_config]

    # print the config of the supported batch systems
    def print_system(self,):
        for system in self.batchsystem_config:
            print("{0} :".format(system))
            for conf in self.batchsystem_config[system]:
                print("{:>20}:  {}".format(conf, self.batchsystem_config[system][conf]))


# parser = argparse.ArgumentParser()
# parser.add_argument("host", help="host address")
# parser.add_argument("user", help="username")
# args = parser.parse_args()
#
# ssh_connector = SshConnector(args.host, args.user)
# print(ssh_connector.exec_command("ls -l"))

b = Batchsystem()
b.read_config()
b.print_system()

# b.create_config()

