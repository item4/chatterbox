import pathlib

import pytest


@pytest.fixture
def fx_tmpdir(tmpdir):
    return pathlib.Path(str(tmpdir))


@pytest.fixture
def fx_config_file_py(fx_tmpdir):
    contents = """
import pathlib

from chatterbox.config import Service

MODULE_DIR = pathlib.Path('modules/')

it_will_be_removed = True

CONNECTIONS = [
    {
        'TYPE': Service.irc,
        'URL': 'irc.ozinger.org',
        'PORT': 6667,
        'USE_SSL': False,
        'NAME': 'BotName',
        'USERNAME': 'dogdog',
        'REALNAME': 'dogdog',
    },
]
"""
    file = fx_tmpdir / 'test.cfg.py'
    with file.open('w') as f:
        f.write(contents)

    return file

