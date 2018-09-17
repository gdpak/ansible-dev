import os
import subprocess
import select
import traceback
import sys
import errno
import json

if sys.version_info[0] == 2:
   def b(s):
      return s
else:
   def b(s):
      return s.encode("latin-1")
from ansible_dev.utils.system import get_bin_path

class Action(object):
    def __init__(self, verbose=False, path=None, ansible_path='ansible', venv='.venv'):
        self._path = path
        self._verbose = verbose
        self._network_org = 'ansible-network'
        self.ansible_path = ansible_path
        self.venv = venv

    @property
    def ansible_path(self):
        return self._ansible_path

    @ansible_path.setter
    def ansible_path(self, a_path):
        if self._path:
            self._ansible_path = os.path.join(self._path, a_path)
        else:
            self._ansible_path = None

    @property
    def venv(self):
        return self._venv

    @venv.setter
    def venv(self, ve_path):
        if self._path:
            self._venv = os.path.join(self._path, ve_path)
        else:
            self._venv = None

    def _log(self, level=0, msg=None):
        if level <= self._verbose:
            if msg:
                print(msg)

    def create_directory(self, path, config_handler):
        path = os.path.abspath(path)
        self._path = path
        self.ansible_path = 'ansible'
        self._config_handler = config_handler
        if os.path.exists(path):
            self._log(level=0, msg="directory exists: %s" % path)
            return True
        try:
            os.makedirs(path)
            self._log(level=0, msg="Created directory: %s" % path)
        except OSError as e:
            if e.error != EEXIST:
                raise e
        return True

    def _read_from_pipes(self, rpipes, rfds, file_descriptor):
        data = b('')
        if file_descriptor in rfds:
            data = os.read(file_descriptor.fileno(), 9000)
            if data == b(''):
                rpipes.remove(file_descriptor)
        return data

    def run_command(self, args):
        self._log(level=1, msg="Executing cmd: %s " % args)
        try:
            kwargs = dict(
                executable=None,
                shell=False,
                stdin=None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            cmd = subprocess.Popen(args, **kwargs)
            stdout = b('')
            stderr = b('')
            rpipes = [cmd.stdout, cmd.stderr]
            while True:
                rfds, wfds, efds = select.select(rpipes, [], rpipes, 1)
                stdout += self._read_from_pipes(rpipes, rfds, cmd.stdout)
                stderr += self._read_from_pipes(rpipes, rfds, cmd.stderr)
                if (not rpipes or not rfds) and cmd.poll() is not None:
                    break
                elif not rpipes and cmd.poll() is None:
                    cmd.wait()
                    break
                self._log(level=3, msg=stdout)
                self._log(level=2, msg=stderr)

            cmd.stdout.close()
            cmd.stderr.close()
            if cmd.returncode:
                self._log(level=0, msg="cmd:%s failed. stdout: %s stderr: %s" %
                        (args, stdout, stderr))
            return (cmd.returncode, stdout)

        except (OSError, IOError) as e:
            self._log(level=0, msg="Error Executing CMD: %s Exception: %s" % (args, e))
            raise e

    def _change_root_work_directory(self):
        try:
            os.chdir(self._path)
        except (OSError, IOError) as e:
            raise e

    def _check_cmd_rc(self, rc, stdout=None):
        if rc:
            if stdout:
                # rc non-zero means some error
                raise ValueError(stdout)
            else:
                raise ValueError(str(rc))
        else:
            return (rc, stdout)

    def create_venv(self, app_name='.venv', py_version=None):
        venv_bin_path = get_bin_path('virtualenv')
        self._log(level=1, msg="Executing virtualenv from : %s" % venv_bin_path)
        venv_abspath = os.path.abspath(os.path.join(self._path, app_name))
        self._venv = venv_abspath
        if os.path.exists(venv_abspath):
           self._log(level=0, msg="venv exists : %s" % venv_abspath)
           return self._venv

        try:
            self._change_root_work_directory()
            # Find active python version
            cmd = ['python', '--version']
            rc, sys_py_ver = self.run_command(cmd)
            rc, sys_py_ver = self._check_cmd_rc(rc, sys_py_ver)
            if sys_py_ver.find(py_version) != -1:
                cmd = ['virtualenv', app_name]
            else:
                py_ver = 'python' + py_version
                cmd = ['virtualenv', '-p', py_ver, app_name]
            rc, stdout = self.run_command(cmd)
            rc, stdout = self._check_cmd_rc(rc, stdout)
            self._log(level=2, msg="run_command : rc=%d" % rc)
            self._log(level=1, msg="venv created : %s" % venv_abspath)
            return self._venv
        except Exception as e:
            self._venv = None
            if self._verbose > 0:
                traceback.print_exc()
            raise e

    def execute_command_in_venv(self, cmd):
        self._change_root_work_directory()
        venv_path = self._venv
        if venv_path is None:
            self._log(level=0, msg="venv is not yet created")
        venv_bin_path = os.path.join(venv_path, 'bin')
      
        old_env_vals = {}
        old_env_vals['PATH'] = os.environ['PATH']
        os.environ['PATH'] = "%s:%s" % (venv_bin_path, os.environ['PATH'])
        rc, stdout = self.run_command(cmd)
        rc, stdout = self._check_cmd_rc(rc, stdout)
        self._log(level=2, msg=rc)
        os.environ['PATH'] = old_env_vals['PATH']
        return rc, stdout

    def clone_git_repo(self, repo, version):
        git_path = get_bin_path('git')
        ansible_dest = self._ansible_path
        cmd = [git_path, 'clone', repo, '-b', version, ansible_dest]
        if os.path.exists(ansible_dest):
            self._log(level=0, msg="ansible repo exists : %s" % ansible_dest)
            return ansible_dest

        try:
            self._change_root_work_directory()
            rc, stdout = self.run_command(cmd)
            rc, stdout = self._check_cmd_rc(rc, stdout)
            self._log(level=2, msg="run_command : cmd=%s rc=%s" % (cmd, rc))
            self._log(level=1, msg="ansible repo created at : %s" % ansible_dest)
            return (ansible_dest)
        except Exception as e:
            self._ansible_path = None
            if self._verbose > 0:
                traceback.print_exc()
            raise e

    def install_repo_dependancies_in_venv(self, repo_path):
        if not os.path.exists(repo_path):
            self._log(level=0, msg="Repo is not yet initialized at: %s" % repo_path)
        try:
            os.chdir(repo_path)
        except (OSError, IOError) as e:
            raise e

        cmd = ['pip', 'install' , '-r', 'requirements.txt']
        try:
            rc, stdout = self.execute_command_in_venv(cmd)
            rc, stdout = self._check_cmd_rc(rc, stdout)
            self._log(level=2, msg="run_command : cmd=%s rc=%s" % (cmd, rc))
            self._log(level=1, msg="repo: %s Dependancies installed" % repo_path)
            return rc
        except Exception as e:
            if self._verbose > 0:
                traceback.print_exc()
            raise e

    def activate_ansible_in_venv(self, ansible_path):
        if not os.path.exists(ansible_path):
            self._log(level=0, msg="No ansible repo at: %s" % ansible_path)
        try:
            os.chdir(ansible_path)
        except (OSError, IOError) as e:
            raise e

        # Prerequisite to do make install of ansible. Install packaging
        cmd = ['pip', 'install', 'packaging']
        rc, stdout = self.execute_command_in_venv(cmd)
        rc, stdout = self._check_cmd_rc(rc, stdout)

        cmd = ['pip', 'install', '--editable', '.']
        try:
            rc, stdout = self.execute_command_in_venv(cmd)
            rc, stdout = self._check_cmd_rc(rc, stdout)
            self._log(level=2, msg="run_command : cmd=%s rc=%s" % (cmd, rc))
            self._log(level=0, msg="Ansible installed from :%s" % ansible_path)
            return rc
        except Exception as e:
            if self._verbose > 0:
                traceback.print_exc()
            raise e

    def print_ansible_version(self, ansible_path):
        if not os.path.exists(ansible_path):
            self._log(level=0, msg="No ansible repo at: %s" % ansible_path)
        try:
            os.chdir(ansible_path)
        except (OSError, IOError) as e:
            raise e

        cmd = ['ansible', '--version']
        try:
            rc, out = self.execute_command_in_venv(cmd)
            rc, out = self._check_cmd_rc(rc, out)
            self._log(level=2, msg="run_command : cmd=%s rc=%s" % (cmd, rc))
            return out
        except Exception as e:
            if self._verbose > 0:
                traceback.print_exc()

    def get_roles(self):
        self._roles_path = os.path.join(self._path, 'roles')
        try:
            os.makedirs(self._roles_path)
        except (OSError, IOError) as e:
            if e == errno.EEXIST:
               pass
        try:
            # update roles path in ansible cfg and copy to workspace root
            config_handler = self._config_handler
            kwargs = {}
            kwargs = dict(
                defaults=dict(
                    roles_path=self._roles_path,
                    ),
            )
            config_handler.update_ansible_cfg(self._path, **kwargs)
            # Chdir to worspace root to start downloading roles
            self._change_root_work_directory()
            workspace_section = "workspace:" + str(self._path)
            default_galaxy_roles_list = self._config_handler.get_value(
                'ansible-dev.cfg',
                'defaults',
                'galaxy_roles_list')
            default_github_roles_list = self._config_handler.get_value(
                'ansible-dev.cfg',
                'defaults',
                'git_roles_repos')
            ws_galaxy_roles_list = self._config_handler.get_value(
                'ansible-dev.cfg',
                workspace_section,
                'galaxy_roles_list')
            ws_github_roles_list = self._config_handler.get_value(
                'ansible-dev.cfg',
                workspace_section,
                'git_roles_repos')
            
            if default_galaxy_roles_list:
                default_galaxy_roles_list = \
                    list(default_galaxy_roles_list.split(','))
                print (default_galaxy_roles_list)
                for role in default_galaxy_roles_list:
                    self._log(level=1, msg="Installing galaxy role %s" % role)
                    cmd = ['ansible-galaxy', 'install', role]
                    self.execute_command_in_venv(cmd)

            if ws_galaxy_roles_list:
                ws_galaxy_roles_list = \
                    list(ws_galaxy_roles_list.split(','))
                for role in ws_galaxy_roles_list:
                    self._log(level=1, msg="Installing galaxy role %s" % role)
                    cmd = ['ansible-galaxy', 'install', role]
                    self.execute_command_in_venv(cmd)
       
            if default_github_roles_list:
                default_github_roles_list = \
                    list(default_github_roles_list.split(','))
                for role in default_github_roles_list:
                    self._log(level=1, msg="Installing github role %s" % role)
                    role_name = os.path.basename(role)
                    galaxy_simulated_role = self._network_org + '.' + role_name
                    role_path = os.path.join(self._roles_path,
                            galaxy_simulated_role)
                    cmd = ['git', 'clone', role, role_path]
                    self.execute_command_in_venv(cmd)

            if ws_github_roles_list:
                ws_github_roles_list = \
                    list(ws_github_roles_list.split(','))
                print (ws_github_roles_list)
                for role in ws_github_roles_list:
                    self._log(level=1, msg="Installing github role %s" % role)
                    role_name = os.path.basename(role)
                    galaxy_simulated_role = self._network_org + '.' + role_name
                    role_path = os.path.join(self._roles_path,
                            galaxy_simulated_role)
                    cmd = ['git', 'clone', role, role_path]
                    self.execute_command_in_venv(cmd)
        except Exception as e:
            self._log(level=0, msg="roles_get failed : %s" % e)
            if self._verbose > 0:
                traceback.print_exc()
