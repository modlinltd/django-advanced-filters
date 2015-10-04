from setuptools import setup
import os

from advanced_filters import __version__

with open(os.path.join(os.path.dirname(__file__),
          'README.md')) as readme:
    README = readme.read()

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
    packages=['advanced_filters'],
    url='https://github.com/modlinltd',
    license='MIT License',
    include_package_data=True,
    description='A Django application for advanced admin filters',
    long_description=README,
    install_requires=[
        'django-easy-select2==1.2.5',
        'django-braces==1.4.0',
        'simplejson==3.6.5',
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
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    test_suite='run_tests',
)
