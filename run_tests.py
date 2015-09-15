import os
import sys

from django.conf import settings
from tests.test_project import settings as test_settings

import django
TEST_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                         'advanced_filters', 'tests')

settings.configure(**vars(test_settings))

try:
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
except ImportError:
    from django.test.simple import DjangoTestSuiteRunner
    test_runner = DjangoTestSuiteRunner(verbosity=1, interactive=False)

try:
    django.setup()
except AttributeError:
    pass

failures = test_runner.run_tests(['advanced_filters'], verbosity=1)
if failures:
    sys.exit(failures)
