import os
from ansible_dev.lib.action import Action
import click

class CurrentContext(object):
    def __init__(self, path, venv_name):
        self._path = path
        self._venv = venv_name
        self._action = Action(verbose=False, path=path, venv=venv_name)

    def run(self, command):
        rc, out = self._action.execute_command_in_venv(command)
        return rc, out


class Context(object):
    def __init__(self, config_handler):
        self._cfg = config_handler
        self._contexts = []
 
    def get_all_context(self):
        sections = self._cfg.get_value("ansible-dev.cfg")
        for sec in sections:
            ctx = {}
            if sec == 'defaults':
                continue
            venv = self._cfg.get_value("ansible-dev.cfg", sec,
                    'venv_name')
            ctx['path'] = sec.split(':')[1]
            ctx['venv'] = venv
            self._contexts.append(ctx)

    def _print_a_context(self, ctx, detail=True):
        cur_ctx = CurrentContext(ctx['path'], ctx['venv'])
        click.secho("Ansible Workspace: %s" % ctx['path'],
            fg='green', bg='black', bold=True)
        if not detail:
            return
        click.secho("Ansible Installed: ", fg='green',bold=True)
        cmd = ['ansible', '--version']
        rc, out = cur_ctx.run(cmd)
        click.secho(out)
        click.secho("Roles: ", fg='green',bold=True)
        cmd = ['ansible-galaxy', 'list']
        rc, out = cur_ctx.run(cmd)
        click.secho(out)


    def print_all_contexts(self, detail):
        out = ' '
        self.get_all_context()
        for ctx in self._contexts:
            self._print_a_context(ctx, detail)
            
        return out


