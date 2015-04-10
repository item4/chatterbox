from setuptools import setup, find_packages

setup(
    name='chatterbox',
    version='0.0.0',
    description='Chatterbox is simple framework for IRC Bot.',
    author='item4',
    author_email='item4_hun' '@' 'hotmail.com',
    url='https://github.com/item4/chatterbox',
    license='MIT License',
    packages=find_packages(exclude=['tests']),
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
