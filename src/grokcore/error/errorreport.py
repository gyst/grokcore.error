import logging
import zope.dottedname.resolve
import zope.error.interfaces
import grokcore.component as grok


# XXX this configuration needs to go somewhere. Where?
_info_level_exceptions = (
    'zope.security.interfaces.Unauthorized',
    )

_warning_level_exceptions = (
    'zope.publisher.interfaces.NotFound',
    )

_always_exc_info = False


class LoggingErrorReporting(grok.GlobalUtility):
    grok.implements(zope.error.interfaces.IErrorReportingUtility)
    grok.provides(zope.error.interfaces.IErrorReportingUtility)

    def __init__(
            self,
            info_level_exceptions=_info_level_exceptions,
            warning_level_exceptions=_warning_level_exceptions,
            always_exc_info=_always_exc_info):

        self.logger = logging.getLogger('grokcore.error')
        self.always_exc_info = always_exc_info

        self.info_level_exceptions = tuple(
            map(zope.dottedname.resolve.resolve, info_level_exceptions))

        self.warning_level_exceptions = tuple(
            map(zope.dottedname.resolve.resolve, warning_level_exceptions))

    def make_extra(self, request=None):
        return None

    def raising(self, exc_info, request=None):
        exc_class = exc_info[0]
        msg = '%s %s' % (exc_info[0].__name__, str(exc_info[1]))
        if request is not None:
            url = getattr(request, 'URL', None)
            if url is not None:
                msg += (' (URL: %s)' % url)

        level = self.logger.error

        if issubclass(exc_class, self.info_level_exceptions):
            level = self.logger.info
            exc_info = exc_info if self.always_exc_info else None

        elif issubclass(exc_class, self.warning_level_exceptions):
            level = self.logger.warning
            exc_info = exc_info if self.always_exc_info else None

        try:
            level(msg, exc_info=exc_info, extra=self.make_extra(request))
        finally:
            exc_info = None  # gc cleanup.
