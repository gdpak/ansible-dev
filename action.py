import os
import subprocess
import select
import traceback
import sys
if sys.version_info[0] == 2:
   def b(s):
      return s
else:
   def b(s):
      return s.encode("latin-1")
from utils.system import get_bin_path

class Action(object):
    def __init__(self, verbose=False):
        self._path = None
        self._verbose = verbose

    @property
    def ansible_path(self):
        return self._ansible_path

    @ansible_path.setter
    def ansible_path(self, a_path):
        if self._path:
            self._ansible_path = os.path.join(self._path, a_path)
        else:
            self._ansible_path = None

    def _log(self, level=0, msg=None):
        if level <= self._verbose:
            if msg:
                print(msg)

    def create_directory(self, path):
        path = os.path.abspath(path)
        self._path = path
        self.ansible_path = 'ansible'
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
            return (cmd.returncode, stdout)

        except (OSError, IOError) as e:
            self._log(level=0, msg="Error Executing CMD: %s Exception: %s" % (args, e))
            raise e

    def _change_root_work_directory(self):
        try:
            os.chdir(self._path)
        except (OSError, IOError) as e:
            raise e

    def create_venv(self, app_name='.venv'):
        venv_bin_path = get_bin_path('virtualenv')
        self._log(level=1, msg="Executing virtualenv from : %s" % venv_bin_path)
        venv_abspath = os.path.abspath(os.path.join(self._path, app_name))
        self._venv = venv_abspath
        if os.path.exists(venv_abspath):
           self._log(level=0, msg="venv exists : %s" % venv_abspath)
           return self._venv

        try:
            self._change_root_work_directory()
            cmd = ['virtualenv', app_name]
            rc = self.run_command(cmd)
            self._log(level=2, msg="run_command : rc=%s" % rc)
            self._log(level=1, msg="venv created : %s" % venv_abspath)
            return self._venv
        except Exception as e:
            self._venv = None
            traceback.print_exc()
            raise e

    def execute_command_in_venv(self, cmd):
        venv_path = self._venv
        if venv_path is None:
            self._log(level=0, msg="venv is not yet created")
        venv_bin_path = os.path.join(venv_path, 'bin')
      
        old_env_vals = {}
        old_env_vals['PATH'] = os.environ['PATH']
        os.environ['PATH'] = "%s:%s" % (venv_bin_path, os.environ['PATH'])
        rc = self.run_command(cmd)
        self._log(level=2, msg=rc)
        os.environ['PATH'] = old_env_vals['PATH']
        return rc

    def clone_git_repo(self, repo, version):
        git_path = get_bin_path('git')
        ansible_dest = self._ansible_path
        cmd = [git_path, 'clone', repo, '-b', version, ansible_dest]
        if os.path.exists(ansible_dest):
            self._log(level=0, msg="ansible repo exists : %s" % ansible_dest)
            return ansible_dest

        try:
            self._change_root_work_directory()
            rc = self.run_command(cmd)
            self._log(level=2, msg="run_command : cmd=%s rc=%s" % (cmd, rc))
            self._log(level=1, msg="ansible repo created at : %s" % ansible_dest)
            return (ansible_dest)
        except Exception as e:
            self._ansible_path = None
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
            rc = self.execute_command_in_venv(cmd)
            self._log(level=2, msg="run_command : cmd=%s rc=%s" % (cmd, rc))
            self._log(level=1, msg="repo: %s Dependancies installed" % repo_path)
            return rc
        except Exception as e:
            traceback.print_exc()
            raise e

    def activate_ansible_in_venv(self, ansible_path):
        if not os.path.exists(ansible_path):
            self._log(level=0, msg="No ansible repo at: %s" % ansible_path)
        try:
            os.chdir(ansible_path)
        except (OSError, IOError) as e:
            raise e

        cmd = ['make', 'install']
        try:
            rc = self.execute_command_in_venv(cmd)
            self._log(level=2, msg="run_command : cmd=%s rc=%s" % (cmd, rc))
            self._log(level=0, msg="Ansible installed from :%s" % ansible_path)
            return rc
        except Exception as e:
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
            self._log(level=2, msg="run_command : cmd=%s rc=%s" % (cmd, rc))
            return out
        except Exception as e:
            traceback.print_exc()
