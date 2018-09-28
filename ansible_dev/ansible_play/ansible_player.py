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
        #cmd = ['pip', 'install' , 'ansible-runner']
        #self._ctx.run_command(cmd)

    def create_playbook_with_name(self, name):
        # run playbook in venv
        #cmd = ['ansible-runner', '--playbook', 'playbook.yml', 'run',
        #    self._runner_path, '--cmdline' , '\'-e playbook_name=%s\'' % name]
        # FIXME: ansible-runner has installation issues on many OS
        #        so we are using ansible-playbook till then
        self._inv_path = os.path.join(self._runner_path, 'tmp_inventory')
        self._playbook_project = os.path.join(self._runner_path, 'project')
        playbook_path = os.path.join(self._playbook_project, 'playbook.yml')
        cmd = ['ansible-playbook', playbook_path,
               '-i', self._inv_path,
               '-e playbook_name=%s workspace_root=%s templates_path=%s' \
               % (name, self._ctx._current_ctx._path, 
                  os.path.join(self._runner_path, 'templates'))]
        self._ctx.run_command(cmd, verbose=3)

    def create_role_with_name(self, name):
        # run playbook in venv
        #cmd = ['ansible-runner', '--playbook', 'role_create.yml', 'run',
        #    self._runner_path, '--cmdline' , '\'-e role_name=%s\'' % name]
        # FIXME: ansible-runner has installation issues on many OS
        #        so we are using ansible-playbook till then
        self._inv_path = os.path.join(self._runner_path, 'tmp_inventory')
        self._playbook_project = os.path.join(self._runner_path, 'project')
        role_play_path = os.path.join(self._playbook_project, 'role_create.yml')
        cmd = ['ansible-playbook', role_play_path,
               '-i', self._inv_path,
               '-e role_name=%s workspace_root=%s templates_path=%s' \
               % (name, self._ctx._current_ctx._path, 
                  os.path.join(self._runner_path, 'templates'))]
        self._ctx.run_command(cmd, verbose=3)
