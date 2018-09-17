import click
from ansible_dev.lib.action import Action
from ansible_dev.config_handler.config import ConfigHandler
from ansible_dev.context_manager.context import Context
import traceback
from colorama import Fore, Back, Style

class Config(object):
    def __init__(self):
        self.verbose = False
        self.action_plugin = None

pass_config = click.make_pass_decorator(Config)

@click.group()
@click.option('--verbose', '-v', count=True, help='Enables'
        ' verbose mode')
@click.pass_context
def cli(ctx, verbose):
    """ansible-dev is a command line tool for getting started with
    ansible.
    It does all prerequisite for running ansible and starts
    initial template for plalybook and roles

    See 'ansible-dev <command> --help' for more information on a specific
    command
    """
    ctx.obj = Config()
    ctx.obj.verbose = verbose
    ctx.obj.action_plugin = Action(verbose)
    ctx.obj.config_handler = ConfigHandler()
    ctx.obj.context = Context(ctx.obj.config_handler)

@cli.command()
@click.option('--venv-name', '-vname', default='.venv',
              type=click.STRING, help='Name to create virtualenv')
@click.option('--ansible-version', '-ver', default='devel',
              type=click.STRING, help='ansible version to checkout')
@click.option('--ansible-repo', '-repo', default='https://github.com/ansible/ansible.git',
              type=click.STRING, help='URL of ansible repo to checkout')
@click.option('--python-version', '-py', default='2.7',
              type=click.STRING, help='python version for ansible')
@click.argument('path', type=click.Path())
@pass_config
def init(config, path, venv_name, ansible_version, ansible_repo, python_version):
    """
    Initialize the environment for ansible in a given directory path
    
    Usage: ansible-dev init <path>
    """

    if not path:
        click.echo("Usage: ansible-dev init <path>")
        return
    
    try:
        workspace_section = 'workspace:' + str(path)
        kwargs = {}
        workspace_vars=dict(
            venv_name=venv_name,
            ansible_version=ansible_version,
            ansible_repo=ansible_repo,
            python_version=python_version,
        )
        kwargs[workspace_section] = workspace_vars
        config.config_handler.update_dev_ansible_cfg(**kwargs)
    except Exception as e:
        if config.verbose > 0:
            traceback.print_exc()
        else:
            click.secho("Could not write to config file: %s. Use -vv for"
                "details" % e, fg='red')
            click.secho(" We can still continue and it can be debugged later",
                fg='blue')

    click.secho('Start: Init at %s ' % path, fg='green')
    
    if config.verbose > 1:
        click.echo("Init args: path=%s, venv_name=%s" % (path, venv_name))
        click.echo("Init args type: path=%s, venv_name=%s" %
                  (type(path), type(venv_name)))

    try:

        click.echo("Step 1/7: create workspace directory")
        config.action_plugin.create_directory(path, config.config_handler)
        click.echo("Step 2/7: create Virtual Environment")
        venv_path = config.action_plugin.create_venv(app_name=venv_name,
            py_version=python_version)
        click.secho("Step 3/7: clone ansible git repo") 
        ansible_path = config.action_plugin.clone_git_repo(
            ansible_repo, ansible_version)
        click.secho("Step 4/7: Install ansible Dependencies in virtial env")
        config.action_plugin.install_repo_dependancies_in_venv(ansible_path)
        click.secho("Step 5/7: Install ansible in virtual-env")
        config.action_plugin.activate_ansible_in_venv(ansible_path)
        click.echo("Step 6/7: Checking ansible installation in virtial env")
        out = config.action_plugin.print_ansible_version(ansible_path)
        click.echo(out)
        click.echo("Step 7/7: Getting all roles defined in config file")
        config.action_plugin.get_roles()
        click.secho("Init Success: Ansible virtual env is ready at : %s" %
                    path, fg='green', bold='True')
        # Set current workspace ctx
        config.context.current_ctx = path
    except Exception as e:
        print ('Failed : Exception %s, run with -vv option to show full'
            ' traceback' % e)
        if config.verbose > 1:
            traceback.print_exc()
        return


@cli.command()
@click.option('--detail', '-l', is_flag=True,
              help='detailed output of ls')
@pass_config
def ls(config, detail):
    """
    show details of ansible envionments
    """
    out = config.context.print_all_contexts(detail)
    click.secho(out, fg='green', bold='True')

@cli.command()
@click.argument('path', type=click.Path())
@pass_config
def workon(config, path):
    """
    set ansible workspace to work on

    Usage: ansible-dev workon <path>\n
    default: Last workspace created by ansible-dev init <path>

    """
    config.context.current_ctx = path

