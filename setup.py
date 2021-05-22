import io
import os
import sys

from advanced_filters import __version__
from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


class Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)


def get_full_description():
    # get long description from README
    readme = 'README.rst'
    changelog = 'CHANGELOG.rst'
    base = os.path.dirname(__file__)
    with io.open(os.path.join(base, readme), encoding='utf-8') as readme:
        README = readme.read()
    with io.open(os.path.join(base, changelog), encoding='utf-8') as changelog:
        CHANGELOG = changelog.read()
    return '%s\n%s' % (README, CHANGELOG)


# allow setup.py to be run from any path
CUR_DIR = os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir))
os.chdir(CUR_DIR)
TEST_REQ_FILE = os.path.join(CUR_DIR, 'test-reqs.txt')
if os.path.exists(TEST_REQ_FILE):
    with open(TEST_REQ_FILE) as f:
        TEST_REQS = list(f.readlines())
else:
    TEST_REQS = []


setup(
    name='django-advanced-filters',
    version=__version__,
    url='https://github.com/modlinltd/django-advanced-filters',
    license='MIT',
    description='A Django application for advanced admin filters',
    keywords='django-admin admin advanced filters custom query',
    long_description=get_full_description(),
    packages=find_packages(exclude=['tests*', 'tests.*', '*.tests']),
    include_package_data=True,
    install_requires=[
        'simplejson>=3.6.5,<4',
    ],
    extras_require=dict(test=TEST_REQS),
    zip_safe=False,
    author='Pavel Savchenko',
    author_email='pavel@modlinltd.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    tests_require=['tox'],
    cmdclass={'test': Tox},
)
