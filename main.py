__author__ = 'Christian Herold'

from ssh_connector import SshConnector


if __name__ == "__main__":
    ssh_connector = SshConnector("taurus", '/home/cherold')
    output = ssh_connector.execute_in_session('module load bullxmpi')
    print output
    ssh_connector.print_log()
