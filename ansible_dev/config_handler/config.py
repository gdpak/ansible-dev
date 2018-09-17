###############################################################
# Utils to handle config file
# Author: Deepak Agrawal
###############################################################

import configparser
import os
import copy
import fnmatch
import shutil

class ConfigHandler(object):
    def __init__(self, path=None):
        if path:
            self._path = path
        else:
            # Space for temp store
            home_dir = os.path.expanduser("~")
            self._path = os.path.join(home_dir, '.ansible_dev.d/')
        self._config_files = []
        self.create_editable_config_files()

    def create_editable_config_files(self):
        try:
            path = self._path
            if not os.path.exists(path):
                os.makedirs(path)
            self.find_files_in_current_package()
            for files in self._config_files:
                if not os.path.exists(os.path.join(path, os.path.basename(files))):
                    shutil.copy(files, path)
            # Update Config files on this.object to writable files location
            filenames = []
            for files in self._config_files:
                filenames.append(os.path.basename(files))
            self._config_files = []
    
            for files in filenames:
                self._config_files.append(os.path.join(self._path, files))
        except (OSError, IOError) as e:
            print ('creating config file at user editable.Excepion received : %s' % e)

    def load_config_from_path(self, file_path):
        config_file_abspath = os.path.abspath(file_path)
        if not os.path.exists(config_file_abspath):
            raise ValueError("cfg file not found at: %s" % config_file_abspath)
        config_parser = configparser.ConfigParser()
        config_parser.read(config_file_abspath)
        return config_parser

    def find_files_in_current_package(self):
        config_file_pattern = '*.cfg'
        for root , dirs ,files in os.walk(os.path.dirname(__file__)):
            for name in files:
                if fnmatch.fnmatch(name, config_file_pattern):
                   self._config_files.append(os.path.join(root, name))

    def update_config(self, filename_path, new_file_loc=None, **kwargs):
        old_config = self.load_config_from_path(filename_path)
        old_sections = old_config.sections()

        for section in kwargs:
            if section in old_sections:
                for key in kwargs[section]:
                   old_config[section][key] = kwargs[section][key]
            else:
                old_config[section] = kwargs[section]
        
        try:
             with open(filename_path, 'w') as f:
                 old_config.write(f)
             if new_file_loc is not None:
                 shutil.copy(filename_path, new_file_loc)
        except (OSError, IOError) as e:
            print ("Unable to modify cfg file : %s" % filename_path)

    def update_dev_ansible_cfg(self, **kwargs):
        for file_path in self._config_files:
            filename = os.path.basename(file_path)
            if fnmatch.fnmatch(filename, 'ansible-dev.cfg'):
                self.update_config(file_path, **kwargs)

    def update_ansible_cfg(self, new_file_path=None, **kwargs):
        for file_path in self._config_files:
            filename = os.path.basename(file_path)
            if fnmatch.fnmatch(filename, 'ansible.cfg'):
                self.update_config(file_path, new_file_path, **kwargs)

    def get_value(self, filename, arg_section=None, key=None):
        for file_path in self._config_files:
            filen = os.path.basename(file_path)
            if fnmatch.fnmatch(filen, filename):
                c_parser = self.load_config_from_path(file_path)
                sections = c_parser.sections()
                if arg_section is None:
                    return sections
                for section in sections:
                    if arg_section == section:
                        if key is None:
                            return c_parser[section]
                        else:
                            return c_parser[section].get(key)
        return None

    def get_path(self):
        return self._path

if __name__ == "__main__":
    an_config = ConfigHandler()
    kwargs = dict(
        defaults=dict(
            roles_path='/macos/net_role/dev/roles',
            ),
        )
    #an_config.update_config(**kwargs)
    rc = an_config.find_files_in_current_package()
    print (rc)
