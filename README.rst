.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

===================================
Experimental Zope Publish Traverser
===================================

Be stricter about what gets published by Zope.
Publishing here means: when a browser visits a url, you get a response back.

See discussions on a `dexterity pull request <https://github.com/plone/plone.dexterity/pull/56>`_
and a `CMFPlone issue <https://github.com/plone/Products.CMFPlone/issues/1504#issuecomment-205277360>`_.

Features
--------

This hooks into the default publish traverser of Zope.
It should work for repoze too, but that is not tested.
It works the same as the default publisher, but it is stricter in what it publishes.

The big difference is: an object will only be published if it has security assertions.

In other words: there must be a permission check.
If anyone can access the object without even checking if they have the ``View`` permission, then we refuse to show it.


Why use this?
-------------

Several security hotfixes for Plone have been released the past few years that have explicitly made objects unpublishable.
As anonymous user you could visit a url and get some information that you should not be able to see, and the hotfix fixed that.

This experimental package does **not** automatically fix all such issues.
But it provides a fix for **one** class of such issues: objects that are accessible for anyone without a security check.

It does **not** fix publishing objects that have a proper permission check but that should not be available for a browser after all.
Several methods have proper permission checks so that only authorized users can use those functions from restricted code, like Python skin scripts or templates.
But when they also have a *docstring*, Zope by default allows them to be published, and not everyone realizes this.
This experimental package does not do anything about that: it has no way of knowing if publishing a properly protected method was intentional or not.

Note that there are other ways to make objects publishable: browser views and namespace publishing are both explicit and good ways of making an object publishable, and they are not affected by this package.


Does it work?
-------------

Try adding ``/ZopeTime`` at the end of the url of your Plone Site.
It should fail to load.


Details
-------

Getting an object for publishing is done by the Zope ``BaseRequest`` class in its ``traverse`` method.
It has this code::

   adapter = queryMultiAdapter((object, self),
                               IBrowserPublisher)
   if adapter is None:
       # Zope2 doesn't set up its own adapters in a lot
       # of cases so we will just use a default adapter.
       adapter = DefaultPublishTraverse(object, self)

So what we do is: register an adapter that gets picked up in this code.
The basis is this zcml registration::

    <adapter
        factory=".traverser.StrictPublishTraverse"
        for="* zope.publisher.interfaces.browser.IBrowserRequest"
        />

This points to ``traverser.py`` where we have a ``StrictPublishTraverse`` class that inherits from one of these two classes::

    try:
        from repoze.zope2.publishtraverse import DefaultPublishTraverse
    except ImportError:
        from ZPublisher.BaseRequest import DefaultPublishTraverse

Due to inheritance, the ``StrictPublishTraverse`` class implements ``zope.publisher.interfaces.browser.IBrowserPublisher``, which is what we were after.

The class lets the original class do its work, returning an object and a path.
But then it does extra checks on the object:

- Is its name in the list of ``KNOWN_NAMES``?
  Then we publish it.
  Currently this is only ``index_html``, which is a name that is used a lot, even when you don't see it in the url.

- Is the object a method or function?
  Then we check if there are security assertions on it.
  So: do you need a role or permission to access this?
  If a role or permission is needed and the visitor does not have it, then this point will never be reached: an unauthorized error will already have been raised.
  If no role or permission is needed, then we do the change that is the only reason for the existence of this package: we refuse to publish this item.
  This will show as a '404 Not Found' error.

If you want to dive deeper into what happens internally when Zope publishes an object, see Martin Aspeli's excellent article on `Zope Secrets <http://docs.zope.org/zope_secrets/>`_.


Options
-------

The package looks for these environment variables:

``EXPERIMENTAL_PUBLISH_TRAVERSE_ONLY_WARN``
    When this is set, instead of refusing to publish an object, a warning is logged.
    Default: false.

``EXPERIMENTAL_PUBLISH_TRAVERSE_ACCEPT_KNOWN_NAMES``
    When this is set, the list of known names is taken into account:
    when an object with a name in the known names is published, we accept it without further checks.
    Default: true.

``EXPERIMENTAL_PUBLISH_TRAVERSE_ACCEPT_IF_ONLY_FOR_ADMINS``
    When this is set, if the publishable object is not protected but its container is *only* accessible for admins, we accept it anyway.
    This can happen if its class has ``security.declareObjectProtected(ManagePortal)``,
    like happens when you use the permissions form of a workflow state in the ZMI.
    An admin in this case is someone with role Manager or Site Administrator.
    Default: true.

Accepted True values are: ``true``, ``t``, ``1``, ``yes``, ``y``.

The defaults are intended to be reasonable for the latest official Plone versions, but the defaults may change.


Installation
------------

Install experimental.publishtraverse by adding it to your buildout::

    [buildout]
    ...
    eggs =
        experimental.publishtraverse

and then running ``bin/buildout``

No zcml is needed.


Compatibility
-------------

Fine on Plone 4.3, 5.0, 5.1.


Contribute
----------

- Issue Tracker: https://github.com/plone/experimental.publishtraverse/issues
- Source Code: https://github.com/plone/experimental.publishtraverse


License
-------

The project is licensed under the GPLv2.
