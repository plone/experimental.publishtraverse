# -*- coding: utf-8 -*-
from DateTime import DateTime
from experimental.publishtraverse import testing
from plone import api
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.testing.z2 import Browser
from zExceptions import NotFound

import transaction
import unittest


class TestStandard(unittest.TestCase):
    """Test without experimental.publishtraverse zcml loaded.

    This basically shows that the package is needed.
    """

    layer = testing.STANDARD_FUNCTIONAL_TESTING

    def test_zopetime(self):
        app = self.layer['app']
        browser = Browser(app)
        browser.handleErrors = False
        browser.open(app.absolute_url() + '/ZopeTime')
        # It simply gets displayed.
        self.assertTrue(browser.contents.startswith(str(DateTime().year())))

    def test_publish_success(self):
        # Test a few locations that definitely need to remain publishable.
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        api.content.create(container=portal, type='Folder', id='folder')
        api.content.create(container=portal, type='Document', id='page')
        folder = portal.folder
        page = portal.page
        logout()
        transaction.commit()

        app = self.layer['app']
        browser = Browser(app)
        browser.handleErrors = False
        methods = ('', 'view')
        for method in methods:
            for obj in (portal, folder, page):
                browser.open(obj.absolute_url() + '/' + method)


class TestExperimental(TestStandard):
    """Test with experimental.publishtraverse zcml loaded.

    We inherit from TestStandard, so that we test the same functionality
    or more.  We may override or add test methods.
    """

    layer = testing.EXPERIMENTAL_FUNCTIONAL_TESTING

    def test_zopetime(self):
        app = self.layer['app']
        browser = Browser(app)
        browser.handleErrors = False
        # There is nothing wrong with publishing ZopeTime,
        # but no security is checked, so we disallow it.
        self.assertRaises(
            NotFound,
            browser.open,
            app.absolute_url() + '/ZopeTime')
