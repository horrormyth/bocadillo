import os
from inspect import cleandoc

import pytest
from click.testing import CliRunner

from bocadillo.cli import create_cli


@pytest.fixture
def runner():
    return CliRunner()


def test_can_init_db(runner, tmpdir):
    cli = create_cli()
    result = runner.invoke(cli, [
        'init:db',
        '--directory', str(tmpdir),
        '-y',
    ])
    assert result.exit_code == 0
    assert 'success' in result.output.lower()


@pytest.mark.parametrize('driver, expected_hints', [
    ('sqlite', ('DB_NAME',)),
    ('mysql', ('DB_NAME', 'DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD')),
    ('pgsql', ('DB_NAME', 'DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD')),
])
def test_can_choose_driver(runner, driver, expected_hints, tmpdir):
    cli = create_cli()

    result = runner.invoke(cli, [
        'init:db',
        '--driver', driver,
        '--directory', str(tmpdir),
        '-y',
    ])

    assert result.exit_code == 0, result.output

    output = result.output
    for hint in expected_hints:
        assert hint in output
