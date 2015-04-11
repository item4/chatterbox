import copy
import pathlib

from chatterbox.config import (Service, is_alphanumeric, is_valid_port,
                               load_config, load_config_from_py,
                               preprocess_config, validate_connections)

import pytest


def test_is_alphanumeric():
    """Test :func:`chatterbox.config.is_alphanumeric`."""
    
    # Case 1. it's all alphanumeric.
    assert is_alphanumeric(
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        'abcdefghijklmnopqrstuvwxyz'
        '0123456789'
    )

    # Case 2. it's all non-alphanumeric.
    not_alphanumerics = {'!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-',
                         '_', '=', '+', '\\', '|', '[', ']', '{', '}', ':',
                         ';', '"', "'", '/', '?', ',', '.', '<', '>', '`', '~'}
    for char in not_alphanumerics:
        assert not is_alphanumeric(char)


def test_is_valid_port():
    """Test :func:`chatterbox.config.is_valid_port`."""
    
    # Case 1. it's all valid port.
    for port in range(1, 65535 + 1):
        assert is_valid_port(port)

    # Case 2. -1 is not valid port.
    assert not is_valid_port(-1)

    # Case 3. 65536 is not valid port.
    assert not is_valid_port(65536)


def test_load_config(fx_tmpdir: pathlib.Path, fx_config_file_py: pathlib.Path):
    """Test :func:`chatterbox.config.load_config`."""
    
    # Case 1. non exists file: raise SystemExit
    non_exists_file = fx_tmpdir / 'null'
    assert not non_exists_file.exists()
    with pytest.raises(SystemExit):
        load_config(non_exists_file)

    # Case 2. given path is dir: raise SystemExit
    dir_path = fx_tmpdir / 'dir'
    dir_path.mkdir()
    assert dir_path.is_dir()
    with pytest.raises(SystemExit):
        load_config(dir_path)

    # Case 3. valid config: work normally
    config = load_config(fx_config_file_py)
    assert type(config) == dict
    assert 'MODULE_DIR' in config
    assert 'NON_EXISTS_KEY' not in config
    assert 'it_will_be_removed' not in config

    # Case 4. non support suffix: raise SystemExit
    non_support_suffix = fx_tmpdir / 'config.zip'
    non_support_suffix.touch()
    assert non_support_suffix.exists()
    with pytest.raises(SystemExit):
        load_config(non_support_suffix)


def test_load_config_from_py(fx_config_file_py: pathlib.Path):
    """Test :func:`chatterbox.config.load_config_from_py`."""
    config = load_config_from_py(fx_config_file_py)

    # Case 1. result is dict
    assert type(config) == dict

    # Case 2. exists keys
    assert 'MODULE_DIR' in config
    assert 'CONNECTIONS' in config

    # Case 3. exists keys. but lowercase. it will be removed
    # in :func:`chatterbox.config.preprocess_config`
    assert 'it_will_be_removed' in config

    # Case 4. non exists key
    assert 'NON_EXISTS_KEY' not in config


def test_preprocess_config():
    """Test :func:`chatterbox.config.preprocess_config`."""

    config = {
        'TEST_1_DIR': pathlib.Path('/'),
        'TEST_2_DIR': '/',
        'it_will_be_removed': True,
        'CONNECTIONS': [],
    }

    res = preprocess_config(config)

    # Case 1. keep only uppercase.
    assert 'TEST_1_DIR' in res
    assert 'TEST_2_DIR' in res
    assert 'it_will_be_removed' not in res

    # Case 2. DIR path change to :type:`pathlib.Path` automatically.
    assert isinstance(res['TEST_1_DIR'], pathlib.Path)
    assert isinstance(res['TEST_2_DIR'], pathlib.Path)


def test_validate_connections():
    """Test :func:`chatterbox.config.validate_connections`."""

    conn = {
        'TYPE': Service.irc,
        'URL': 'irc.ozinger.org',
        'PORT': 6667,
        'USE_SSL': False,
        'NAME': 'BotName',
        'USERNAME': 'dogdog',
        'REALNAME': 'dogdog',
    }

    # Case 1. Missing service type
    wrong_conn = copy.deepcopy(conn)
    del wrong_conn['TYPE']
    with pytest.raises(SystemExit):
        validate_connections(wrong_conn)

    # Case 2. Wrong service type
    wrong_conn = copy.deepcopy(conn)
    wrong_conn['TYPE'] = 'kakaotalk'
    with pytest.raises(SystemExit):
        validate_connections(wrong_conn)

    # Case 3. Missing url
    wrong_conn = copy.deepcopy(conn)
    del wrong_conn['URL']
    with pytest.raises(SystemExit):
        validate_connections(wrong_conn)

    # Case 4. Wrong url
    wrong_conn = copy.deepcopy(conn)
    wrong_conn['URL'] = 1234
    with pytest.raises(SystemExit):
        validate_connections(wrong_conn)

    # Case 5. Missing name
    wrong_conn = copy.deepcopy(conn)
    del wrong_conn['NAME']
    with pytest.raises(SystemExit):
        validate_connections(wrong_conn)

    # Case 6. Wrong name
    wrong_conn = copy.deepcopy(conn)
    wrong_conn['NAME'] = 1234
    with pytest.raises(SystemExit):
        validate_connections(wrong_conn)

    # Case 7. Missing use ssl
    wrong_conn = copy.deepcopy(conn)
    del wrong_conn['USE_SSL']
    with pytest.raises(SystemExit):
        validate_connections(wrong_conn)

    # Case 8. Wrong use ssl
    wrong_conn = copy.deepcopy(conn)
    wrong_conn['USE_SSL'] = None
    with pytest.raises(SystemExit):
        validate_connections(wrong_conn)

    # Case 9. Missing port
    wrong_conn = copy.deepcopy(conn)
    del wrong_conn['PORT']
    with pytest.raises(SystemExit):
        validate_connections(wrong_conn)

    # Case 10. Wrong type port
    wrong_conn = copy.deepcopy(conn)
    wrong_conn['PORT'] = '6667'
    with pytest.raises(SystemExit):
        validate_connections(wrong_conn)

    # Case 11. Wrong port
    wrong_conn = copy.deepcopy(conn)
    wrong_conn['PORT'] = 1234567890
    with pytest.raises(SystemExit):
        validate_connections(wrong_conn)

    # Case 12. Missing username
    wrong_conn = copy.deepcopy(conn)
    del wrong_conn['USERNAME']
    with pytest.raises(SystemExit):
        validate_connections(wrong_conn)

    # Case 13. Wrong type username
    wrong_conn = copy.deepcopy(conn)
    wrong_conn['USERNAME'] = 1234
    with pytest.raises(SystemExit):
        validate_connections(wrong_conn)

    # Case 14. Wrong username
    wrong_conn = copy.deepcopy(conn)
    wrong_conn['USERNAME'] = ':'
    with pytest.raises(SystemExit):
        validate_connections(wrong_conn)

    # Case 15. Missing realname
    wrong_conn = copy.deepcopy(conn)
    del wrong_conn['REALNAME']
    with pytest.raises(SystemExit):
        validate_connections(wrong_conn)

    # Case 16. Wrong type realname
    wrong_conn = copy.deepcopy(conn)
    wrong_conn['REALNAME'] = 1234
    with pytest.raises(SystemExit):
        validate_connections(wrong_conn)

    # Case 17. Wrong realname
    wrong_conn = copy.deepcopy(conn)
    wrong_conn['REALNAME'] = ':'
    with pytest.raises(SystemExit):
        validate_connections(wrong_conn)

    # Case 18. work normally
    assert validate_connections(conn)
