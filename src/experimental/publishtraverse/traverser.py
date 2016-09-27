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
    from AccessControl.ZopeSecurityPolicy import getRoles
except ImportError:
    def getRoles(container, name, value, default):
        return getattr(value, '__roles__', default)

logger = logging.getLogger('experimental.publishtraverse')
_marker = object()
TRUE_VALUES = ('true', 't', '1', 'yes', 'y')

# Should we only warn, instead of fail?  Default: no.
ONLY_WARN = os.environ.get('EXPERIMENTAL_PUBLISH_TRAVERSE_ONLY_WARN', 'false')
if ONLY_WARN and ONLY_WARN.lower() in TRUE_VALUES:
    ONLY_WARN = True
    logger.info('Will only warn about possible problems.')
else:
    ONLY_WARN = False
    logger.info('Will forbid access in case of problems.')

# Known names that we can ignore.
KNOWN_NAMES = [
    'index_html',
]
# Should we accept known names?  Default: yes.
ACCEPT_KNOWN_NAMES = os.environ.get(
    'EXPERIMENTAL_PUBLISH_TRAVERSE_ACCEPT_KNOWN_NAMES', 'true')
if ACCEPT_KNOWN_NAMES and ACCEPT_KNOWN_NAMES.lower() in TRUE_VALUES:
    ACCEPT_KNOWN_NAMES = True
    logger.info('Will accept known names: %r.', KNOWN_NAMES)
else:
    ACCEPT_KNOWN_NAMES = False
    KNOWN_NAMES = []
    logger.info('Will not accept known names.')


def check_security(context, name, value, request):
    roles = getRoles(context, name, value, None)
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
