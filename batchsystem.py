# -*- coding: utf-8 -*-
__author__ = 'Christian Herold'


import sys
import yaml


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