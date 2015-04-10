import asyncio
import collections
import collections.abc
import pathlib
import sys

from .config import Service, load_config
from .globals import _globals, Proxy
from .irc import Bot


__all__ = 'Chatterbox',

app = Proxy('app')


class Chatterbox:

    def __init__(self, app_name: str, config_file: pathlib.Path):
        self.loop = asyncio.get_event_loop()
        self.config = load_config(config_file)
        self.app_name = app_name
        self.module = {}
        self.on_handler = dict(irc=collections.defaultdict(list))
        setattr(_globals, 'app', self)

    @property
    def irc(self) -> object:
        on_handler = self.on_handler['irc']

        class Irc:

            @staticmethod
            def on(command: str):
                command = command.upper()

                def decorator(func: collections.abc.Callable):
                    if not asyncio.iscoroutine(func):
                        func = asyncio.coroutine(func)

                    on_handler[command].append(func)
                    return func
                return decorator
        return Irc

    def run(self):
        if not self.config['MODULE_DIR'].exists():
            print('MODULE_DIR is not exists!', file=sys.stderr)
            raise SystemExit(1)
        for module_file in self.config['MODULE_DIR'].iterdir():
            if module_file.suffix == '.py' and \
               module_file.name != '__init__.py':
                with module_file.open() as f:
                    print(module_file.name)
                    print(self.module)
                    exec(
                        compile(f.read(), module_file.name, 'exec'),
                        self.module
                    )

        for index, conn in enumerate(self.config['CONNECTIONS']):
            tasks = []
            if conn['TYPE'] == Service.irc:
                tasks.append(asyncio.async(Bot(self, index).run()))

        self.loop.run_until_complete(asyncio.wait(tasks))
        self.loop.close()
