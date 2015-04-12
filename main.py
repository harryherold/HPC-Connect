__author__ = 'Christian Herold'

from ssh_connector import SshConnector


if __name__ == "__main__":
    mpi_app = "/home/cherold/mpi-example/hello_mpi"
    ssh_connector = SshConnector("taurus", '/home/cherold', 'slurm')
    ssh_connector.submit_interactive_job(mpi_app, 2, modules="bullxmpi")
    ssh_connector.print_log()
