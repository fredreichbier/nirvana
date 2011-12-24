import sys
import re
import hashlib
from subprocess import PIPE, Popen

from django.conf import settings
from django.http import HttpResponse
from django.utils import simplejson
from django.core.mail import mail_admins
from django.utils.translation import ugettext as _
from django.db.models.fields import SlugField
from django.forms import RegexField

version_slug_re = re.compile(r'^[-\w.]+$')

class FormVersionSlugField(RegexField):
    default_error_messages = {
        'invalid': (u"Enter a valid 'slug' consisting of letters, numbers,"
                     u" underscores, hyphens and dots."),
    }
    def __init__(self, *args, **kwargs):
        super(FormVersionSlugField, self).__init__(version_slug_re, *args, **kwargs)

class DBVersionSlugField(SlugField):
    def formfield(self, **kwargs):
        defaults = {'form_class': FormVersionSlugField}
        defaults.update(kwargs)
        return super(DBVersionSlugField, self).formfield(**defaults)


def json_view(func):
    def wrap(request, *a, **kw):
        response = None
        try:
            response = dict(func(request, *a, **kw))
            if 'result' not in response:
                response['__result'] = 'ok'
        except KeyboardInterrupt:
            # Allow keyboard interrupts through for debugging.
            raise
        except Exception, e:
            # Mail the admins with the error
            exc_info = sys.exc_info()
            subject = 'JSON view error: %s' % request.path
            try:
                request_repr = repr(request)
            except:
                request_repr = 'Request repr() unavailable'
#            import traceback
#            message = 'Traceback:\n%s\n\nRequest:\n%s' % (
#                '\n'.join(traceback.format_exception(*exc_info)),
#                request_repr,
#                )
#            mail_admins(subject, message, fail_silently=True)

            # Come what may, we're returning JSON.
            if hasattr(e, 'message'):
                msg = e.message
            else:
                msg = _('Internal error')+': '+str(e)
            response = {'__result': 'error',
                        '__text': msg}

        json = simplejson.dumps(response)
        return HttpResponse(json, mimetype='text/plain') # TODO: i guess that should be application/json
    return wrap

def get_api_token(user):
    """
        Calculate the API token of *user*.
    """
    md5 = hashlib.md5()
    md5.update(user.username)
    md5.update(':')
    md5.update(user.password)
    return md5.hexdigest()


def sign(checksum):
    proc = Popen(
        ['/usr/bin/gpg2',
            '-q',
            '--batch',
            '-b',
            '-u', settings.GPG_KEY,
            '--passphrase', settings.GPG_PASSPHRASE,
            '--armor',
            '-'],
        stdin=PIPE, stdout=PIPE, stderr=PIPE)
    return proc.communicate(checksum)[0]

