import click

class Config(object):
    def __init__(self):
        self.verbose = False

pass_config = click.make_pass_decorator(Config)

@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enables verbose mode')
@click.pass_context
def cli(ctx, verbose):
    """ansible-dev is a comman line tool for getting started with
    ansible.
    It does all prerequisite for running ansible and start
    initial template plalybook and roles
    """
    ctx.obj = Config()
    ctx.obj.verbose = verbose

@cli.command()
@click.argument('path', nargs=-1, type=click.Path())
@pass_config
def init(config, path):
    """
    Initialize the environment for ansible in given path
    
    Usage: ansible-dev init <path>
    """
    if not path:
        click.echo("Usage: ansible-dev init <path>")
        return

    if config.verbose:
        click.echo('Start: Init at %s ' % path)
