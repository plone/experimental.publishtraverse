# -*- coding: utf-8 -*-
import os
import string
import unittest


class TestHelperFunctions(unittest.TestCase):
    """Test helper functions.
    """

    def test_allow_object(self):
        from experimental.publishtraverse.traverser import allow_object
        # This should be True if we pass in Manager and/or Site Administrator,
        # and False if we pass in anything else.
        self.assertTrue(allow_object(['Manager']))
        self.assertTrue(allow_object(('Manager',)))
        self.assertTrue(allow_object(['Site Administrator']))
        self.assertTrue(allow_object(['Manager', 'Site Administrator']))
        self.assertFalse(allow_object(['Anonymous']))
        self.assertFalse(allow_object(['Anonymous', 'Site Administrator']))
        self.assertFalse(allow_object(['Manager', 'Member']))
        self.assertFalse(allow_object(['Manager', 'Member',
                                       'Site Administrator']))
        self.assertFalse(allow_object([]))
        # Test some unexpected input for good measure.
        self.assertFalse(allow_object(None))
        self.assertFalse(allow_object(''))
        self.assertFalse(allow_object('python'))
        self.assertFalse(allow_object(1))

    def test_boolean_from_env(self):
        from experimental.publishtraverse.traverser import (
            boolean_from_env as be)
        self.assertFalse(be('no such variable', False))
        self.assertTrue(be('no such variable', True))

        # Set an environment variable.
        name = 'experimental_publish_traverse_test_variable'

        # Only some values are read as True.
        # See TRUE_VALUES in traverser.py
        for value in ('true', 't', '1', 'yes', 'y'):
            for trans in (string.lower, string.upper):
                value = trans(value)
                os.environ[name] = value
                self.assertTrue(be(name, False),
                                '{0} should be True'.format(value))

        # All others are False.
        for value in ('false', 'f', '0', 'no', 'n',
                      'hello', 'ja', 'tru', 'yessir'):
            for trans in (string.lower, string.upper):
                value = trans(value)
                os.environ[name] = value
                self.assertFalse(be(name, True),
                                 '{0} should be False'.format(value))

        # cleanup
        del os.environ[name]
