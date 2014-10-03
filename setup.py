
from setuptools import setup, find_packages

setup(
    name='EventReactor',
    version='0.1.0',
    url='https://github.com/euforia/EventReactor.git',
    description='Hookable and reactable event system',
    long_description=open('README.rst').read(),
    author='euforia',
    author_email='euforia@gmail.com',
    license='LICENSE.txt',
    packages=find_packages(),
    data_files=[
        ('/etc/event-reactor',                ['etc/config.json.sample', 'etc/event-handlers.json.sample']),
        ('/etc/event-reactor/event-handlers', ['etc/event-handlers/testing.py']),
        ('/usr/local/bin',                    ['fire-event.py', 'event-router.py', 'event-sub.py']),
        ('/etc/init.d',                       ['etc/init.d/event-reactor'])
    ],
    install_requires=[ p for p in open('REQUIREMENTS.txt').read().split('\n') if p != '' ],
)