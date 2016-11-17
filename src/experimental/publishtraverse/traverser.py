# -*- coding: utf-8 -*-
import logging
import os
import types


try:
    from repoze.zope2.publishtraverse import DefaultPublishTraverse
except ImportError:
    from ZPublisher.BaseRequest import DefaultPublishTraverse

# This is from ZPublisher.BaseRequest:
try:
    from AccessControl.ZopeSecurityPolicy import getRoles  # noqa P001
except ImportError:
    def getRoles(container, name, value, default):
        return getattr(value, '__roles__', default)

logger = logging.getLogger('experimental.publishtraverse')
_marker = object()
TRUE_VALUES = ('true', 't', '1', 'yes', 'y')


def boolean_from_env(name, default):
    value = os.environ.get(name, _marker)
    if value is _marker:
        return default
    if not value:
        return default
    return value.lower() in TRUE_VALUES

# Should we only warn, instead of fail?  Default: no.
ONLY_WARN = boolean_from_env('EXPERIMENTAL_PUBLISH_TRAVERSE_ONLY_WARN', False)
if ONLY_WARN:
    logger.info('Will only warn about possible problems.')
else:
    logger.info('Will forbid access in case of problems.')

# Known names that we can ignore.
KNOWN_NAMES = [
    'index_html',
]
# Should we accept known names?  Default: yes.
ACCEPT_KNOWN_NAMES = boolean_from_env(
    'EXPERIMENTAL_PUBLISH_TRAVERSE_ACCEPT_KNOWN_NAMES', True)
if ACCEPT_KNOWN_NAMES:
    logger.info('Will accept known names: %r.', KNOWN_NAMES)
else:
    KNOWN_NAMES = []
    logger.info('Will not accept known names.')

# Should we allow publishing anyway if object is only accessible for some
# roles?  Default: yes.
ALLOWED_ROLES = set(['Manager', 'Site Administrator'])
ACCEPT_IF_ONLY_FOR_ADMINS = boolean_from_env(
    'EXPERIMENTAL_PUBLISH_TRAVERSE_ACCEPT_IF_ONLY_FOR_ADMINS', True)
if ACCEPT_IF_ONLY_FOR_ADMINS:
    logger.info('Will accept if object is only for these roles: %r.',
                ALLOWED_ROLES)
else:
    ALLOWED_ROLES = []
    logger.info('Will not accept even if only for admins.')


def allow_object(roles):
    # If only allowed roles are in the roles, we allow this object.
    if not roles or not ALLOWED_ROLES:
        return False
    try:
        extra_roles = set(roles).difference(ALLOWED_ROLES)
    except TypeError:
        return False
    if extra_roles:
        return False
    return True


def check_security(context, name, value, request):
    roles = getRoles(context, name, value, None)
    if ACCEPT_IF_ONLY_FOR_ADMINS and not roles:
        # It could be that the context itself is protected by a permission:
        # security.declareObjectProtected(ManagePortal)
        # Then it might be okay after all.
        # But this may open a can of worms, so we only want to allow this
        # if the context is only accessible for admins.
        # Note that we are not logged in yet in this part of the code,
        # so we cannot do permission checks ourselves.
        roles = getRoles(context, None, context, None)
        if allow_object(roles):
            logger.debug('Allowing admin-only access to %s', name)
        else:
            roles = None
    if not roles:
        # Note: I don't know if if matters if roles is None or an empty list or
        # an empty string.
        URL = request['URL']
        if not ONLY_WARN:
            logger.error('Refusing to publish object without roles at %s', URL)
            return request.response.forbiddenError(name)
        logger.warn('The object at %s has no roles.', URL)
    else:
        logger.debug('__roles__ for %s: %s', name, roles)
    return value


class StrictPublishTraverse(DefaultPublishTraverse):
    """Override the default browser publisher to be stricter.
    """

    def browserDefault(self, request):
        # This is only called when we are at the end of the path, which is
        # nice: when publishing x/y/z, we only want to check z, not the x and y
        # that are traversed to.  Note that if name is not found, we do not end
        # up here.
        # Get the original value.
        obj, default_path = super(
            StrictPublishTraverse, self).browserDefault(request)
        # Ignore some names for now, to avoid spamming the log for boring
        # stuff, which can crowd out the interesting stuff.  If there is a dot
        # in the name, we know it cannot be a function or method name, so we
        # ignore it.
        try:
            name = obj.__name__
        except AttributeError:
            # For example a BlobWrapper.
            name = ''
        if (name and name not in KNOWN_NAMES and '.' not in name):
            logger.debug(
                'Doing strict browserDefault check for name %r at url %s',
                name, request['ACTUAL_URL'])
            # We are only interested in methods and functions.
            if (isinstance(obj, types.MethodType) or
                    isinstance(obj, types.FunctionType)):
                parent = request.PARENTS[-2]
                # check_security might change the object to a forbidden
                # response.
                obj = check_security(parent, name, obj, request)

        return obj, default_path
