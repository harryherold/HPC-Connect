__author__ = 'Christian Herold'

#!/usr/bin/python2
import time
import sys
import os
import getpass
import yaml
from paramiko import SSHClient, SSHConfig, AutoAddPolicy


class SshConnector:
    host = ""
    user = ""
    ssh_config = None
    ssh_client = None
    batch_sys = None
    ssh_log = ""
    prompt = ""

    def __init__(self, host, home_path, user=None):
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
        self.detect_prompt(home_path)
        print("Deteced prompt:")
        print(self.prompt)

    # connect to host with config
    def connect_with_config(self):
        self.ssh_client = SSHClient()
        self.ssh_client.load_system_host_keys()
        self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        self.ssh_client.connect(self.ssh_config['hostname'],
                                username=self.ssh_config['user'])

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

    # execute command on the host, blocking semantic
    def execute(self, cmd):
        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh_client.exec_command(cmd)
        self.ssh_log += str(ssh_stderr.read())
        return str(ssh_stdout.read())

    # implement own function to check prompt in reverse order
    def execute_in_session(self, cmd):
        channel = self.ssh_client.invoke_shell()
        while not channel.send_ready():
            time.sleep(0.00001)
        channel.send(cmd + '\n')
        recv_buffer = " "
        while not recv_buffer.endswith(self.prompt + ' '):
            rsp = channel.recv(1024)
            recv_buffer += rsp
        pattern = self.prompt + ' ' + cmd
        begin = recv_buffer.find(pattern) + len(pattern) + 2
        end = len(recv_buffer) - len(self.prompt + ' ')
        return recv_buffer[begin:end]

    def detect_prompt(self, home_path):
        channel = self.ssh_client.invoke_shell()
        while not channel.send_ready():
            time.sleep(0.00001)
        channel.send('echo $HOME\n')
        recv_buffer = ''
        while not home_path in recv_buffer:
            resp = channel.recv(1024)
            recv_buffer += resp
        idx = recv_buffer.rfind('echo')
        prompt = ''
        for i in range(idx - 2, -1, -1):
            if(recv_buffer[i] == ' '):
                break
            elif(recv_buffer[i] != '\r' and recv_buffer[i] != '\n'
                                   and recv_buffer[i] != '\t'):
                prompt += recv_buffer[i]
        self.prompt = prompt[::-1]

    def print_log(self):
        print("\n\nSSH LOG")
        print("========")
        print(self.ssh_log)

    def print_modules(self):
        print(self.exec_command("module av"))

    def load_modules(self, modules):
        return self.exec_command("module load {}".format(modules))

    def submit_job(self, path_to_exec, modules, runtime, options, sys_name):
        conf = self.batch_sys.get_batchsystem_config(sys_name)
        self.load_modules(modules)
        cmd = "{0} {1} {2} {3}".format(conf['shell_command'], options,
                                runtime, path_to_exec)
        self.exec_command(cmd)


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

    # returns the whole config of a given batchsystem
    def get_batchsystem_config(self, sys_name):
        return self.batchsystem_config[sys_name]

    # print the config of the supported batch systems
    def print_system(self):
        for system in self.batchsystem_config:
            print("{0} :".format(system))
            for conf in self.batchsystem_config[system]:
                print("{:>20}:  {}".format(conf,
                       self.batchsystem_config[system][conf]))


ssh_connector = SshConnector("taurus", '/home/cherold')
output = ssh_connector.execute_in_session('module load bullxmpi')
print output
#ssh_connector.print_log()
