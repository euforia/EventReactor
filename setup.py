
from setuptools import setup, find_packages

setup(
	name='event-reactor',
	version='0.1.0',
	url='http://git.tm.tmcs/infradev/event-reactor.git',
	description='Hookable and reactable event system',
	long_description=open('README.rst').read(),
	author='abs',
	author_email='abs.pathak@ticketmaster.com',
	license='LICENSE.txt',
	packages=find_packages(),
	data_files=[
		('/etc/event-reactor',			 ['etc/config.json.sample', 'etc/event-handlers.json.sample']),
		('/usr/local/bin/event-reactor', ['fire-event.py', 'event-router.py', 'event-sub.py'])
	],
	install_requires=[ p for p in open('REQUIREMENTS.txt').read().split('\n') if p != '' ],
)