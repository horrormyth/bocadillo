"""Bocadillo CLI factory."""
import os
import pathlib
from inspect import cleandoc
from typing import List, Optional

import click

CUSTOM_COMMANDS_FILE_ENV_VAR = 'BOCA_CUSTOM_COMMANDS_FILE'


def get_custom_commands_file_path():
    return os.getenv(CUSTOM_COMMANDS_FILE_ENV_VAR, 'boca.py')


class FileGroupCLI(click.MultiCommand):
    """Multi-command CLI that loads a group of commands from a file.

    Notes
    -----
    - Commands are loaded from a file determined by `file_name`, relative to the
    current working directory (i.e., when the CLI script is executed).
    - The first click.Group object found in that file is used as a source of
    commands.

    Inspired By
    -----------
    https://click.palletsprojects.com/en/7.x/commands/#custom-multi-commands
    """

    def __init__(self, file_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._group: click.Group = None
        self.file_name = file_name

    def _load_group(self):
        ns = {}
        path = self.file_name

        try:
            with open(path, 'r') as f:
                code = compile(source=f.read(), filename=path, mode='exec')
                eval(code, ns, ns)
        except FileNotFoundError:
            # User did not create custom commands, use an empty group.
            self._group = click.Group()
            return

        for key, value in ns.items():
            if isinstance(value, click.Group):
                self._group = value
                break
        else:
            raise click.ClickException(
                f'Expected at least one group in {path}, none found.'
            )

    @property
    def group(self) -> click.Group:
        """Lazy-loaded, cached group object."""
        if self._group is None:
            self._load_group()
        return self._group

    def list_commands(self, ctx: click.Context) -> List[str]:
        return self.group.list_commands(ctx)

    def get_command(self, ctx: click.Context, name: str) -> click.Command:
        return self.group.get_command(ctx, name)


def create_cli() -> click.Command:
    @click.group()
    def builtin():
        pass

    @builtin.command(name='help')
    @click.pass_context
    def help_(ctx):
        """Show help about boca."""
        click.echo(ctx.parent.get_help())

    @builtin.command(name='init:db')
    @click.option('-d', '--driver',
                  type=click.Choice(['mysql', 'pgsql', 'sqlite']),
                  default='sqlite')
    @click.option('-y', '--no-input', is_flag=True,
                  help='Answer yes to all confirmations.')
    @click.option('--directory',
                  default='.',
                  help='Where files should be generated')
    def init_db(driver: Optional[str], no_input: bool, directory: str):
        """Generate files for configuring a database."""
        options = {'driver': driver}
        options_contents = ', '.join(f'{key}=\'{value}\''
                                     for key, value in options.items())
        contents = cleandoc(
            f'''"""Database configuration.
            
            For help with the Orator ORM, see the official docs:
            https://orator-orm.com
            
            Get started: import the `Model` base class from here and start
            building models!
            """
            from dotenv import load_dotenv

            from bocadillo.db import setup_db

            load_dotenv()
            db, Model, DATABASES = setup_db({options_contents})
            '''
        ) + '\n'
        click.echo(click.style('Using driver: '), nl=False)
        click.echo(click.style(driver, fg='blue'))

        where = pathlib.Path(directory)
        config_package = where / 'config'
        config_package_path = str(config_package)
        db_script_path = str(where / 'config' / 'db.py')

        if not os.path.exists(config_package_path):
            config_package.mkdir()
            with open(str(config_package / '__init__.py'), 'w') as f:
                pass

        if os.path.exists(db_script_path) and not no_input:
            click.confirm(
                click.style(
                    f'{db_script_path} will be overwritten. Continue?',
                    fg='yellow',
                ),
                abort=True,
            )

        with open(db_script_path, 'w') as f:
            f.write(contents)

        click.echo(click.style('Success. ', fg='green', bold=True), nl=False)

        env_variables_by_driver = {
            'sqlite': (
                'DB_NAME',
            ),
            'mysql': (
                'DB_NAME',
                'DB_HOST',
                'DB_PORT',
                'DB_USER',
                'DB_PASSWORD',
            ),
            'pgsql': (
                'DB_NAME',
                'DB_HOST',
                'DB_PORT',
                'DB_USER',
                'DB_PASSWORD',
            ),
        }
        env_variables = env_variables_by_driver[driver]
        click.echo(
            'Remember setting the following environment variable(s): '
            f'{", ".join(env_variables)}.'
        )

    @builtin.command(name='init:custom')
    @click.option('-d', '--directory', default='',
                  help='Where files should be generated.')
    def init_custom(directory: str):
        """Generate files required to build custom commands."""
        custom_commands_script_contents = cleandoc(
            '''"""Custom Bocadillo commands.
    
            Use Click to build custom commands. For documentation, see:
            https://click.palletsprojects.com
            """
            from bocadillo.ext import click
    
    
            @click.group()
            def cli():
                pass
    
            # Write your @cli.command() functions below.\n
            '''
        ) + '\n'
        path = os.path.join(directory, get_custom_commands_file_path())
        with open(path, 'w') as f:
            f.write(custom_commands_script_contents)
        click.echo(click.style(f'Generated {path}', fg='green'))
        click.echo('Open the file and start building!')

    custom = FileGroupCLI(
        file_name=get_custom_commands_file_path(),
    )

    # Builtins first to prevent override in custom commands.
    return click.CommandCollection(sources=[builtin, custom])


# Exposed to the setup.py entry point
cli = create_cli()
