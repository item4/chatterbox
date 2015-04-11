import collections
import enum
import pathlib
import sys

__all__ = ('ConfigField', 'Service', 'is_alphanumeric', 'is_valid_port',
           'irc_config_fields', 'load_config', 'load_config_from_py',
           'preprocess_config', 'validate_connections')

ConfigField = collections.namedtuple('Config', ['name', 'type', 'validator'])


class Service(enum.Enum):
    irc = 1


def is_valid_port(port: int) -> bool:
    return 0 < port < 65536


def is_alphanumeric(value: str) -> bool:
    return value.isalnum()

irc_config_fields = {
    ConfigField('URL', str, None),
    ConfigField('NAME', str, None),
    ConfigField('PORT', int, is_valid_port),
    ConfigField('USE_SSL', bool, None),
    ConfigField('USERNAME', str, is_alphanumeric),
    ConfigField('REALNAME', str, is_alphanumeric),
}


def load_config(file: pathlib.Path) -> dict:
    if not file.exists():
        print('Config file is not exists!', file=sys.stderr)
        raise SystemExit(1)

    if not file.is_file():
        print('This input is not file!', file=sys.stderr)
        raise SystemExit(1)

    if file.suffix == '.py':
        config = load_config_from_py(file)
    else:
        print('This input is not supported!', file=sys.stderr)
        raise SystemExit(1)

    return preprocess_config(config)


def load_config_from_py(file: pathlib.Path) -> dict:
    config = {}
    with file.open() as f:
        exec(compile(f.read(), file.name, 'exec'), config)
    return config


def preprocess_config(config: dict) -> dict:
    res = {}
    for key, value in config.items():
        if not key.isupper():
            continue

        if key.endswith('_DIR') and not isinstance(value, pathlib.Path):
            value = pathlib.Path(value)

        if key == 'CONNECTIONS':
            for conn in value:
                validate_connections(conn)

        res[key] = value

    return res


def validate_connections(value: dict):
    try:
        service_type = value['TYPE']
    except KeyError:
        print('Need service type', file=sys.stderr)
        raise SystemExit(1)

    if service_type not in Service.__members__.values():
        print('{} is not supported!'.format(service_type),
              file=sys.stderr)
        raise SystemExit(1)

    config_fields = dict()
    if service_type == Service.irc:
        config_fields = irc_config_fields

    for name, type_, validator in config_fields:
        try:
            v = value[name]
        except KeyError:
            print('Need {} value.'.format(name), file=sys.stderr)
            raise SystemExit(1)

        if not isinstance(v, type_):
            print('Type of {} is must be {}. {} given.'.format(
                name,
                type_.__name__,
                type(v)
            ), file=sys.stderr)
            raise SystemExit(1)

        if validator is not None and not validator(v):
            print('Value of {} is invalid.'.format(name),
                  file=sys.stderr)
            raise SystemExit(1)

    return True
