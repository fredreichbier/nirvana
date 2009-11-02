import re

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

