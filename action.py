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

class Action(object):
    def __init__(self, verbose=False):
        self._path = None
        self._verbose = verbose

    def _log(self, level=0, msg=None):
        if level or self._verbose:
            if msg:
                print(msg)

    def create_directory(self, path):
        path = os.path.abspath(path)
        self._path = path
        if os.path.exists(path):
            self._log(level=1, msg="directory exists: %s" % path)
            return True
        try:
            os.makedirs(path)
            self._log(level=1, msg="Created directory: %s" % path)
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
        self._log(level=0, msg="Executing cmd: %s " % args)
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
                self._log(level=0, msg=stdout)
                self._log(level=1, msg=stderr)

            cmd.stdout.close()
            cmd.stderr.close()
            return cmd.returncode

        except (OSError, IOError) as e:
            self._log(level=1, msg="Error Executing CMD: %s Exception: %s" % (args, e))
            raise e

    def _change_root_work_directory(self):
        try:
            os.chdir(self._path)
        except (OSError, IOError) as e:
            raise e

    def create_venv(self, app_name='.venv'):
        venv_abspath = os.path.abspath(os.path.join(self._path, app_name))
        if os.path.exists(venv_abspath):
           self._log(level=1, msg="venv exists : %s" % venv_abspath)
           return

        try:
            self._change_root_work_directory()
            cmd = ['virtualenv', app_name]
            rc = self.run_command(cmd)
            self._log(level=0, msg=rc)
            self._log(level=1, msg="venv created : %s" % venv_abspath)
        except Exception as e:
            traceback.print_exc()
            raise e




