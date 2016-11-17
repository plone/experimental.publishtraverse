Changelog
=========


1.1 (2016-11-17)
----------------

New features:

- Publish objects when their containers are only accessible for admins.
  You do that with ``security.declareObjectProtected(ManagePortal)``.
  This fixes setting permissions for a workflow state.
  You can turn this off by setting the new option
  ``EXPERIMENTAL_PUBLISH_TRAVERSE_ACCEPT_IF_ONLY_FOR_ADMINS``
  to false.
  [maurits]

Bug fixes:

- Added ``test`` extra and improved code quality of package,
  with help of plone.app.codeanalysis.
  [maurits]


1.0 (2016-09-28)
----------------

- Initial release.
  [maurits]
