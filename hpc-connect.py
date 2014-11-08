#!/usr/bin/python3
import string
import sys, os, re
from paramiko import SSHClient, SSHConfig, AutoAddPolicy
from threading import Thread, Event

# for debuging
import time


# connect to host
def connect_to_host(ssh_login):
    ssh_client = SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(AutoAddPolicy())
    ssh_client.connect(ssh_login['hostname'], username=ssh_login['user'])

    return ssh_client


# read ssh config of user
def read_ssh_config(hostname):
    config_file = os.path.join(os.getenv('HOME'), '.ssh/config')
    config = SSHConfig()
    config.parse(open(config_file, 'r'))
    o = config.lookup(hostname)
    if len(o.keys()) < 2:
        print("wrong")
        return None
    return o


# exec command batch system
def exec_command(client, command) -> string:
    ssh_in, ssh_out, ssh_err = client.exec_command(command)
    if not ssh_err:
        print('Command execution on host failed\n')
    return ""


def get_job(client, node_count, process_count) -> SSHClient:
    submit_cmd = "salloc -N {0} -n {1} bash\n".format(node_count, process_count)
    channel = client.invoke_shell()
    channel.setblocking(1)
    channel.send(submit_cmd)
    buf = ''
    while not "bash-4.1$" in buf:
        buf += str(channel.recv(9999))
        time.sleep(10/1000000.0)

    while not channel.send_ready():
        time.sleep(10/1000000.0)

    host_cmd = "srun hostname\n"
    channel.send(host_cmd)


    buf = ""
    while not "bash-4.1$" in buf:
        buf += str(channel.recv(9999))
        if "bash-4.1$" in buf:
            break

    # b'srun hostname\r\n'b'taurusi1121\r\ntaurusi1121\r\n'b'bash-4.1$ '
    return re.findall("taurusi[0-9]{4}", buf)


#is better to give the thread the full initialized ssh client
def run_logger(hostname, nodename, event):
    config = read_ssh_config(hostname)
    client = connect_to_host(ssh_config)
    ssh_in, ssh_out, ssh_err = client.exec_command("hostname")
    #channel = client.invoke_shell()
    #channel.send("ssh {0} \'module load gpi2/1.1.0\'".format(nodename))
    #channel.send("hostname")
    buf = ssh_out.read()
    #print("connect to {}".format(nodename))
    while not event.is_set():
        print("hallo {0}".format(buf))
        time.sleep(1)
        #buf += str(channel.recv(9999))
        #time.sleep(10/1000000.0)
    #print(buf)
    #print("Good Bye")
    client.close()

host = "taurus"
ssh_config = read_ssh_config(host)
logger_client = connect_to_host(ssh_config)
hpc_hosts = get_job(logger_client, 1, 1)
print("Got Job")
#cmd = 'echo "' + '\n'.join(str(i) for i in hpc_hosts) + '" > ~/machinefile'
#logger_client.exec_command(cmd)
#logger_client.exec_command("module load gpi2/1.1.0")

stop_event = Event()
logger_thread = Thread(target=run_logger, args=(host, hpc_hosts[0], stop_event))
#print(get_worker_nodes(logger_client))
print("Start logger thread")
logger_thread.start()

time.sleep(10)
print("Kill logger thread")
stop_event.set()
logger_client.close()
#ssh_in, ssh_out, ssh_err = logger_client.exec_command("bjobs")
#print(ssh_out.read())
#channel = logger_client.invoke_shell()
#buf = ''
#while not 'cherold@atlas' in buf:
#    buf += str(channel.recv(9999))

#print(buf)

#channel.send('bjobs')

#ssh_in, ssh_out, ssh_err = exec_command(logger_client, "id")
#print(ssh_out.read())
#ssh_in, ssh_out, ssh_err = exec_command(exec_client, cmd)
#print(ssh_out.read())
#exec_client.close()

