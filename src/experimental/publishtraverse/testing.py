# -*- coding: utf-8 -*-
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import pkg_resources


try:
    pkg_resources.get_distribution('plone.app.contenttypes')
except pkg_resources.DistributionNotFound:
    HAS_PACT = False
else:
    HAS_PACT = True


class StandardLayer(PloneSandboxLayer):
    # If you want to add standard content, like a Folder or Document, you need
    # to create your own layer, because there are no content types by default
    # in Plone 5 test setup...
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        super(StandardLayer, self).setUpZope(app, configurationContext)
        if HAS_PACT:
            # prepare installing plone.app.contenttypes
            z2.installProduct(app, 'Products.DateRecurringIndex')
            import plone.app.contenttypes
            self.loadZCML(package=plone.app.contenttypes)

    def setUpPloneSite(self, portal):
        super(StandardLayer, self).setUpPloneSite(portal)
        if HAS_PACT:
            # Install into Plone site using portal_setup
            applyProfile(portal, 'plone.app.contenttypes:default')


STANDARD_FIXTURE = StandardLayer()
STANDARD_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(STANDARD_FIXTURE,),
    name='StandardTesting:Functional')


class ExperimentalLayer(StandardLayer):
    defaultBases = (STANDARD_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        super(ExperimentalLayer, self).setUpZope(app, configurationContext)
        # Load ZCML
        import experimental.publishtraverse
        self.loadZCML(package=experimental.publishtraverse)


EXPERIMENTAL_FIXTURE = ExperimentalLayer()
EXPERIMENTAL_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(EXPERIMENTAL_FIXTURE,),
    name='ExperimentalTesting:Functional')
