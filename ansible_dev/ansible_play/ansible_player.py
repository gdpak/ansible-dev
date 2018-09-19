import os

class AnsibleRunner(object):
    def __init__(self, ctx):
        self._ctx = ctx

    def prepare_ansible_runner_env(self):
        cfg_obj = self._ctx._cfg
        self._runner_path = os.path.join(self._ctx._cfg._path, self._ctx._cfg._runner_homedir)
        cfg_obj.copy_ansible_runner_input_dir()
        # copy current path to env vars for ansible_runner
        kwargs = dict(
            workspace_root=self._ctx._current_ctx._path,
            templates_path=os.path.join(self._runner_path, 'templates'),
        )
        cfg_obj.copy_runner_vars_for_ansible('env', 'extravars', **kwargs)

        # Install ansible-runner in venv
        cmd = ['pip', 'install' , 'ansible-runner']
        self._ctx.run_command(cmd)

    def create_playbook_with_name(self, name):
        # run playbook in venv
        cmd = ['ansible-runner', '--playbook', 'playbook.yml', 'run',
            self._runner_path, '--cmdline' , '\'-e playbook_name=%s\'' % name]
        self._ctx.run_command(cmd, verbose=3)

    def create_role_with_name(self, name):
        # run playbook in venv
        cmd = ['ansible-runner', '--playbook', 'role_create.yml', 'run',
            self._runner_path, '--cmdline' , '\'-e role_name=%s\'' % name]
        self._ctx.run_command(cmd, verbose=3)
