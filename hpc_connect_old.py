__author__ = 'harry'

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
    client = connect_with_config(ssh_config)
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

#parser = argparse.ArgumentParser()
#parser.add_argument("host", help="host address")
#parser.add_argument("user", help="username")

#args = parser.parse_args()

#ssh_client = connect(args.host, args.user)

#ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command("ls -l")
#print(ssh_stdout.read())

#host = "taurus"
#ssh_config = read_ssh_config(host)
#logger_client = connect_with_config(ssh_config)
#hpc_hosts = get_job(logger_client, 1, 1)
#print("Got Job")
#stop_event = Event()
#logger_thread = Thread(target=run_logger, args=(host, hpc_hosts[0], stop_event))
#print("Start logger thread")
#logger_thread.start()

#time.sleep(10)
#print("Kill logger thread")
#stop_event.set()
#logger_client.close()