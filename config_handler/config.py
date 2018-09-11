###############################################################
# Utils to handle config file
# Author: Deepak Agrawal
###############################################################

import configparser
import os
import copy

class Config(object):
    def __init__(self, file_path):
        config_file_abspath = os.path.abspath(file_path)
        if not os.path.exists(config_file_abspath):
            raise ValueError("cfg file not found at: %s" % config_file_abspath)
        config_parser = configparser.ConfigParser()
        config_parser.read(config_file_abspath)
        self._config = config_parser

    def update_config(self, **kwargs):
        old_config = self._config
        #new_config = copy.deepcopy(old_config)
        for key in kwargs:
            if key in old_config:
                print (key)
                old_config.update(kwargs)
        #print (new_config)
        
        for k, v in old_config.items:
            print (k, v)


def add_roles_path_ansible_cfg(file_path, roles_path, tmp_op):
    config_file_abspath = os.path.abspath(file_path)
    if not os.path.exists(config_file_abspath):
        raise ValueError("ansible.cfg not found at: %s" % config_file_abspath)

    an_config = configparser.ConfigParser()
    an_config.read(config_file_abspath)
    an_config["defaults"]["roles_path"] = roles_path

    with open(tmp_op, 'w') as c:
        an_config.write(c)

if __name__ == "__main__":
    an_config = Config('./../templates/ansible.cfg')
    kwargs = dict(
        defaults=dict(
            roles_path='/macos/net_role/dev/roles',
            ),
        )
    an_config.update_config(**kwargs)
