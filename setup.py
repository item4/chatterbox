import os

from setuptools import setup, find_packages


def readme():
    try:
        with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
            return f.read()
    except (IOError, OSError):
        return ''

tests_require = {
    'pytest >= 2.7.0',
}

setup(
    name='chatterbox',
    version='0.0.0',
    description='Chatterbox is simple framework for IRC Bot.',
    long_description=readme(),
    author='item4',
    author_email='item4_hun' '@' 'hotmail.com',
    url='https://github.com/item4/chatterbox',
    license='MIT License',
    packages=find_packages(exclude=['tests']),
    tests_require=tests_require,
    extras_require={
        'tests': tests_require,
    },
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
