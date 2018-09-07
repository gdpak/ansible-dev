import click
from action import Action
import traceback

class Config(object):
    def __init__(self):
        self.verbose = False
        self.action_plugin = None

pass_config = click.make_pass_decorator(Config)

@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enables verbose mode')
@click.option('--debug', '-d', is_flag=True, help='Enables debug mode')
@click.pass_context
def cli(ctx, verbose, debug):
    """ansible-dev is a comman line tool for getting started with
    ansible.
    It does all prerequisite for running ansible and start
    initial template plalybook and roles
    """
    ctx.obj = Config()
    ctx.obj.verbose = verbose
    ctx.obj.debug = debug
    ctx.obj.action_plugin = Action(verbose)

@cli.command()
@click.option('--venv-name', default='.venv',
              type=click.STRING, help='Name to create virtualenv')
@click.argument('path', type=click.Path())
@pass_config
def init(config, path, venv_name):
    """
    Initialize the environment for ansible in given path
    
    Usage: ansible-dev init <path>
    """
    if not path:
        click.echo("Usage: ansible-dev init <path>")
        return

    if config.verbose:
        click.echo('Start: Init at %s ' % path)
    
    if config.debug:
        click.echo("Init args: path=%s, venv_name=%s" % (path, venv_name))
        click.echo("Init args type: path=%s, venv_name=%s" %
                  (type(path), type(venv_name)))

    try:
        config.action_plugin.create_directory(path)
        config.action_plugin.create_venv(app_name=venv_name)
    except Exception as e:
        print ("Failed : Exception %s" % e)
        if config.debug:
            traceback.print_exc()
        return
