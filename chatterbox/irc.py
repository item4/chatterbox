import asyncio
import functools
import re


__all__ = 'Bot', 'Line'


class Bot:

    def __init__(self, app, index: int):
        self.reader = None
        self.writer = None
        self.app = app
        self.index = index
        self.config = app.config['CONNECTIONS'][index]

    @asyncio.coroutine
    def connect(self):
        connection = asyncio.open_connection(
            self.config['URL'],
            self.config['PORT'],
            ssl=self.config.get('USE_SSL', False),
            loop=self.app.loop
        )
        reader, writer = yield from connection

        self.reader = reader
        self.writer = writer

    @asyncio.coroutine
    def handshake(self):
        yield from self.irc.nick(self.config['NAME'])
        yield from self.irc.user(self.config['USERNAME'],
                                 self.config['REALNAME'])

    @asyncio.coroutine
    def close(self):
        if self.writer is not None:
            self.writer.close()

    @asyncio.coroutine
    def send(self, message):
        print('>>> %s' % message)
        self.writer.write(message.encode('u8', 'ignore'))

    @property
    def irc(self):
        @asyncio.coroutine
        def send(command: str, params: list = None, message: str = None):
            command = command.upper()
            if params is None:
                params = []
            param_string = ' '.join(params)

            result = command

            if param_string:
                result += ' ' + param_string

            if message:
                result += ' :' + message

            result += '\n'

            yield from self.send(result)

        class Irc:

            @staticmethod
            @asyncio.coroutine
            def mode(mode: _Mode):
                yield from send('MODE', [str(mode)])

            @staticmethod
            @asyncio.coroutine
            def nick(name: str):
                yield from send('NICK', [name])

            @staticmethod
            @asyncio.coroutine
            def pong(return_msg: str):
                yield from send('PONG', message=return_msg)

            @staticmethod
            @asyncio.coroutine
            def user(username: str, realname: str):
                yield from send('USER', [username, '0', '*'], realname)

        return Irc

    @asyncio.coroutine
    def parse(self):
        data = yield from self.reader.readline()

        data = data.decode('u8').rstrip()
        print('<<< %s' % data)
        if data.startswith('PING '):
            if data[5] == ':':
                res = data[6:]
            else:
                res = data[5:]
            yield from self.irc.pong(res)
            return True
        elif data.startswith('ERROR '):
            return False
        else:
            line = Line(data)
            res = True
            handler_list = self.app.on_handler['irc'].get(line['command'], [])
            for handler in handler_list:
                res = yield from handler(self, line)
                if res is None:
                    res = True
                if not res:
                    break
            return res

    @asyncio.coroutine
    def run(self):
        while True:
            try:
                yield from self.connect()
                yield from self.handshake()
                running = True
                while running:
                    running = yield from self.parse()
            except Exception as e:
                print(e)
            finally:
                yield from self.close()


class Line(dict):

    pattern = re.compile(
        r'^:(?:(?P<name>[^!\s]+)!(?P<ident>[^@\s]+)@'
        r'(?P<host>[^\s]+)|(?P<server>[^!\s]+)) '
        r'(?P<command>[^\s]+)(?: (?P<params>[^:].*))?(?: :(?P<message>.+?))?$'
    )

    def __init__(self, raw):
        super(dict).__init__()
        self['raw'] = raw
        self.update(self.pattern.match(raw).groupdict())
        self['params'] = (self['params'] or '').split(' ')

    def __repr__(self):
        return self['raw']


class _Mode:
    def __init__(self, target: str, keyword: str, *, inverse: bool = False):
        self.mode = keyword
        self.target = target
        self.stat = not inverse
        self.modes = {keyword: {target: not inverse}}

    def __invert__(self):
        self.stat = not self.stat
        self.modes[self.mode][self.target] = self.stat

    def __iter__(self):
        return self.modes.items()

    def __str__(self):
        target_buff = []
        mode_buff = []

        for mode, members in self.modes.items():
            for target, stat in members.items():
                target_buff.append(target)
                if stat:
                    mode_str = '+' + mode
                else:
                    mode_str = '-' + mode
                mode_buff.append(mode_str)

        if target_buff:
            return ' '.join(target_buff) + ' ' + ''.join(mode_buff)
        else:
            raise RuntimeError

    def add(self, other):
        for mode, members in other:
            if mode in self.modes:
                for target, stat in members.items():
                    if target in self.modes[mode] and \
                       stat != self.modes[mode][target]:
                        del self.modes[mode][target]

                if not self.modes[mode]:
                    del self.modes[mode]
            else:
                self.modes[mode] = members


class _UserMode(_Mode):

    def __add__(self, other):
        if isinstance(other, self.__class__):
            self.add(other)
        else:
            raise TypeError


class _ChannelMode(_Mode):

    def __add__(self, other):
        if isinstance(other, self.__class__):
            self.add(other)
        else:
            raise TypeError


class UserMode:

    SERVER_EXTENSION = functools.partial(_UserMode, keyword='x')
    x = functools.partial(_UserMode, keyword='x')
