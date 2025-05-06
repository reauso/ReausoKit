import unittest
from contextlib import contextmanager


class ExtendedTestCase(unittest.TestCase):
    @contextmanager
    def assertNotRaised(self, expected_exception=Exception):
        try:
            yield None
        except expected_exception as e:
            raise self.failureException(f'{type(e).__name__} (subclass of {expected_exception.__name__}) raised')