import os
from ansible_dev.lib.action import Action
import click

class CurrentContext(object):
    def __init__(self, path, venv_name, verbose=0):
        self._path = path
        self._venv = venv_name
        self._action = Action(verbose=verbose, path=path, venv=venv_name)

    def run(self, command, verbose=0):
        rc, out = self._action.execute_command_in_venv(command, verbose)
        return rc, out


class Context(object):
    def __init__(self, config_handler, verbose=0):
        self._cfg = config_handler
        self._contexts = []
        self._current_ctx = None
        self._verbose = verbose
    
    @property
    def current_ctx(self):
        return self._current_ctx

    @current_ctx.setter
    def current_ctx(self, path):
        self.get_all_context()
        found = False
        for existing_ctx in self._contexts:
            if str(path) == existing_ctx['path']:
                found = True
                break
        if found:
            workspace_sec = 'workspace:' + str(path)
            venv = self._cfg.get_value("ansible-dev.cfg",
                workspace_sec,
                'venv_name')
            self._current_ctx = CurrentContext(path=path, venv_name=venv,
                    verbose=self._verbose)
            self.set_persistent_current_context(path=path, venv=venv)
        else:
            self._current_ctx = None

 
    def get_all_context(self):
        sections = self._cfg.get_value("ansible-dev.cfg")
        for sec in sections:
            ctx = {}
            if sec == 'defaults' or sec == 'current_context':
                continue
            venv = self._cfg.get_value("ansible-dev.cfg", sec,
                    'venv_name')
            ctx['path'] = sec.split(':')[1]
            ctx['venv'] = venv
            self._update_contexts(ctx)

    def _update_contexts(self, ctx):
        if self._contexts:
           found = False
           for ectx in self._contexts:
               if ectx['path'] == ctx['path']:
                   found = True
           if not found:
               self._contexts.append(ctx)
        else:
            self._contexts.append(ctx)

    def _print_a_context(self, ctx, detail=True):
        cur_ctx = CurrentContext(ctx['path'], ctx['venv'])
        click.secho("Ansible Workspace: %s" % ctx['path'],
            fg='green', bg='black', bold=True)
        if detail:
            click.secho("Ansible Environment : ", fg='green',bold=False)
            cmd = ['ansible', '--version']
            rc, out = cur_ctx.run(cmd)
            click.secho(out)
            venv_path = os.path.join(ctx['path'], ctx['venv'])
            click.secho("Virtualenv : %s" % venv_path, fg='green',bold=False)
            click.secho("Roles: ", fg='green',bold=True)
            cmd = ['ansible-galaxy', 'list']
            rc, out = cur_ctx.run(cmd)
            click.secho(out)
            click.secho('---', fg='blue', bold=True)

    def print_all_contexts(self, detail):
        out = ''
        self.get_all_context()
        for ctx in self._contexts:
            self._print_a_context(ctx, detail)

        if not detail:
            click.secho('---', fg='blue', bold=True)
        curctx = self.current_ctx
        if curctx:
            click.secho("Current working path: %s"
                % self.current_ctx._path, fg='green')
        else:
            click.secho("Current working Environment is not set", fg='red')
            
        return out

    def set_auto_context(self):
        # Get if there is a ctx setting in config file
        secs = self._cfg.get_value("ansible-dev.cfg")
        for sec in secs:
            if sec == 'current_context':
                path = self._cfg.get_value("ansible-dev.cfg", sec, 'path')
                self.current_ctx = path
                return self._current_ctx

        self.get_all_context()
        if not len(self._contexts):
            click.secho("No workspace is created yet. Exiting", fg="red")
        # Set the context to first found workspace
        ctx = self._contexts[0]
        self.current_ctx = CurrentConext(path=ctx["path"],
            venv_name=ctx['venv'])
        self.set_persistent_current_context(path=ctx['path'], venv=ctx['venv'])

    def set_persistent_current_context(self, path, venv):
        cuurent_ctx_section = "current_context"
        kwargs = {}
        current_ctx_vars = dict(
            path=path,
        )
        kwargs[cuurent_ctx_section] = current_ctx_vars
        self._cfg.update_dev_ansible_cfg(**kwargs)

    def run_command(self, cmd, verbose=0):
        rc, out = self.current_ctx.run(cmd, verbose)
        return rc, out

    def add_roles(self, role_name, role_repo, force):
        if role_name:
           if force:
               cmd = ['ansible-galaxy', 'install', role_name, '--force']
           else:
               cmd = ['ansible-galaxy', 'install', role_name]
           self.run_command(cmd)

        if role_repo:
           role_name = role_name = os.path.basename(role_repo)
           ws_path = self._current_ctx._path
           role_path = os.path.join(ws_path, 'roles')
           abs_role_path = os.path.join(role_path, role_name)
           if force:
               cmd = ['git', 'clone', role_repo, abs_role_path, '--force']
           else:
               cmd = ['git', 'clone', role_repo, abs_role_path]
           self.run_command(cmd)
